#!/usr/bin/env python3
"""
CCC Single Distribution Builder
==============================

Builds a single distribution cleanly to avoid checksum conflicts.
Used to build jammy after noble was successfully uploaded.
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

class CCCSingleBuilder:
    """Single distribution builder for targeted fixes."""

    def __init__(self, distribution="jammy"):
        """Initialize builder for specific distribution."""
        self.base_dir = Path.home() / "prog/ai/git/collective-context"
        self.ccc_dir = self.base_dir / "ccc"
        self.packaging_dir = self.base_dir / "ccc-debian-packaging"

        # Version info
        self.version = "0.3.4"
        self.distribution = distribution

        # Environment setup
        os.environ["DEBEMAIL"] = "team@collective-context.org"
        os.environ["DEBFULLNAME"] = "Collective Context Team"

        print(f"🎯 Single Builder for Ubuntu {distribution}")

    def clean_distribution_files(self):
        """Clean only this distribution's files."""
        print(f"🧹 Cleaning {self.distribution} files...")

        # Clean packaging directory of this distribution only
        for pattern in [f"*{self.version}-{self.distribution}*"]:
            for file in self.packaging_dir.glob(pattern):
                file.unlink(missing_ok=True)
                print(f"   Removed: {file.name}")

    def build_single_distribution(self):
        """Build package for single distribution."""
        print(f"🏗️  Building clean {self.distribution} package...")

        # Create completely fresh clean directory
        clean_dir = self.base_dir / "ccc-single-clean"
        if clean_dir.exists():
            shutil.rmtree(clean_dir)

        clean_dir.mkdir()

        # Copy essential files
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

        # Create clean changelog
        changelog_content = f"""ccc ({self.version}) UNRELEASED; urgency=medium

  * CCC package build for Ubuntu {self.distribution}

 -- Collective Context Team <team@collective-context.org>  {datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')}
"""
        changelog_path = clean_dir / "debian/changelog"
        changelog_path.write_text(changelog_content)

        # Create orig.tar.gz in parent directory for debuild
        orig_file = self.base_dir / f"ccc_{self.version}.orig.tar.gz"
        print(f"   Creating orig.tar.gz...")
        subprocess.run([
            "tar", "-czf", str(orig_file),
            "-C", str(self.base_dir), "ccc-single-clean"
        ], check=True)

        # Also copy to packaging directory for later use
        packaging_orig = self.packaging_dir / f"ccc_{self.version}.orig.tar.gz"
        if not packaging_orig.exists():
            shutil.copy2(str(orig_file), str(packaging_orig))

        # Update changelog for this distribution
        new_version = f"{self.version}-{self.distribution}1"
        subprocess.run([
            "dch", "-D", self.distribution, "-v", new_version,
            f"CCC package build for Ubuntu {self.distribution}"
        ], cwd=clean_dir, check=True)

        # Build source package
        subprocess.run([
            "debuild", "-S", "-sa", "-us", "-uc"
        ], cwd=clean_dir, check=True)

        # Move build artifacts to packaging directory
        parent_dir = clean_dir.parent
        for pattern in [f"ccc_{new_version}*"]:
            for file in parent_dir.glob(pattern):
                dest = self.packaging_dir / file.name
                shutil.move(str(file), str(dest))
                print(f"   Moved: {file.name} -> packaging/")

        # Clean up
        shutil.rmtree(clean_dir)

        print(f"✅ Built {self.distribution} package: {new_version}")
        return new_version

    def sign_and_upload(self, version):
        """Sign and upload the package."""
        print(f"🔐 Signing and uploading {version}...")

        changes_file = self.packaging_dir / f"ccc_{version}_source.changes"

        if not changes_file.exists():
            print(f"❌ Changes file not found: {changes_file}")
            return False

        # Sign using existing GPG system
        sys.path.append(str(self.ccc_dir / "lib"))
        try:
            from ccc_ppa_upload import CCCPPAManager

            # Create mock manager
            class MockManager:
                def log(self, message, level="INFO"):
                    print(f"[{level}] {message}")

            manager = CCCPPAManager(MockManager())

            # Sign the package
            success = manager.sign_package_with_ultimate_gpg(str(changes_file))
            if not success:
                print(f"❌ Signing failed for {changes_file.name}")
                return False

            print(f"✅ Signed: {changes_file.name}")

            # Upload using dput
            result = subprocess.run([
                "dput", "--force", "ppa:collective-context/ccc", str(changes_file)
            ], cwd=self.packaging_dir, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ Upload successful: {changes_file.name}")
                return True
            else:
                print(f"❌ Upload failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error during sign/upload: {e}")
            return False

def main():
    """Main entry point."""
    distribution = sys.argv[1] if len(sys.argv) > 1 else "jammy"

    builder = CCCSingleBuilder(distribution)

    # Clean old files
    builder.clean_distribution_files()

    # Build package
    version = builder.build_single_distribution()

    # Sign and upload
    success = builder.sign_and_upload(version)

    if success:
        print(f"🎉 {distribution} package successfully uploaded!")
        return 0
    else:
        print(f"❌ {distribution} package upload failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())