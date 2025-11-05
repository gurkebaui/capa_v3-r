# memory/listener.py

import time
import json
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from memory.subsystem import MemorySubsystem

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [LTM Listener] - %(message)s')

class JournalEventHandler(FileSystemEventHandler):
    def __init__(self, memory_subsystem: MemorySubsystem, journal_path: str):
        self.memory_subsystem = memory_subsystem
        self.journal_path = journal_path
        # Keep track of the last read position in the file
        try:
            with open(self.journal_path, 'r') as f:
                self.last_pos = f.tell()
        except FileNotFoundError:
            # Create the file if it doesn't exist
            open(self.journal_path, 'a').close()
            self.last_pos = 0

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
                    if not line:
                        continue
                    
                    try:
                        # Validate and process the JSON object
                        data = json.loads(line)
                        if 'text' in data and 'metadata' in data:
                            self.memory_subsystem.add_experience(data['text'], data['metadata'])
                        else:
                            logging.warning(f"Invalid journal entry (missing keys): {line}")
                    except json.JSONDecodeError:
                        logging.error(f"Failed to decode JSON from line: {line}")
                    except Exception as e:
                        logging.error(f"An unexpected error occurred while processing line '{line}': {e}")
                
                # Update last position to the end of the file
                self.last_pos = f.tell()
        except FileNotFoundError:
             logging.error(f"Journal file not found at {self.journal_path}")


def run_ltm_listener(journal_path: str = "journals/ltm_journal.wal"):
    """
    Starts the listener process that monitors the journal file.
    """
    logging.info("Starting LTM Listener Process...")
    memory_system = MemorySubsystem()
    event_handler = JournalEventHandler(memory_system, journal_path)
    
    observer = Observer()
    observer.schedule(event_handler, path='journals', recursive=False)
    observer.start()
    
    logging.info(f"Now monitoring '{journal_path}' for changes.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logging.info("LTM Listener Process stopped.")

if __name__ == "__main__":
    # Allows running this script directly to start the listener
    run_ltm_listener()