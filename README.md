# CCC - Collective Context Commander (CC) ⛵

**🚀 Professionelles Multi-Agent Orchestrierungssystem für Claude Code Workflows**

>Die Stärke der Innovation ist wie ein Kunstwerk; sie wird lebendig, wenn visionäre Ideen und neuartige Werkzeuge zusammenfließen. An alle Entwickler dieser Welt: Lasst uns gemeinsam zu neuen Ufern aufbrechen. 🚀

## 🎯 Was ist CCC?

CCC ist ein leistungsstarkes CLI-System, das **Multi-Agent KI-Orchestrierung** ermöglicht - die Koordination mehrerer KI-Assistenten (Claude-1, Claude-2, Aider-1, Aider-2) in anspruchsvollen Workflows. Stell dir vor, du wärst der Dirigent eines KI-Orchesters.

## 🎼 Orchestra Pattern - Das Herzstück

### Konzept
Ein zentraler "Dirigent" koordiniert spezialisierte Agenten wie ein Orchester. Jeder Agent hat eine klare Rolle und arbeitet synchron mit den anderen zusammen.

### Hierarchie
```
    User/Product Owner
           |
    Claude-1 (Conductor)
      /          \
Aider-1        Aider-2
(Main Dev)    (Parallel Dev)
      \          /
    Claude-2 (Quality Gate)
           |
    Production Deploy
```

### Vorteile
- **Klare Hierarchie**: Jeder Agent weiß seine Rolle
- **Spezialisierung**: Agents fokussieren auf ihre Stärken
- **Parallelisierung**: Aider-1 und Aider-2 arbeiten parallel
- **Qualitätssicherung**: Claude-2 als finaler Review-Step
- **Skalierbarkeit**: Weitere Agents können hinzugefügt werden

## ✅ Getestete & Production-Ready Funktionen

Das CCC-System ist bereits **vollständig einsatzbereit** für folgende Kernfunktionen:

### 🔗 Multi-Agent Context System
- **Instanz-übergreifende Kommunikation** zwischen allen KI-Agenten
- **Broadcast-Nachrichten** an alle Instanzen gleichzeitig
- **Individuelle Nachrichten** an spezifische Agenten
- **Kontext-Sharing** zwischen Claude-1, Claude-2, Aider-1, Aider-2

### 📝 Session Management
- **Automatisches Session-Tracking** mit KI-Instanz Zuordnung
- **Session-Speicherung** mit Zeitstempel und Agent-Kennzeichnung
- **Session-Wiederherstellung** für nahtlose Workflow-Fortsetzung
- **Alias-Unterstützung** für schnelle Befehle

### 📚 Intelligentes Help-System
- **Umgebungserkennung** (Claude Code vs. Linux Console)
- **Drei Help-Modi**: compact, full, experimental
- **Automatische Formatierung** je nach Ausgabeumgebung
- **Markdown-Optimierung** für Claude Code Terminal

## 🎮 Verwendung der getesteten Funktionen

### Multi-Agent Kommunikation
```bash
# Eigenen Kontext lesen
ccc context

# Kontext von Claude-2 lesen
ccc co cl2

# Nachricht an Claude-2 senden
ccc context to cl2 -- "Beginne mit der Code-Implementierung"

# Broadcast an alle Agenten
ccc context to all -- "Sprint Planning abgeschlossen"
```

### Session Management
```bash
# Session für Claude-1 starten
ccc ses sta cl1

# Session für Claude-1 speichern
ccc ses sav cl1

# Session für Claude-1 beenden
ccc ses end cl1
```

### Help-System nutzen
```bash
# Kompakte Hilfe
ccc help

# Vollständige getestete Funktionen
ccc help full

# Experimentelle Funktionen (mit Warnungen)
ccc help experimental
```

## 🎮 Agent-Rollen im Detail

### KI-Instanzen & Spezialisierung
- **Claude-1 (cl1)**: System Architect & Conductor
  - Orchestriert den gesamten Entwicklungsprozess
  - Plant Architektur und koordiniert andere Agents

