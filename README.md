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
- **🆕 JSON Session Management** - TypeScript-basierte Session-Speicherung mit Metadaten
- **Alias-Unterstützung** für schnelle Befehle

### 📚 Intelligentes Help-System
- **Umgebungserkennung** (Claude Code vs. Linux Console)
- **Drei Help-Modi**: compact, full, experimental
- **Automatische Formatierung** je nach Ausgabeumgebung
- **Markdown-Optimierung** für Claude Code Terminal

### 🧪 Testing Infrastructure
- **Vitest-basiertes Testing** mit TypeScript-Unterstützung
- **7 Tests** für Core-Funktionalität (Session Management, Basic Operations)
- **Automatische CI/CD Integration** vorbereitet
- **Test Scripts** über npm verfügbar

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
# Klassisches Session Management
ccc ses sta cl1                      # Session für Claude-1 starten
ccc ses sav cl1                      # Session für Claude-1 speichern
ccc ses end cl1                      # Session für Claude-1 beenden

# 🆕 JSON Session Management (TypeScript-basiert)
ccc ses man save "project-alpha"     # JSON Session mit Metadaten speichern
ccc ses man list                     # Alle JSON Sessions auflisten
ccc ses man load "2025-09-15_project-alpha.json"  # JSON Session laden
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

### Testing & Development
```bash
# Tests ausführen
npm test                             # Alle Tests (7 Tests)
npm run test:run                     # CI-Mode Tests
npm run test:ui                      # UI Test Dashboard

# TypeScript Session Management entwickeln
npm run build                        # TypeScript kompilieren
npm run dev                          # Watch Mode für Entwicklung
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

# Dependencies installieren (für JSON Session Management & Testing)
npm install

# Ausführbar machen
chmod +x ccc

# TypeScript kompilieren (für Session Management Features)
npm run build

# Optional: Global installieren
sudo ln -sf "$(pwd)/ccc" /usr/local/bin/ccc
```

### Erste Schritte
```bash
# Hilfe anzeigen
./ccc help

# Tests ausführen (verifiziert Installation)
npm test

# Multi-Agent Context System testen
./ccc context

# Klassisches Session Management
./ccc ses sta cl1

# 🆕 JSON Session Management ausprobieren
./ccc ses man save "first-test"
./ccc ses man list
```

## 📁 Projekt-Struktur

```
ccc/
├── ccc                                      # Haupt-CLI Script (Python)
├── package.json                             # Node.js Dependencies & Scripts
├── tsconfig.json                            # TypeScript Configuration
├── vitest.config.ts                         # Testing Configuration
├── 0.HELLO-AI-START-HERE.md                 # KI Einstiegspunkt
│
├── lib/                                     # Python Kern-Module
│   ├── ccc_manager.py                       # Service Management
│   ├── ccc_commands.py                      # Befehl-Implementierung
│   └── ccc_claude.py                        # Inter-Agent Kommunikation
│
├── src/                                     # TypeScript Source Code
│   ├── session/
│   │   └── SimpleSessionManager.ts          # JSON Session Management
│   └── cli/
│       ├── index.ts                         # TypeScript CLI Entry
│       └── session-commands.ts              # Session CLI Commands
│
├── tests/                                   # Test Suite (7 Tests)
│   └── unit/
│       ├── basic.test.ts                    # Basic functionality tests
│       ├── helper.test.ts                   # Project structure tests
│       └── session/
│           └── SimpleSessionManager.test.ts # Session management tests
│
├── dist/                                    # Compiled TypeScript (auto-generated)
├── node_modules/                            # Node.js Dependencies (auto-generated)
│
├── local-only/                              # Private Development Files
│   ├── SESSION/                             # Session Files (organized)
│   │   ├── 2025-09-15_CL1_SESSION-SAVE.md  # Daily session saves
│   │   ├── 2025-09-15_CL1_SESSION-FULL.md  # Complete session exports
│   │   └── *.json                           # JSON session files
│   ├── HELP/                                # Help Documentation (organized)
│   │   ├── compact.md                       # Quick reference (ccc help)
│   │   ├── full.md                          # Complete docs (ccc help full)
│   │   └── experimental.md                  # Experimental features
│   ├── WORK/                                # Work assignments
│   │   └── 2025-09-15/                      # Daily work logs
│   ├── Claude-1.md                          # Claude-1 Context
│   ├── Claude-2.md                          # Claude-2 Context
│   ├── Aider-1.md                           # Aider-1 Context
│   └── Aider-2.md                           # Aider-2 Context
│
├── config/                                  # Configuration files
├── tmp/                                     # Temporary files
└── logs/                                    # Log files
```

