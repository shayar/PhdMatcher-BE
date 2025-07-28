import json
import numpy as np
import faiss
from typing import List, Tuple, Optional
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

class VectorDatabase:
    def __init__(self):
        self.index = None
        self.professor_mapping = {}
        self.load_index()
    
    def load_index(self):
        """Load FAISS index and professor mapping"""
        try:
            if os.path.exists(settings.FAISS_INDEX_PATH):
                self.index = faiss.read_index(settings.FAISS_INDEX_PATH)
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            else:
                logger.warning("FAISS index file not found, creating new index")
                self.index = faiss.IndexFlatL2(settings.EMBEDDING_DIMENSION)
            
            if os.path.exists(settings.FAISS_MAPPING_PATH):
                with open(settings.FAISS_MAPPING_PATH, 'r') as f:
                    self.professor_mapping = json.load(f)
                logger.info(f"Loaded professor mapping with {len(self.professor_mapping)} entries")
            else:
                logger.warning("Professor mapping file not found")
                
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            self.index = faiss.IndexFlatL2(settings.EMBEDDING_DIMENSION)
            self.professor_mapping = {}
    
    def add_embedding(self, professor_id: str, embedding: List[float]):
        """Add a professor embedding to the index"""
        if not self.index:
            return
        
        embedding_array = np.array([embedding], dtype=np.float32)
        self.index.add(embedding_array)
        
        # Map the index position to professor ID
        index_position = self.index.ntotal - 1
        self.professor_mapping[str(index_position)] = professor_id
    
    def search_similar(
        self, 
        query_embedding: List[float], 
        top_k: int = 50
    ) -> List[Tuple[str, float]]:
        """Search for similar professors"""
        if not self.index or self.index.ntotal == 0:
            return []
        
        query_array = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_array, min(top_k, self.index.ntotal))
        
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # FAISS returns -1 for invalid indices
                continue
            
            professor_id = self.professor_mapping.get(str(idx))
            if professor_id:
                # Convert L2 distance to similarity score (0-1)
                similarity_score = 1.0 / (1.0 + distance)
                results.append((professor_id, similarity_score))
        
        return results
    
    def save_index(self):
        """Save FAISS index and mapping to disk"""
        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)
            os.makedirs(os.path.dirname(settings.FAISS_MAPPING_PATH), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, settings.FAISS_INDEX_PATH)
            
            # Save professor mapping
            with open(settings.FAISS_MAPPING_PATH, 'w') as f:
                json.dump(self.professor_mapping, f)
            
            logger.info("Successfully saved FAISS index and mapping")
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    def rebuild_index(self, professor_embeddings: List[Tuple[str, List[float]]]):
        """Rebuild the entire index from scratch"""
        self.index = faiss.IndexFlatL2(settings.EMBEDDING_DIMENSION)
        self.professor_mapping = {}
        
        embeddings = []
        for i, (professor_id, embedding) in enumerate(professor_embeddings):
            embeddings.append(embedding)
            self.professor_mapping[str(i)] = professor_id
        
        if embeddings:
            embeddings_array = np.array(embeddings, dtype=np.float32)
            self.index.add(embeddings_array)
        
        self.save_index()
        logger.info(f"Rebuilt FAISS index with {len(embeddings)} professors")