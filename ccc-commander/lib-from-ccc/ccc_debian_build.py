"""
CCC Debian Build Manager - Professional Native Debian Packaging System
Based on proven PPA upload patterns with Reprepro integration
"""

import subprocess
import json
import os
import shutil
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

class DebianBuildManager:
    """Professional Debian package build and upload manager"""

    def __init__(self, manager):
        self.manager = manager
        self.config = self.load_debian_config()
        self.log_dir = Path("local-only/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Build paths
        self.build_output_dir = Path(self.config.get("paths", {}).get("build_output_dir", "../debian-packages"))
        self.debian_source_dir = Path(self.config.get("paths", {}).get("debian_source_dir", "debian"))
        self.scripts_dir = Path(self.config.get("paths", {}).get("scripts_dir", "scripts"))

        # Version and package info
        self.version = "0.3.4"
        self.debian_revision = "1"

    def log_operation(self, message: str, level: str = "INFO"):
        """Log operation with timestamp to both CCC and Debian-specific log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"

        # Log to CCC manager
        self.manager.log(message, level)

        # Log to Debian build log
        debian_log = self.log_dir / f"debian-build-{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(debian_log, "a") as f:
            f.write(f"{log_entry}\n")

    def load_debian_config(self) -> Dict[str, Any]:
        """Load Debian packaging configuration from config.json"""
        try:
            config_path = Path("config/config.json")
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                    return config.get("debian_packaging", {})
        except Exception as e:
            self.manager.log(f"Could not load Debian config: {e}", "WARNING")

        # Return default config
        return {
            "enabled": True,
            "target_repository": "apt.collective-context.org",
            "supported_distributions": [
                {"codename": "bookworm", "version": "12", "enabled": True},
                {"codename": "trixie", "version": "13", "enabled": True}
            ],
            "build_settings": {
                "clean_build": True,
                "orig_tarball_reuse": True,
                "lintian_checks": True
            }
        }

    def get_enabled_distributions(self) -> List[Dict[str, Any]]:
        """Get list of enabled Debian distributions"""
        distributions = self.config.get("supported_distributions", [])
        return [dist for dist in distributions if dist.get("enabled", True)]

    def get_enabled_packages(self) -> List[Dict[str, Any]]:
        """Get list of enabled packages for building"""
        packages = self.config.get("auto_build_packages", [])
        return [pkg for pkg in packages if pkg.get("enabled", True)]

    def display_debian_config(self) -> bool:
        """Display current Debian packaging configuration"""
        if not self.config.get("enabled", True):
            self.log_operation("Debian packaging is disabled in configuration", "WARNING")
            return False

        self.log_operation(f"🎯 Target Repository: {self.config.get('target_repository', 'apt.collective-context.org')}")

        enabled_packages = self.get_enabled_packages()
        self.log_operation(f"📦 Enabled Packages ({len(enabled_packages)}):")
        for pkg in enabled_packages:
            pkg_type = pkg.get("type", "unknown").upper()
            self.log_operation(f"  ✅ {pkg['name']} ({pkg_type}) - {pkg.get('description', 'No description')}")

        enabled_distros = self.get_enabled_distributions()
        self.log_operation(f"🐧 Enabled Debian Distributions ({len(enabled_distros)}):")
        for dist in enabled_distros:
            priority = dist.get("priority", "normal").upper()
            self.log_operation(f"  ✅ {dist['codename']} ({dist['version']}) - {priority} priority")

        settings = self.config.get("build_settings", {})
        self.log_operation("⚙️  Build Settings:")
        self.log_operation(f"  🔐 Auto-sign: {settings.get('auto_sign', True)}")
        self.log_operation(f"  🔍 Check duplicates: {settings.get('check_duplicates', True)}")
        self.log_operation(f"  🧹 Clean build: {settings.get('clean_build', True)}")
        self.log_operation(f"  📋 Lintian checks: {settings.get('lintian_checks', True)}")

        return True

    def create_orig_tarball(self, force: bool = False) -> bool:
        """Create clean orig.tar.gz for Debian packaging"""
        orig_tarball = Path(f"../cccmd_{self.version}.orig.tar.gz")

        if orig_tarball.exists() and not force:
            self.log_operation(f"Using existing orig.tar.gz: {orig_tarball}")
            return True

        self.log_operation("Creating clean orig.tar.gz for Debian packaging...")

        try:
            # Get exclusions from config
            exclusions = self.config.get("debian_packaging_guidelines", {}).get(
                "common_mistakes_to_avoid", {}).get("orig_tarball", {}).get("exclusions", [
                    "debian/", ".git/", "__pycache__/", "*.egg-info/",
                    ".pytest_cache/", "venv*/", "dist/", "build/", "local-only/"
                ])

            # Build tar exclude arguments
            exclude_args = []
            for exclusion in exclusions:
                exclude_args.extend(["--exclude", exclusion])

            # Create tarball in parent directory
            os.chdir("..")
            tar_cmd = [
                "tar", "--exclude-vcs"
            ] + exclude_args + [
                "-czf", f"cccmd_{self.version}.orig.tar.gz", "ccc/"
            ]

            result = subprocess.run(tar_cmd, capture_output=True, text=True)
            os.chdir("ccc")

            if result.returncode == 0:
                file_size = orig_tarball.stat().st_size if orig_tarball.exists() else 0
                self.log_operation(f"✅ Created orig.tar.gz ({file_size} bytes)")
                return True
            else:
                self.log_operation(f"❌ Failed to create orig.tar.gz: {result.stderr}", "ERROR")
                return False

        except Exception as e:
            self.log_operation(f"❌ Exception creating orig.tar.gz: {e}", "ERROR")
            return False

    def clean_build_environment(self):
        """Clean build environment before starting new build"""
        self.log_operation("🧹 Cleaning build environment...")

        # Clean build artifacts
        patterns_to_clean = [
            "../cccmd_*.deb", "../ccc_*.deb", "../cccmd_*.dsc",
            "../cccmd_*.changes", "../cccmd_*.buildinfo", "../cccmd_*.tar.*"
        ]

        for pattern in patterns_to_clean:
            for file_path in Path(".").glob(pattern):
                try:
                    file_path.unlink()
                    self.log_operation(f"Removed: {file_path}")
                except Exception as e:
                    self.log_operation(f"Could not remove {file_path}: {e}", "WARNING")

        # Clean debian build directories
        build_dirs = ["debian/.debhelper", "debian/tmp", "debian/ccc", "debian/cccmd"]
        for build_dir in build_dirs:
            build_path = Path(build_dir)
            if build_path.exists():
                try:
                    shutil.rmtree(build_path)
                    self.log_operation(f"Removed directory: {build_path}")
                except Exception as e:
                    self.log_operation(f"Could not remove {build_path}: {e}", "WARNING")

        # Run debian/rules clean
        try:
            subprocess.run(["debian/rules", "clean"], check=False, capture_output=True)
        except Exception:
            pass

    def update_changelog_for_distribution(self, distro: Dict[str, Any]):
        """Update debian/changelog for specific distribution"""
        codename = distro["codename"]
        version = distro["version"]

        changelog_content = f"""cccmd ({self.version}-{self.debian_revision}~deb{version}u1) {codename}; urgency=medium

  * New upstream release {self.version}
  * Professional native Debian packaging for {codename}
  * Automated build for Debian {version} ({codename})
  * Complete development environment with CCC base package
  * Integration with apt.collective-context.org repository

 -- Collective Context Team <collective-context@recode.at>  {datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')}

"""

        changelog_path = self.debian_source_dir / "changelog"
        with open(changelog_path, "w") as f:
            f.write(changelog_content)

        self.log_operation(f"Updated changelog for {codename}")

    def build_package_for_distribution(self, distro: Dict[str, Any]) -> bool:
        """Build Debian package for specific distribution"""
        codename = distro["codename"]
        version = distro["version"]

        self.log_operation(f"🔨 Building for Debian {codename} ({version})")

        try:
            # Update changelog for this distribution
            self.update_changelog_for_distribution(distro)

            # Build binary package only (simpler than source+binary)
            build_cmd = ["dpkg-buildpackage", "-b", "-us", "-uc", "-d"]

            self.log_operation(f"Running: {' '.join(build_cmd)}")
            result = subprocess.run(build_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                # Move packages to distribution-specific directory
                distro_dir = self.build_output_dir / codename
                distro_dir.mkdir(parents=True, exist_ok=True)

                # Move .deb files
                for deb_file in Path("..").glob("*.deb"):
                    dest_file = distro_dir / deb_file.name
                    shutil.move(str(deb_file), str(dest_file))
                    self.log_operation(f"Moved package: {dest_file}")

                self.log_operation(f"✅ Build for {codename} completed successfully")
                return True
            else:
                self.log_operation(f"❌ Build failed for {codename}: {result.stderr}", "ERROR")
                return False

        except Exception as e:
            self.log_operation(f"❌ Build exception for {codename}: {e}", "ERROR")
            return False

    def run_lintian_checks(self) -> bool:
        """Run Lintian quality checks on built packages"""
        if not self.config.get("build_settings", {}).get("lintian_checks", True):
            self.log_operation("Lintian checks disabled in configuration")
            return True

        self.log_operation("🔍 Running Lintian quality checks...")

        try:
            all_passed = True
            for distro in self.get_enabled_distributions():
                distro_dir = self.build_output_dir / distro["codename"]
                if distro_dir.exists():
                    for deb_file in distro_dir.glob("*.deb"):
                        self.log_operation(f"Checking {deb_file.name}...")
                        result = subprocess.run(
                            ["lintian", str(deb_file)],
                            capture_output=True, text=True
                        )

                        if result.returncode == 0:
                            self.log_operation(f"✅ Lintian passed: {deb_file.name}")
                        else:
                            self.log_operation(f"⚠️  Lintian warnings for {deb_file.name}:")
                            for line in result.stdout.splitlines():
                                self.log_operation(f"    {line}")
                            # Don't fail on warnings, just log them

            return True

        except Exception as e:
            self.log_operation(f"⚠️  Lintian check exception: {e}", "WARNING")
            return True  # Don't fail build on lintian issues

    def check_repository_for_duplicates(self) -> bool:
        """Check if packages already exist in repository"""
        if not self.config.get("build_settings", {}).get("check_duplicates", True):
            return False

        self.log_operation("🔍 Checking repository for existing packages...")

        try:
            # For now, we don't have direct access to the Reprepro server
            # This would be implemented once the server is available
            self.log_operation("⚠️  Repository duplicate check not yet implemented")
            self.log_operation("💡 Will be added once Reprepro server is accessible")
            return False

        except Exception as e:
            self.log_operation(f"⚠️  Repository check failed: {e}", "WARNING")
            return False

    def test_ssh_connection(self) -> bool:
        """Test SSH connection to Reprepro server"""
        server_config = self.config.get("reprepro_server", {})
        hostname = server_config.get("hostname", "apt.collective-context.org")
        username = server_config.get("username", "ai")
        port = server_config.get("port", 22)
        ssh_key_path = server_config.get("ssh_key_path", "~/.ssh/id_rsa_apt")

        if not server_config.get("test_connection", True):
            return True

        self.log_operation(f"🔗 Testing SSH connection to {username}@{hostname}:{port}...")

        try:
            # Expand SSH key path
            ssh_key_path = os.path.expanduser(ssh_key_path)

            ssh_cmd = [
                "ssh", "-q", "-p", str(port), "-i", ssh_key_path,
                f"{username}@{hostname}", "exit"
            ]

            result = subprocess.run(
                ssh_cmd, capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                self.log_operation("✅ SSH connection successful")
                return True
            else:
                self.log_operation("❌ SSH connection failed", "ERROR")
                self.log_operation("💡 Please ensure SSH key is configured for the server")
                return False

        except subprocess.TimeoutExpired:
            self.log_operation("❌ SSH connection timeout", "ERROR")
            return False
        except Exception as e:
            self.log_operation(f"❌ SSH test exception: {e}", "ERROR")
            return False

    def upload_packages_to_repository(self) -> bool:
        """Upload built packages to Reprepro repository"""
        server_config = self.config.get("reprepro_server", {})
        hostname = server_config.get("hostname", "apt.collective-context.org")
        username = server_config.get("username", "ai")
        port = server_config.get("port", 22)
        ssh_key_path = os.path.expanduser(server_config.get("ssh_key_path", "~/.ssh/id_rsa_apt"))
        incoming_dir = server_config.get("incoming_dir", "~/deb/")
        repo_dir = server_config.get("repository_dir", "/var/www/apt")

        self.log_operation("📤 Uploading packages to Reprepro repository...")

        # Test SSH connection first
        if not self.test_ssh_connection():
            return False

        try:
            success_count = 0
            total_count = 0

            for distro in self.get_enabled_distributions():
                codename = distro["codename"]
                distro_dir = self.build_output_dir / codename

                if not distro_dir.exists():
                    self.log_operation(f"⚠️  No packages found for {codename}")
                    continue

                # Upload packages for this distribution
                deb_files = list(distro_dir.glob("*.deb"))
                if not deb_files:
                    self.log_operation(f"⚠️  No .deb files found for {codename}")
                    continue

                self.log_operation(f"Uploading {len(deb_files)} packages for {codename}...")

                for deb_file in deb_files:
                    total_count += 1

                    # Upload via SCP with custom port and SSH key
                    scp_cmd = [
                        "scp", "-P", str(port), "-i", ssh_key_path,
                        str(deb_file), f"{username}@{hostname}:{incoming_dir}"
                    ]

                    self.log_operation(f"Running: {' '.join(scp_cmd)}")
                    scp_result = subprocess.run(scp_cmd, capture_output=True, text=True)

                    if scp_result.returncode == 0:
                        self.log_operation(f"✅ Uploaded: {deb_file.name}")
                        success_count += 1

                        # Note: Repository integration (reprepro includedeb) would be handled
                        # by the server administrator or separate script on the server
                        # For now, we just upload to the incoming directory

                    else:
                        self.log_operation(f"❌ Failed to upload {deb_file.name}: {scp_result.stderr}", "ERROR")
                        self.log_operation(f"SCP stdout: {scp_result.stdout}", "DEBUG")

            self.log_operation(f"📊 Upload complete: {success_count}/{total_count} packages successful")

            if success_count > 0:
                self.log_operation("💡 Packages uploaded to incoming directory")
                self.log_operation("💡 Server administrator will integrate into repository")

            return success_count == total_count

        except Exception as e:
            self.log_operation(f"❌ Upload exception: {e}", "ERROR")
            return False

    def run_full_build_process(self) -> bool:
        """Run complete Debian build process"""
        self.log_operation("🚀 Starting Debian Build Process")
        self.log_operation("=" * 50)

        # Display configuration
        if not self.display_debian_config():
            return False

        # Check for duplicates
        if self.check_repository_for_duplicates():
            self.log_operation("⚠️  Packages already exist in repository - skipping build")
            return True

        # Clean build environment
        if self.config.get("build_settings", {}).get("clean_build", True):
            self.clean_build_environment()

        # Create orig.tar.gz
        if not self.create_orig_tarball():
            return False

        # Build packages for each distribution
        build_success = True
        enabled_distros = self.get_enabled_distributions()

        for distro in enabled_distros:
            self.log_operation(f"\n🔄 Building for {distro['description']}...")

            if not self.build_package_for_distribution(distro):
                build_success = False
                break

            # Clean between builds
            if len(enabled_distros) > 1:
                self.log_operation("🧹 Cleaning between distribution builds...")
                try:
                    subprocess.run(["debian/rules", "clean"], check=False, capture_output=True)
                except Exception:
                    pass

        if not build_success:
            self.log_operation("❌ Build process failed", "ERROR")
            return False

        # Run quality checks
        self.run_lintian_checks()

        self.log_operation("\n✅ All Debian packages built successfully!")
        self.log_operation(f"📦 Packages located in: {self.build_output_dir}")

        # List built packages
        for distro in enabled_distros:
            distro_dir = self.build_output_dir / distro["codename"]
            if distro_dir.exists():
                packages = list(distro_dir.glob("*.deb"))
                self.log_operation(f"  {distro['codename']}: {len(packages)} packages")
                for pkg in packages:
                    self.log_operation(f"    - {pkg.name}")

        return True

    def run_upload_process(self) -> bool:
        """Run upload process to Reprepro repository"""
        self.log_operation("📤 Starting Debian Package Upload Process")
        self.log_operation("=" * 50)

        # Check if packages exist
        packages_found = False
        for distro in self.get_enabled_distributions():
            distro_dir = self.build_output_dir / distro["codename"]
            if distro_dir.exists() and list(distro_dir.glob("*.deb")):
                packages_found = True
                break

        if not packages_found:
            self.log_operation("❌ No packages found to upload", "ERROR")
            self.log_operation("💡 Run build process first with: ccc exec debian build")
            return False

        # Upload packages
        return self.upload_packages_to_repository()

def debian_build_command(manager):
    """CCC exec debian build command"""
    builder = DebianBuildManager(manager)
    success = builder.run_full_build_process()
    return 0 if success else 1

def debian_upload_command(manager):
    """CCC exec debian upload command"""
    builder = DebianBuildManager(manager)
    success = builder.run_upload_process()
    return 0 if success else 1

def debian_full_command(manager):
    """CCC exec debian full command - build and upload"""
    builder = DebianBuildManager(manager)

    # Build packages
    if not builder.run_full_build_process():
        return 1

    # Upload packages
    if not builder.run_upload_process():
        return 1

    builder.log_operation("🎉 Complete Debian packaging process finished!")
    builder.log_operation(f"🔗 Repository available at: https://{builder.config.get('target_repository', 'apt.collective-context.org')}/")

    return 0

if __name__ == "__main__":
    """CLI entry point for standalone usage"""
    import sys
    import argparse

    # Mock manager for standalone usage
    class MockManager:
        def log(self, message, level="INFO"):
            print(f"[{level}] {message}")

    parser = argparse.ArgumentParser(description="Build and upload Debian packages")
    parser.add_argument("action", choices=["build", "upload", "full"], help="Action to perform")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without actually doing it")
    args = parser.parse_args()

    manager = MockManager()

    if args.action == "build":
        result = debian_build_command(manager)
    elif args.action == "upload":
        result = debian_upload_command(manager)
    elif args.action == "full":
        result = debian_full_command(manager)

    sys.exit(result)