## 🆕 Neueste Features (September 2025)

### ✨ JSON Session Management (TypeScript-basiert)
- **Strukturierte Session-Speicherung** mit Metadaten (Timestamp, Arbeitsverzeichnis, Platform)
- **CLI Integration** über `ccc session manage` Commands
- **TypeScript Implementation** für bessere Typsicherheit und Erweiterbarkeit

### 🧪 Testing Infrastructure
- **Vitest Testing Framework** mit 7 automatisierten Tests
- **TypeScript Test Support** für moderne Entwicklungspraktiken
- **CI/CD Ready** für kontinuierliche Integration

### 📁 Organisierte Verzeichnisstruktur
- **SESSION/**: Alle Session-Dateien zentral organisiert
- **HELP/**: Help-Dokumentation strukturiert abgelegt
- **WORK/**: Arbeitsaufträge und Logs systematisch archiviert

### 🛠️ Development Workflow
- **npm Scripts** für Testing, Building und Development
- **TypeScript Compilation** mit Source Maps und Declarations
- **Mixed Python/TypeScript Architecture** für beste Tool-Synergien

## 🔬 Experimentelle Funktionen

**⚠️ Warnung**: Folgende Funktionen sind im experimentellen Stadium und werden als **historisch unzuverlässig** eingestuft:

- Service Control (start, stop, restart)
- AutoInput Service
- Dialog Monitoring
- Status/Config Befehle

*Nutze `ccc help experimental` für Details.*

## 🔒 Security First (v0.2.0+)

Since v0.2.0, CCC uses JSON-based configuration with strict validation:

- ✅ **No code execution in configs**
- ✅ **Input validation for all commands**
- ✅ **Path traversal prevention**
- ✅ **Secure secret management**

### Configuration Migration

Old `.ts` configs are no longer supported. Migrate to JSON:

```json
// config-json/global/config.json
{
  "prompts": {
    "system": "You are a helpful assistant"
  },
  "settings": {
    "temperature": 0.7
  }
}
```

### Environment Variables

Never store secrets in code:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENROUTER_API_KEY="sk-or-..."
```

## 🧪 Testing

Run the test suite:

```bash
npm test                 # Run all tests
npm run test:run         # CI mode
npm run test:coverage    # Coverage report
npm run test:security    # Security tests only
```

Current coverage: ~60% (Target: 80%)

## 📚 API Documentation

Full API documentation is available in the source code via JSDoc comments.

Key modules:
- `SimpleSessionManager` - Session persistence
- `loadSafeConfig` - Secure config loading
- `safeExecute` - Shell command safety
- `validatePath` - Path traversal prevention

## 🛡️ Sicherheit & Qualität

- ✅ **Security Audit durchgeführt** (September 2025)
- ✅ **15+ automatisierte Tests** mit Vitest Framework
- ✅ **TypeScript Integration** für Typsicherheit
- ✅ **Keine hardcodierten Credentials**
- ✅ **Sichere Subprocess-Behandlung**
- ✅ **Input-Validierung** durchgehend
- ✅ **JSON-basierte sichere Konfiguration**
- ✅ **CI/CD Pipeline** mit GitHub Actions
- ✅ **Strukturierte Projektorganisation** (SESSION/, HELP/, WORK/)

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
