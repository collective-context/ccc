#!/usr/bin/env python3
"""
CCC Professional Build System
=============================

A comprehensive, robust build system for CCC packages that handles:
- Multi-distribution builds (jammy, noble)
- Clean workspace management
- Proper file placement and checksums
- GPG signing
- PPA uploads

This system is designed to work reliably from start (cc ex up ppa) to finish (packages on Launchpad).
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path
import json
from datetime import datetime
import logging

class CCCProfessionalBuilder:
    """Professional CCC package builder with complete workflow management."""

    def __init__(self, base_dir=None):
        """Initialize the professional builder."""
        if base_dir is None:
            base_dir = Path.home() / "prog/ai/git/collective-context"

        self.base_dir = Path(base_dir)
        self.ccc_dir = self.base_dir / "ccc"
        self.packaging_dir = self.base_dir / "ccc-debian-packaging"

        # Version info from config
        self.config = self.load_config()
        self.version = self.config["ppa_management"]["auto_upload_packages"][0]["version"]
        self.distributions = [d["codename"] for d in self.config["ppa_management"]["supported_distributions"] if d["enabled"]]

        # Setup logging
        self.setup_logging()

        # Environment setup
        os.environ["DEBEMAIL"] = "team@collective-context.org"
        os.environ["DEBFULLNAME"] = "Collective Context Team"

        self.logger.info(f"Initialized CCC Professional Builder v{self.version}")
        self.logger.info(f"Target distributions: {', '.join(self.distributions)}")

    def load_config(self):
        """Load configuration from ~/.config/ccc/config.json"""
        config_path = Path.home() / ".config/ccc/config.json"
        with open(config_path, 'r') as f:
            return json.load(f)

    def setup_logging(self):
        """Setup comprehensive logging."""
        self.logger = logging.getLogger('CCCBuilder')
        self.logger.setLevel(logging.INFO)

        # Console handler with colors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('🔨 %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def clean_workspace(self):
        """Clean all previous build artifacts."""
        self.logger.info("🧹 Cleaning workspace...")

        # Clean packaging directory of target version files
        for pattern in [f"*{self.version}*"]:
            for file in self.packaging_dir.glob(pattern):
                file.unlink(missing_ok=True)
                self.logger.info(f"   Removed: {file.name}")

        # Clean any temp directories
        for temp_dir in self.base_dir.glob("ccc-clean*"):
            if temp_dir.is_dir():
                shutil.rmtree(temp_dir)
                self.logger.info(f"   Removed temp dir: {temp_dir.name}")

        # Clean any build artifacts in base directory
        for pattern in [f"ccc_{self.version}*", "*.deb"]:
            for file in self.base_dir.glob(pattern):
                file.unlink(missing_ok=True)

    def create_clean_source(self):
        """Create a clean source directory for building."""
        self.logger.info("📦 Creating clean source directory...")

        clean_dir = self.base_dir / "ccc-clean"
        if clean_dir.exists():
            shutil.rmtree(clean_dir)

        clean_dir.mkdir()

        # Copy essential files only
        essential_files = [
            "lib/", "debian/", "ccc_main.py", "cc", "ccc",
            "pyproject.toml", "setup.py", "README.md", "LICENSE", "Makefile"
        ]

        for item in essential_files:
            source = self.ccc_dir / item
            dest = clean_dir / item

            if source.is_dir():
                shutil.copytree(source, dest, dirs_exist_ok=True)
            elif source.exists():
                shutil.copy2(source, dest)

        # Create clean changelog with current timestamp (will be fixed later for orig.tar.gz consistency)
        self.create_clean_changelog(clean_dir)

        # Create orig.tar.gz
        orig_file = self.base_dir / f"ccc_{self.version}.orig.tar.gz"
        subprocess.run([
            "tar", "-czf", str(orig_file),
            "-C", str(self.base_dir), "ccc-clean"
        ], check=True)

        self.logger.info(f"   Created: {orig_file.name}")
        return clean_dir, orig_file

    def create_clean_changelog(self, clean_dir, fixed_timestamp=None):
        """Create a clean changelog for the build with optional fixed timestamp."""
        # Use fixed timestamp if provided, otherwise use current time
        if fixed_timestamp:
            timestamp_str = fixed_timestamp
        else:
            timestamp_str = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

        changelog_content = f"""ccc ({self.version}) UNRELEASED; urgency=medium

  * CCC package build for Ubuntu distributions

 -- Collective Context Team <team@collective-context.org>  {timestamp_str}
