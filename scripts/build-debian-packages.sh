#!/bin/bash
set -e

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔨 Building Debian packages for CCC 0.3.4${NC}"

# Versions-Info
VERSION="0.3.4"
DEBIAN_REVISION="1"

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf ../cccmd_*.deb ../cccmd_*.dsc ../cccmd_*.changes ../cccmd_*.buildinfo ../cccmd_*.tar.*
rm -rf debian/.debhelper debian/tmp debian/ccc debian/cccmd
debian/rules clean || true

# Erstelle sauberes orig.tar.gz wenn nicht vorhanden
if [ ! -f "../cccmd_${VERSION}.orig.tar.gz" ]; then
    echo -e "${YELLOW}Creating clean orig.tar.gz...${NC}"
    cd ..
    tar --exclude-vcs \
        --exclude="ccc/debian" \
        --exclude="ccc/.pytest_cache" \
        --exclude="ccc/htmlcov" \
        --exclude="ccc/venv*" \
        --exclude="ccc/dist" \
        --exclude="ccc/__pycache__" \
        --exclude="ccc/*.egg-info" \
        --exclude="ccc/local-only" \
        --exclude="ccc/.pybuild" \
        --exclude="ccc/.claude" \
        --exclude="ccc/logs" \
        --exclude="ccc/tmp" \
        -czf cccmd_${VERSION}.orig.tar.gz ccc/
    cd ccc
    echo -e "${GREEN}Created orig.tar.gz ($(ls -lh ../cccmd_${VERSION}.orig.tar.gz | awk '{print $5}'))${NC}"
fi

# Funktion für einzelnen Build
build_for_distro() {
    local DISTRO=$1
    local DISTRO_VERSION=$2

    echo -e "${GREEN}Building for Debian ${DISTRO} (${DISTRO_VERSION})${NC}"

    # Changelog für spezifische Distribution erstellen
    cat > debian/changelog <<EOF
cccmd (${VERSION}-${DEBIAN_REVISION}~deb${DISTRO_VERSION}u1) ${DISTRO}; urgency=medium

  * New upstream release ${VERSION}
  * Professional PPA Upload System with 100% reliability
  * Flexible command abbreviations (minimum 2 characters)
  * Enhanced multi-agent context system
  * JSON session management with metadata
  * Automated build for Debian ${DISTRO_VERSION} (${DISTRO})

 -- Collective Context Team <collective-context@recode.at>  $(date -R)
EOF

    # Nur Binary-Paket bauen (einfacher als Source + Binary)
    echo -e "${YELLOW}Building binary package for ${DISTRO}...${NC}"
    dpkg-buildpackage -b -us -uc -d

    # Pakete in distro-spezifisches Verzeichnis verschieben
    mkdir -p ../debian-packages/${DISTRO}
    mv ../cccmd*.deb ../debian-packages/${DISTRO}/ 2>/dev/null || true
    mv ../ccc*.deb ../debian-packages/${DISTRO}/ 2>/dev/null || true

    echo -e "${GREEN}✅ Build für ${DISTRO} abgeschlossen!${NC}"
    echo -e "   Pakete: $(ls ../debian-packages/${DISTRO}/*.deb 2>/dev/null | wc -l)"
}

# Debian 12 (Bookworm) Build
build_for_distro "bookworm" "12"

# Clean zwischen Builds
echo -e "${YELLOW}Cleaning between builds...${NC}"
debian/rules clean || true

# Debian 13 (Trixie) Build
build_for_distro "trixie" "13"

# Lintian Tests
echo -e "${YELLOW}Running Lintian checks...${NC}"
for distro in bookworm trixie; do
    if [ -d "../debian-packages/${distro}" ]; then
        echo -e "Checking ${distro} packages:"
        lintian ../debian-packages/${distro}/*.deb || true
    fi
done

echo -e "${GREEN}✅ Alle Debian-Pakete erfolgreich erstellt!${NC}"
echo -e "${YELLOW}Pakete befinden sich in: ../debian-packages/${NC}"
if [ -d "../debian-packages" ]; then
    ls -la ../debian-packages/*/
fi