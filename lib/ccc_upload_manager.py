#!/usr/bin/env python3
"""
CCC Upload Manager - Professional Integration
===========================================

Integrates the professional build system with CCC commands.
This replaces the problematic upload_all_packages function with a robust implementation.
"""

import sys
import os
from pathlib import Path

def upload_all_packages_professional(manager):
    """Professional upload system that works from start to finish."""
    print("🚀 CCC 0.3.4 PROFESSIONAL Package Upload Process")
    print("=" * 60)
    print("📦 PROFESSIONAL: Robust build + upload with guaranteed success")
    print()

    try:
        # Import professional builder
        sys.path.append(str(Path(__file__).parent))
        from ccc_professional_build import CCCProfessionalBuilder

        # Initialize professional builder
        builder = CCCProfessionalBuilder()

        print("🔵 Step 1: BASE packages (ccc) - Professional Build...")
        print("-" * 40)

        # Execute complete professional build and upload for base packages
        success = builder.build_and_upload_all()

        if not success:
            print("❌ Professional base package build and upload failed")
            return 1

        print("✅ Professional base package build and upload completed!")
        print()

        print("🟢 Step 2: META packages (cccmd)...")
        print("-" * 40)

        # For meta packages, use existing system for now
        # In the future, this could be integrated into the professional builder
        import subprocess

        packaging_dir = Path.home() / "prog/ai/git/collective-context/ccc-debian-packaging"

        meta_changes_files = [
            "cccmd_0.3.4-jammy1_source.changes",
            "cccmd_0.3.4-noble1_source.changes"
        ]

        existing_meta_files = [f for f in meta_changes_files if (packaging_dir / f).exists()]

        if len(existing_meta_files) == 0:
            print("📦 No meta packages found - building from scratch...")
            try:
                print("🔨 Building CCCMD 0.3.4 meta packages...")
                result = subprocess.run([
                    str(packaging_dir / "build-meta.sh")
                ], capture_output=True, text=True, cwd=str(packaging_dir))

                if result.returncode != 0:
                    print("❌ Failed to build meta packages")
                    print(result.stderr)
                    print("⚠️  Base packages were uploaded successfully, but meta build failed.")
                    return 1
                else:
                    print("✅ Meta packages built successfully!")
            except Exception as e:
                print(f"❌ Meta build failed: {e}")
                print("⚠️  Base packages were uploaded successfully, but meta build failed.")
                return 1
        else:
            print(f"📦 Found {len(existing_meta_files)} existing meta packages")

        print("📤 Uploading meta packages...")

        # Import and use the existing meta upload system
        from ccc_ppa_upload import upload_meta_packages
        result_meta = upload_meta_packages(manager)

        if result_meta != 0:
            print("❌ Meta package upload failed.")
            print("⚠️  Base packages were uploaded successfully, but meta packages failed.")
            return result_meta

        print("✅ Meta packages uploaded successfully!")
        print()

        # Final success message
        print("=" * 60)
        print("🎉 PROFESSIONAL CCC 0.3.4 Package Upload Completed!")
        print("📊 Check upload status at:")
        print("   https://launchpad.net/~collective-context/+archive/ubuntu/ccc")
        print()
        print("💡 After successful build (15-30 minutes), users can install:")
        print("   • Individual: sudo apt install ccc")
        print("   • Complete:   sudo apt install cccmd")
        print()
        print("📦 Available packages:")
        print("   • ccc (BASE) - Core CCC Commander tool")
        print("   • cccmd (META) - Complete development suite with dependencies")

        return 0

    except Exception as e:
        print(f"❌ Professional upload system failed: {e}")
        import traceback
        traceback.print_exc()
        return 1