# arena_v3.py (KORRIGIERTE main-Funktion)

import logging
from agent import Agent
from memory.subsystem import MemorySubsystem
from memory.man import MemoryAccessNetwork
from processing.layer1 import ContextEnricher
import json

try:
    import capa_core # type: ignore
except ImportError:
    print("FATAL: Could not import 'capa_core'. Build it first.")
    exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)


def seed_emotion_test(memory_system: MemorySubsystem):
    """Adds a memory with strong negative emotion for testing."""
    logger = logging.getLogger("TestSeeder")
    logger.info("Seeding LTM with a negative emotional memory...")
    memory_system.add_experience(
        "My first attempt at building a complex algorithm resulted in a complete system crash and data loss.",
        {"topic": "failure", "emotion": "negative"}
    )
    logger.info("Seeding complete.")


def main():
    """
    The main entry point for the CAPA v3-R interactive arena.
    """
    logger = logging.getLogger("Arena")
    logger.info("--- Initializing CAPA v3-R ---")

    cpp_core = capa_core.CPPCore()
    memory_subsystem = MemorySubsystem()
    man = MemoryAccessNetwork(memory_subsystem)
    context_enricher = ContextEnricher(man)
    agent = Agent(cpp_core, man, context_enricher, memory_subsystem)
    
    print("\n--- CAPA v3-R Arena ---")
    print("Available commands: process_input <text>, initiate_training, seed_emotion_test, exit")

    while True:
        try:
            user_input = input("> ")
            if not user_input: continue

            # --- KORREKTUR HIER: Korrekte Befehlsverarbeitung ---
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

            elif command == "initiate_training":
                agent.initiate_training()
            
            elif command == "seed_emotion_test":
                seed_emotion_test(memory_subsystem)


            elif command == "manage_stm":
                agent.manage_short_term_memory()
                print("STM management cycle completed.")



            elif command == "reward" or command == "punish":
                if not args:
                    print(f"Usage: {command} <float_value> [optional reason text]")
                    continue
                
                arg_parts = args.split(maxsplit=1)
                value_str = arg_parts[0]
                reason = arg_parts[1] if len(arg_parts) > 1 else ""
                
                try:
                    value = float(value_str)
                    if command == "reward":
                        agent.reward(value, reason)
                        print(f"Applied reward of {value} with reason: '{reason}'.")
                    else: # punish
                        agent.punish(value, reason)
                        print(f"Applied punishment of {value} with reason: '{reason}'.")
                except ValueError:
                    print(f"Usage: {command} <float_value> [optional reason text]")

            elif command == "status":
                print(agent.get_status())

            elif command == "logs":
                all_logs = agent.action_logger.get_logs()
                print("\n--- Action & Feedback Logs ---")
                print(json.dumps(all_logs, indent=2))
                print("----------------------------\n")




            else:
                print(f"Unknown command: '{command}'")

        except KeyboardInterrupt:
            logger.info("\nShutting down arena due to user interrupt.")
            break
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()