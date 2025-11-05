# memory/subsystem.py

import chromadb
from chromadb.utils import embedding_functions
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [MemorySubsystem] - %(message)s')

class MemorySubsystem:
    def __init__(self, db_path="./db", collection_name="ltm_collection"):
        """
        Initializes the persistent ChromaDB backend and the sentence transformer model.
        """
        logging.info("Initializing Memory Subsystem...")
        # Use a standard sentence transformer model
        self.sentence_transformer = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Initialize ChromaDB client with persistence
        client = chromadb.PersistentClient(path=db_path)
        
        self.collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.sentence_transformer
        )
        logging.info(f"ChromaDB collection '{collection_name}' loaded/created.")

    def add_experience(self, text: str, metadata: dict):
        """
        Adds a new experience (text) with its metadata to the LTM.
        """
        # ChromaDB requires unique IDs for each document
        # We'll use a timestamp-based ID for simplicity
        doc_id = f"exp_{int(time.time() * 1000)}"
        
        try:
            self.collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logging.info(f"Added experience to LTM with ID: {doc_id}")
        except Exception as e:
            logging.error(f"Failed to add experience to ChromaDB: {e}")

    def query_memories(self, query_text: str, n_results: int = 5) -> list:
        """
        Queries the LTM for relevant memories based on a query text.
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            logging.error(f"Failed to query ChromaDB: {e}")
            return []