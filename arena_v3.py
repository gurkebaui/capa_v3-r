# arena_v3.py (KORRIGIERTE main-Funktion)

import logging
from agent import Agent
from memory.subsystem import MemorySubsystem
from memory.man import MemoryAccessNetwork
from processing.layer1 import ContextEnricher

try:
    import capa_core # type: ignore
except ImportError:
    print("FATAL: Could not import 'capa_core'. Build it first.")
    exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)

def main():
    """
    The main entry point for the CAPA v3-R interactive arena.
    """
    logger = logging.getLogger("Arena")
    logger.info("--- Initializing CAPA v3-R ---")

    # --- 1. Kern-Komponenten initialisieren ---
    cpp_core = capa_core.CPPCore()
    memory_subsystem = MemorySubsystem()
    man = MemoryAccessNetwork(memory_subsystem)
    context_enricher = ContextEnricher(man)

    # --- 2. Agenten instanziieren ---
    # KORREKTUR HIER: Wir übergeben 'memory_subsystem' als viertes Argument
    agent = Agent(cpp_core, man, context_enricher, memory_subsystem)
    
    print("\n--- CAPA v3-R Arena ---")
    print("Available commands: process_input <text>, exit")

    while True:
        try:
            user_input = input("> ")
            if not user_input: continue

            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command == "exit":
                logger.info("Shutting down arena.")
                break
            
            elif command == "process_input":
                if not args:
                    print("Usage: process_input <text>")
                    continue
                
                final_result = agent.process_input(args)
                
                print("\n" + "="*20)
                print(f"[FINAL AGENT RESPONSE]: {final_result.get('external_response', 'N/A')}")
                print("="*20 + "\n")

            else:
                print(f"Unknown command: '{command}'")

        except KeyboardInterrupt:
            logger.info("\nShutting down arena due to user interrupt.")
            break
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()