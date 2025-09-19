#!/bin/bash
set -e

# Konfiguration
REPO_SERVER="apt.collective-context.org"
REPO_USER="root"  # Oder spezifischer Upload-User
INCOMING_DIR="/var/www/apt/incoming"

echo "📤 Uploading Debian packages to Reprepro server..."

# SSH-Key Check
if ! ssh -q ${REPO_USER}@${REPO_SERVER} exit; then
    echo "❌ SSH-Verbindung fehlgeschlagen. Bitte SSH-Key einrichten!"
    exit 1
fi

# Pakete hochladen
for distro in bookworm trixie; do
    echo "Uploading packages for ${distro}..."

    if [ -d "../debian-packages/${distro}" ]; then
        # Upload via SCP
        scp ../debian-packages/${distro}/*.deb ${REPO_USER}@${REPO_SERVER}:${INCOMING_DIR}/

        # Pakete zum Repository hinzufügen
        ssh ${REPO_USER}@${REPO_SERVER} "
            cd /var/www/apt
            for deb in ${INCOMING_DIR}/*.deb; do
                if [[ \$(basename \$deb) == *trixie* ]]; then
                    reprepro includedeb trixie \$deb && rm \$deb
                else
                    reprepro includedeb bookworm \$deb && rm \$deb
                fi
            done
        "
    fi
done

echo "✅ Upload abgeschlossen!"
echo "🔍 Verifiziere auf: https://apt.collective-context.org/"