

# CAPA v3-R - "Der Denker"

## Übersicht

**CAPA v3-R ("Der Denker")** ist ein Prototyp einer künstlichen Intelligenz-Architektur, der auf den Prinzipien der **kognitiven Hierarchie**, **modularen Spezialisierung** und des **autonomen Lernens** basiert.

Im Gegensatz zu monolithischen Modellen imitiert diese Architektur die Gewaltenteilung des menschlichen Gehirns. Sie nutzt ein Team von spezialisierten, kooperierenden KI-Modulen, die in einer hierarchischen Struktur angeordnet sind. Das System ist als proaktiver, lernender Agent konzipiert, der in der Lage ist, zu denken, zu fühlen (simuliert), Pläne zu erstellen und aus Feedback zu lernen, um sich selbst zu verbessern.

Das Herzstück ist ein hybrides C++/Python-System, das einen hochperformanten C++-Kern für das Kurzzeitgedächtnis mit einer intelligenten, in Python implementierten Steuerungs- und Langzeitgedächtnis-Architektur kombiniert.

## Features

*   **Hierarchisches Denken:** Drei kognitive Layer mit dedizierten LLMs (`Layer 3: Reflex`, `Layer 4: Planer`, `Layer 5: Executor`) für Aufgaben unterschiedlicher Komplexität.
*   **Dynamische Kognition:** Eine `Agent`-Klasse orchestriert einen dynamischen Denkprozess, bei dem Aufgaben basierend auf Konfidenz zwischen den Layern eskaliert werden.
*   **Vorausschauende Absicht:** Fähigkeit zur Erstellung, Speicherung und Verfolgung von Langzeitplänen.
*   **Emotionales System:**
    *   **Layer 1:** Ein intelligenter Vorfilter, der den emotionalen Kontext einer Anfrage erfasst.
    *   **AffectiveEngine:** Ein internes Emotionssystem, das den Zustand des Agenten basierend auf Erfolg (intrinsischer Reward) und Misserfolg (intrinsisches Punishment) sowie externem Feedback anpasst.
*   **Persistentes Gedächtnis:** Ein Langzeitgedächtnis (LTM) auf Basis von `ChromaDB`, in dem "gelernte Lektionen" und Pläne dauerhaft gespeichert werden.
*   **Autonomer Lernzyklus:** Ein `manage_stm`-Zyklus, der einem Schlafzyklus nachempfunden ist. Hierbei werden die Erfahrungen des "Tages" (aus dem STM) zu "gelernten Lektionen" und einer "Lektion des Tages" synthetisiert und im LTM archiviert.

## Installation

### Voraussetzungen

*   Python (3.10+)
*   Ein C++ Compiler-Toolchain (z.B. Visual Studio mit "Desktopentwicklung mit C++" unter Windows)
*   CMake (Version 3.15+)
*   Git
*   [Ollama](https://ollama.com/) (muss installiert sein und im Hintergrund laufen)

### Setup-Schritte

1.  **Repository klonen:**
    ```bash
    git clone <repository_url>
    cd capa_v3_r
    ```

2.  **Git Submodule initialisieren:**
    (Wird für `pybind11` benötigt)
    ```bash
    git submodule update --init --recursive
    ```

3.  **Python-Umgebung einrichten:**
    ```bash
    python -m venv .venv
    # Windows
    .\.venv\Scripts\activate
    # macOS/Linux
    # source .venv/bin/activate
    ```

4.  **Python-Abhängigkeiten installieren:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **C++ Kern-Modul kompilieren:**
    Führe das Build-Skript aus, um das `capa_core`-Modul zu erstellen.
    ```bash
    # Windows
    .\build.bat
    ```
    Dies erstellt die `capa_core.pyd`-Datei im Hauptverzeichnis.

6.  **Ollama LLMs herunterladen:**
    Stelle sicher, dass Ollama läuft und lade die für die Architektur benötigten Modelle herunter.
    ```bash
    ollama pull granite4:3b
    ollama pull gemma3:4b
    ollama pull dolphin3
    ```

## Benutzung

Starte die interaktive Arena über die Kommandozeile:
```bash
python arena_v3.py
```

### Verfügbare Befehle

*   `process_input <text>`: Startet den Denkprozess für den gegebenen Text.
*   `reward <wert> [grund]`: Gibt dem Agenten positives Feedback für seine letzte Aktion.
*   `punish <wert> [grund]`: Gibt dem Agenten negatives Feedback für seine letzte Aktion.
*   `manage_stm`: Löst den "Schlaf- und Lernzyklus" aus.
*   `status`: Zeigt den aktuellen internen emotionalen Zustand des Agenten an.
*   `logs`: Zeigt die detaillierten Aktions- und Feedback-Protokolle der aktuellen Sitzung an.
*   `exit`: Beendet die Anwendung.