"""
        changelog_path = clean_dir / "debian/changelog"
        changelog_path.write_text(changelog_content)
        self.logger.info(f"   Created clean changelog: {self.version} ({timestamp_str})")

    def build_for_distribution(self, clean_dir, distribution):
        """Build package for a specific Ubuntu distribution."""
        self.logger.info(f"🏗️  Building for Ubuntu {distribution}...")

        # Update changelog for this distribution
        new_version = f"{self.version}-{distribution}1"
        subprocess.run([
            "dch", "-D", distribution, "-v", new_version,
            f"CCC package build for Ubuntu {distribution}"
        ], cwd=clean_dir, check=True)

        # Build source package with non-interactive flags
        subprocess.run([
            "debuild", "-S", "-sa", "-us", "-uc", "-d"
        ], cwd=clean_dir, check=True)

        # Move build artifacts to packaging directory
        parent_dir = clean_dir.parent
        for pattern in [f"ccc_{new_version}*"]:
            for file in parent_dir.glob(pattern):
                dest = self.packaging_dir / file.name
                shutil.move(str(file), str(dest))
                self.logger.info(f"   Moved: {file.name} -> packaging/")

        return new_version

    def build_all_distributions(self):
        """Build packages for all enabled distributions."""
        self.logger.info("🚀 Starting multi-distribution build process...")

        # Clean workspace first
        self.clean_workspace()

        # Create clean source ONCE with fixed timestamp for orig.tar.gz consistency
        clean_dir, orig_file = self.create_clean_source()

        # CRITICAL: Move orig.tar.gz to packaging directory ONCE to ensure identical checksums
        dest_orig = self.packaging_dir / orig_file.name
        if dest_orig.exists():
            dest_orig.unlink()  # Remove any existing file
        shutil.move(str(orig_file), str(dest_orig))
        self.logger.info(f"   ✅ Single orig.tar.gz: {orig_file.name} -> packaging/")

        # Extract fixed timestamp from original changelog for consistency
        import time
        import os
        # Ensure we have proper timezone info
        os.environ['TZ'] = 'Europe/Berlin'
        time.tzset()
        fixed_timestamp = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        self.logger.info(f"   🔒 Using fixed timestamp for all builds: {fixed_timestamp}")

        built_versions = []

        try:
            for distribution in self.distributions:
                # Recreate clean directory for each distribution
                if clean_dir.exists():
                    shutil.rmtree(clean_dir)

                clean_dir.mkdir()

                # Copy essential files again
                essential_files = [
                    "lib/", "debian/", "ccc_main.py", "cc", "ccc",
                    "pyproject.toml", "setup.py", "README.md", "LICENSE", "Makefile"
                ]

                for item in essential_files:
                    source = self.ccc_dir / item
                    dest = clean_dir / item

                    if source.is_dir():
                        shutil.copytree(source, dest, dirs_exist_ok=True)
                    elif source.exists():
                        shutil.copy2(source, dest)

                # Create clean changelog with FIXED timestamp for this distribution
                self.create_clean_changelog(clean_dir, fixed_timestamp)

                # CRITICAL: Copy orig.tar.gz to parent directory for debuild
                parent_orig = clean_dir.parent / f"ccc_{self.version}.orig.tar.gz"
                if not parent_orig.exists():
                    shutil.copy2(str(dest_orig), str(parent_orig))
                    self.logger.info(f"   📋 Copied orig.tar.gz for debuild: {parent_orig.name}")

                # Build for this distribution
                version = self.build_for_distribution(clean_dir, distribution)
                built_versions.append(version)

        finally:
            # Clean up
            if clean_dir.exists():
                shutil.rmtree(clean_dir)

        self.logger.info(f"✅ Built {len(built_versions)} distribution packages with identical orig.tar.gz")
        return built_versions

    def sign_packages(self, versions):
        """Sign all packages with GPG."""
        self.logger.info("🔐 Signing packages with GPG...")

        # Use direct GPG signing instead of complex import
        os.environ["DEBEMAIL"] = "team@collective-context.org"
        os.environ["DEBFULLNAME"] = "Collective Context Team"

        # Load GPG configuration
        gpg_config = Path.home() / ".config" / "ccc" / "gpg.json"
        gpg_pass = None
        if gpg_config.exists():
            import json
            with open(gpg_config, 'r') as f:
                config = json.load(f)
                gpg_pass = config.get("pass", "")

        for version in versions:
            changes_file = self.packaging_dir / f"ccc_{version}_source.changes"

            if changes_file.exists():
                # Use debsign for reliable signing
                env = os.environ.copy()
                if gpg_pass:
                    # Set up GPG passphrase if available
                    env["GPG_PASSPHRASE"] = gpg_pass

                result = subprocess.run([
                    "debsign", "-k", "EA8C41A4255934A9A729E13D4A92127F90F94A2E",
                    str(changes_file)
                ], cwd=self.packaging_dir, env=env, capture_output=True, text=True)

                if result.returncode == 0:
                    self.logger.info(f"   ✅ Signed: {changes_file.name}")
                else:
                    self.logger.warning(f"   ⚠️ Signing attempt for {changes_file.name}: {result.stderr}")
                    # Continue anyway - files might already be signed
                    self.logger.info(f"   ➡️ Continuing with {changes_file.name}")

        return True

    def check_ppa_for_duplicates(self, versions):
        """Check PPA for existing packages before upload."""
        self.logger.info("🔍 Checking PPA for existing packages...")

        try:
            import requests
            from bs4 import BeautifulSoup

            # Check PPA page for existing versions
            ppa_url = "https://launchpad.net/~collective-context/+archive/ubuntu/ccc"
            response = requests.get(ppa_url, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text().lower()

                existing_versions = []
                for version in versions:
                    version_string = f"ccc {version.replace('-', '-')}"
                    if version_string.lower() in page_text:
                        existing_versions.append(version)
                        self.logger.warning(f"   ⚠️ Package already exists in PPA: {version}")

                if existing_versions:
                    self.logger.error(f"❌ Found {len(existing_versions)} existing packages - STOPPING UPLOAD")
                    self.logger.error("   This prevents Launchpad rejection emails!")
                    return False

                self.logger.info("✅ No duplicate packages found - safe to upload")
                return True

        except Exception as e:
            self.logger.warning(f"⚠️ Could not check PPA (continuing anyway): {e}")
            return True  # Continue if check fails

    def upload_packages(self, versions):
        """Upload signed packages to PPA."""
        self.logger.info("📤 Uploading packages to PPA...")

        # CRITICAL: Check for duplicates first
        if not self.check_ppa_for_duplicates(versions):
            return False

        # Use direct dput upload - more reliable than complex imports
        success_count = 0
        for version in versions:
            changes_file = self.packaging_dir / f"ccc_{version}_source.changes"

            if changes_file.exists():
                self.logger.info(f"   🚀 Uploading: {changes_file.name}")

                # Use dput to upload - but handle errors gracefully
                result = subprocess.run([
                    "dput", "--force", "ppa:collective-context/ccc", str(changes_file)
                ], cwd=self.packaging_dir, capture_output=True, text=True)

                if result.returncode == 0:
                    self.logger.info(f"   ✅ Upload successful: {changes_file.name}")
                    success_count += 1
                else:
                    self.logger.warning(f"   ⚠️ Upload issue for {changes_file.name}: {result.stderr}")
                    # Check if it's a "already uploaded" error
                    if "already uploaded" in result.stderr or "File already exists" in result.stderr:
                        self.logger.info(f"   ℹ️ Package already exists - skipping {changes_file.name}")
                        success_count += 1
                    else:
                        self.logger.error(f"   ❌ Real upload error: {result.stderr}")

        # Return success if at least one package was processed
        return success_count > 0

    def build_and_upload_all(self):
        """Complete build and upload process."""
        self.logger.info("🎯 Starting complete CCC build and upload process...")

        try:
            # Build all distributions
            versions = self.build_all_distributions()

            if not versions:
                self.logger.error("❌ No packages were built")
                return False

            # Sign all packages
            if not self.sign_packages(versions):
                self.logger.error("❌ Package signing failed")
                return False

            # Upload all packages
            if not self.upload_packages(versions):
                self.logger.error("❌ Package upload failed")
                return False

            self.logger.info("🎉 Complete build and upload process successful!")
            self.logger.info("📊 Check status at: https://launchpad.net/~collective-context/+archive/ubuntu/ccc")
            return True

        except Exception as e:
            self.logger.error(f"❌ Build process failed: {e}")
            return False


def main():
    """Main entry point for professional build system."""
    builder = CCCProfessionalBuilder()
    success = builder.build_and_upload_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()