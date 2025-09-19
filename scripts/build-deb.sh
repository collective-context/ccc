#!/bin/bash
set -e

echo "🔨 Building Debian packages for CCC..."

# Environment variables for dch
export DEBEMAIL="team@collective-context.org"
export DEBFULLNAME="Collective Context Team"

# Versionsinfo
VERSION="0.3.4"

# Clean previous builds
rm -rf debian/tmp debian/*.debhelper* debian/*.substvars
rm -f ../*.deb ../*.dsc ../*.changes ../*.buildinfo ../*.tar.xz
rm -f ../ccc_*.orig.tar.gz ../cccmd_*.orig.tar.gz  # Remove old orig files

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

echo "📦 Creating minimal clean source for CCC package..."
# Create a minimal clean copy with only essential files
cd ..
rm -rf ccc-clean
mkdir -p ccc-clean

# Copy only essential files for CCC package
cp -r ccc/lib ccc-clean/
cp -r ccc/debian ccc-clean/
cp ccc/ccc_main.py ccc-clean/
cp ccc/cc ccc-clean/
cp ccc/ccc ccc-clean/
cp ccc/pyproject.toml ccc-clean/
cp ccc/setup.py ccc-clean/
cp ccc/README.md ccc-clean/
cp ccc/LICENSE ccc-clean/
cp ccc/Makefile ccc-clean/

# Reset changelog to clean base version
echo "ccc (${VERSION}) UNRELEASED; urgency=medium

  * CCC package build for Ubuntu distributions

 -- Collective Context Team <team@collective-context.org>  $(date -R)
" > ccc-clean/debian/changelog

# Create minimal orig.tar.gz from clean copy
tar -czf ccc_${VERSION}.orig.tar.gz ccc-clean/

# Copy orig.tar.gz to packaging directory but keep local copy for builds
cp ccc_${VERSION}.orig.tar.gz ccc-debian-packaging/

# Function to build CCC package for specific Ubuntu version
build_ccc_for_ubuntu() {
    local ubuntu_codename=$1
    local version_suffix=$2

    echo "📦 Building CCC package for Ubuntu $ubuntu_codename..."

    # Update changelog for this Ubuntu version
    local new_version="${VERSION}-${ubuntu_codename}${version_suffix}"

    # Create new changelog entry in the clean directory
    (cd ccc-clean && dch -D "$ubuntu_codename" -v "$new_version" "CCC package build for Ubuntu $ubuntu_codename")

    echo "📦 Building source package for PPA..."
    # Build source package for PPA (unsigned - we'll sign later with our GPG system)
    (cd ccc-clean && debuild -S -sa -us -uc)

    echo "📦 Moving built files to packaging directory..."
    # Move built files to packaging directory for upload (we're already in parent directory)
    mv ccc-clean/*.dsc ccc-debian-packaging/ 2>/dev/null || true
    mv ccc-clean/*.changes ccc-debian-packaging/ 2>/dev/null || true
    mv ccc-clean/*.buildinfo ccc-debian-packaging/ 2>/dev/null || true
    mv ccc-clean/*.tar.xz ccc-debian-packaging/ 2>/dev/null || true

    echo "✅ CCC package built for $ubuntu_codename"
}

echo "📦 Building for multiple Ubuntu versions..."

# Ubuntu 22.04 (Jammy)
build_ccc_for_ubuntu "jammy" "1"

# Reset changelog and rebuild clean directory for next version
echo "📦 Recreating clean build directory for next version..."
rm -rf ccc-clean
mkdir -p ccc-clean

# Copy only essential files for CCC package
cp -r ccc/lib ccc-clean/
cp -r ccc/debian ccc-clean/
cp ccc/ccc_main.py ccc-clean/
cp ccc/cc ccc-clean/
cp ccc/ccc ccc-clean/
cp ccc/pyproject.toml ccc-clean/
cp ccc/setup.py ccc-clean/
cp ccc/README.md ccc-clean/
cp ccc/LICENSE ccc-clean/
cp ccc/Makefile ccc-clean/

# Reset changelog to clean base version again
echo "ccc (${VERSION}) UNRELEASED; urgency=medium

  * CCC package build for Ubuntu distributions

 -- Collective Context Team <team@collective-context.org>  $(date -R)
" > ccc-clean/debian/changelog

# Ubuntu 24.04 (Noble)
build_ccc_for_ubuntu "noble" "1"

echo "📦 Cleaning up build directory..."
rm -rf ccc-clean

echo "📦 Building binary package for local testing..."
# Build binary package for local testing (unsigned) - use original ccc directory
cd ccc
debuild -us -uc -b
cd ..

echo "✅ Build complete for both Ubuntu versions!"
echo ""
echo "📋 Files created in packaging directory:"
ls -la ccc-debian-packaging/ccc_0.3.4-*.changes ccc-debian-packaging/ccc_0.3.4-*.dsc 2>/dev/null || echo "No 0.3.4 files found in packaging directory"
ls -la *.deb 2>/dev/null || echo "No .deb files found in current directory"

echo ""
echo "🔍 Running lintian check..."
for changes_file in ccc-debian-packaging/ccc_0.3.4-*.changes; do
    if [ -f "$changes_file" ]; then
        echo "Checking $changes_file..."
        lintian --info "$changes_file" || echo "Lintian check completed with warnings for $changes_file"
    fi
done

echo ""
echo "🚀 Ready for PPA upload!"
echo "   Both jammy and noble versions built"
echo "   Use: cc ex up ppa"