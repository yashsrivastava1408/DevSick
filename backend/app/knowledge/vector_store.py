import os
import chromadb
from chromadb.config import Settings
import logging
from typing import List, Dict, Any, Optional
import uuid

logger = logging.getLogger(__name__)

class IncidentMemory:
    """Vector database for storing and retrieving past incidents and resolutions."""

    def __init__(self, persist_directory: str = "./data/chroma"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="incidents",
            metadata={"hnsw:space": "cosine"}
        )

    def store_incident(self, incident_id: str, summary: str, root_cause: str, resolution: List[str], scenario_type: str):
        """Store an incident and its resolution in the vector store."""
        # Combine fields into a rich document for embedding
        document = f"Scenario: {scenario_type}\nSummary: {summary}\nRoot Cause: {root_cause}\nResolution Actions: {', '.join(resolution)}"
        
        self.collection.add(
            ids=[incident_id],
            documents=[document],
            metadatas=[{
                "incident_id": incident_id,
                "scenario_type": scenario_type,
                "root_cause": root_cause,
                "resolution": json.dumps(resolution) if isinstance(resolution, list) else resolution
            }]
        )
        logger.info(f"Stored incident {incident_id} in memory.")

    def find_similar_incidents(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Search for similar past incidents."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        formatted_results = []
        if results['ids']:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i]
                })
        return formatted_results

    def ingest_documentation(self, filepath: str):
        """Read and store documentation for architectural context."""
        if not os.path.exists(filepath):
            return
            
        with open(filepath, "r") as f:
            content = f.read()
            
        doc_id = f"doc_{os.path.basename(filepath)}"
        self.collection.add(
            ids=[doc_id],
            documents=[content],
            metadatas=[{"type": "documentation", "source": filepath}]
        )
        logger.info(f"Ingested documentation: {filepath}")

# Global singleton
import json
incident_memory = IncidentMemory()