- **Aider-1 (ai1)**: Primary Code Implementation
  - Hauptentwicklung und Feature-Implementierung
  - Direkte Code-Generierung und -Modifikation

- **Aider-2 (ai2)**: Parallel Development & Testing
  - Parallele Entwicklung und Test-Erstellung
  - Code-Validierung und Alternative Implementierungen

- **Claude-2 (cl2)**: Quality Gate & Code Review
  - Finaler Review-Step vor Production
  - Qualitätssicherung und Best-Practice Enforcement

### Zielkürzel für Kommunikation
- `cl1` → Claude-1 (Conductor)
- `cl2` → Claude-2 (Quality Gate)
- `ai1` → Aider-1 (Main Dev)
- `ai2` → Aider-2 (Parallel Dev)
- `all` → Alle Instanzen (Broadcast)

## 🚀 Schnellstart

### Installation
```bash
# Repository klonen
git clone https://github.com/collective-context/ccc.git
cd ccc

# Ausführbar machen
chmod +x ccc

# Optional: Global installieren
sudo ln -sf "$(pwd)/ccc" /usr/local/bin/ccc
```

### Erste Schritte
```bash
# Hilfe anzeigen
./ccc help

# Multi-Agent Context System testen
./ccc context

# Session für Claude-1 starten
./ccc ses sta cl1
```

## 📁 Projekt-Struktur

```
ccc/
├── ccc                          # Haupt-CLI Script
├── lib/                         # Kern-Module
│   ├── ccc_manager.py           # Service Management
│   ├── ccc_commands.py          # Befehl-Implementierung
│   └── ccc_claude.py            # Inter-Agent Kommunikation
├── local-only/                  # KI-Instanz Kontextdateien
│   ├── Claude-1.md              # Claude-1 Kontext
│   ├── Claude-2.md              # Claude-2 Kontext
│   ├── Aider-1.md               # Aider-1 Kontext
│   ├── Aider-2.md               # Aider-2 Kontext
│   ├── full.md                  # Getestete Funktionen Hilfe
│   ├── experimental.md          # Experimentelle Funktionen
│   └── compact.md               # Kompakte Hilfe
├── config/                      # Konfigurationsdateien
├── tmp/                         # Temporäre Dateien
└── 0.HELLO-AI-START-HERE.md     # KI Einstiegspunkt
```

## 🔬 Experimentelle Funktionen

**⚠️ Warnung**: Folgende Funktionen sind im experimentellen Stadium und werden als **historisch unzuverlässig** eingestuft:

- Service Control (start, stop, restart)
- AutoInput Service
- Dialog Monitoring
- Status/Config Befehle

*Nutze `ccc help experimental` für Details.*

## 🛡️ Sicherheit & Qualität

- ✅ **Getestete Kernfunktionen** sind production-ready
- ✅ **Keine hardcodierten Credentials**
- ✅ **Sichere Subprocess-Behandlung**
- ✅ **Input-Validierung** durchgehend
- ✅ **Audit-bereite Codebasis**

## 📚 Weiterführende Informationen

- **Vollständige Dokumentation**: [collective-context.org](https://collective-context.org)
- **Orchestra Pattern Details**: [collective-context.org/patterns/orchestra/](https://collective-context.org/patterns/orchestra/)
- **CLI Referenz**: `ccc help full`

## 🤝 Beiträge

Wir freuen uns über Beiträge! Dieses Projekt ist Teil der [Collective Context](https://collective-context.org) Initiative.

## 📄 Lizenz

MIT License - siehe LICENSE Datei für Details.

## 🌟 Teil des Collective Context Ökosystems

CCC ist die **Grundlage** des **Collective Context** Ökosystems - revolutioniert wie Entwickler mit KI-Assistenten durch ausgeklügelte Multi-Agent Orchestrierung arbeiten.

**Bereit, deinen KI-Workflow zu orchestrieren?** ⚡

---

*Entwickelt mit ❤️ von der Collective Context Community*
