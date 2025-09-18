#!/bin/bash
set -e

echo "🔨 Building Debian packages for CCC..."

# Versionsinfo
VERSION="0.3.2"
DISTRIBUTION="jammy"  # Ubuntu 22.04 LTS

# Clean previous builds
rm -rf debian/tmp debian/*.debhelper* debian/*.substvars
rm -f ../*.deb ../*.dsc ../*.changes ../*.buildinfo ../*.tar.xz

# Check if we have the required tools
for cmd in debuild dch lintian; do
    if ! command -v $cmd &> /dev/null; then
        echo "❌ $cmd not found. Please install with:"
        echo "   sudo apt install devscripts build-essential"
        exit 1
    fi
done

# Check GPG key
if ! gpg --list-secret-keys team@collective-context.org &> /dev/null; then
    echo "❌ GPG key for team@collective-context.org not found"
    echo "   Configure GPG key first"
    exit 1
fi

echo "📦 Building source package for PPA..."
# Build source package for PPA (signed)
debuild -S -sa -k"team@collective-context.org"

echo "📦 Building binary package for local testing..."
# Build binary package for local testing (unsigned)
debuild -us -uc -b

echo "✅ Build complete!"
echo ""
echo "📋 Files created:"
ls -la ../*.changes ../*.dsc ../*.deb 2>/dev/null || echo "No files found in parent directory"

echo ""
echo "🔍 Running lintian check..."
lintian --info ../*.changes || echo "Lintian check completed with warnings"

echo ""
echo "🚀 Ready for PPA upload!"
echo "   Use: python3 lib/ccc_ppa_upload.py --dry-run"