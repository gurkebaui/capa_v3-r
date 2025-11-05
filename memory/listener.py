# memory/listener.py (FINAL, POLLING VERSION)

import time
import json
import logging
import os
# --- DIE ÄNDERUNG: Wir importieren den PollingObserver ---
from watchdog.observers.polling import PollingObserver as Observer 
from watchdog.events import FileSystemEventHandler
from memory.subsystem import MemorySubsystem

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [LTM Listener] - %(message)s')

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DEFAULT_JOURNAL_PATH = os.path.join(PROJECT_ROOT, 'journals', 'ltm_journal.wal')

# ... (Der Rest der Datei ist identisch und korrekt) ...
class JournalEventHandler(FileSystemEventHandler):
    def __init__(self, memory_subsystem: MemorySubsystem, journal_path: str):
        self.memory_subsystem = memory_subsystem
        self.journal_path = journal_path
        
        if not os.path.exists(self.journal_path):
            open(self.journal_path, 'a').close()

        with open(self.journal_path, 'r') as f:
            f.seek(0, 2)
            self.last_pos = f.tell()
            
    def on_modified(self, event):
        if event.src_path == self.journal_path:
            self._process_new_lines()
            
    def _process_new_lines(self):
        try:
            with open(self.journal_path, 'r') as f:
                f.seek(self.last_pos)
                new_lines = f.readlines()
                if not new_lines:
                    return

                for line in new_lines:
                    line = line.strip()
                    if not line: continue
                    
                    try:
                        data = json.loads(line)
                        if 'text' in data and 'metadata' in data:
                            self.memory_subsystem.add_experience(data['text'], data['metadata'])
                        else:
                            logging.warning(f"Invalid journal entry (missing keys): {line}")
                    except Exception as e:
                        logging.error(f"Error processing line '{line}': {e}")
                
                self.last_pos = f.tell()
        except FileNotFoundError:
             logging.error(f"Journal file not found at {self.journal_path}")


def run_ltm_listener(journal_path: str = DEFAULT_JOURNAL_PATH):
    logging.info("Starting LTM Listener Process...")
    journal_dir = os.path.dirname(journal_path)
    os.makedirs(journal_dir, exist_ok=True)
    
    memory_system = MemorySubsystem()
    event_handler = JournalEventHandler(memory_system, journal_path)
    
    # Hier wird jetzt der PollingObserver verwendet.
    observer = Observer() 
    observer.schedule(event_handler, path=journal_dir, recursive=False)
    observer.start()
    
    logging.info(f"Now monitoring '{journal_path}' for changes via Polling.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logging.info("LTM Listener Process stopped.")

if __name__ == "__main__":
    run_ltm_listener()