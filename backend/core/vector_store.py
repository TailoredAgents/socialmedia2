"""
FAISS Vector Store Implementation
Provides high-performance vector indexing and similarity search for content embeddings.
"""

import os
import json
import uuid
import pickle
import builtins
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS not available, install faiss-cpu for better performance")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """
    High-performance FAISS-based vector store for content embeddings.
    
    Features:
    - FAISS IndexFlatIP for efficient cosine similarity search
    - Persistent storage with automatic loading/saving
    - Batch operations for optimal performance
    - Memory-efficient operations with configurable limits
    """
    
    def __init__(
        self, 
        dimension: int = 1536,
        index_path: str = "data/faiss_indexes",
        index_type: str = "flat_ip",
        max_vectors_in_memory: int = 100000
    ):
        """
        Initialize vector store.
        
        Args:
            dimension: Embedding vector dimension (1536 for OpenAI ada-002)
            index_path: Directory to store index files
            index_type: FAISS index type ('flat_ip', 'hnsw', 'ivf')
            max_vectors_in_memory: Maximum vectors to keep in memory
        """
        self.dimension = dimension
        self.index_path = index_path
        self.index_type = index_type
        self.max_vectors_in_memory = max_vectors_in_memory
        
        # File paths
        self.index_file = os.path.join(index_path, "faiss.index")
        self.metadata_file = os.path.join(index_path, "metadata.json")
        self.id_mapping_file = os.path.join(index_path, "id_mapping.json")
        
        # Create directory if it doesn't exist
        os.makedirs(index_path, exist_ok=True)
        
        # Initialize components
        self._index = self._create_or_load_index()
        self._metadata = self._load_metadata()
        self._id_mapping = self._load_id_mapping()
        self._next_internal_id = max([int(k) for k in self._id_mapping.keys()] + [-1]) + 1
        
        logger.info(f"VectorStore initialized with {self.total_vectors} vectors")
    
    def _create_or_load_index(self):
        """Create new FAISS index or load existing one."""
        if not FAISS_AVAILABLE:
            logger.warning("FAISS not available, using fallback implementation")
            return None
            
        # Try to load existing index
        if os.path.exists(self.index_file):
            try:
                index = faiss.read_index(self.index_file)
                logger.info(f"Loaded existing FAISS index with {index.ntotal} vectors")
                return index
            except Exception as e:
                logger.error(f"Failed to load index: {e}. Creating new index.")
        
        # Create new index based on type
        if self.index_type == "flat_ip":
            # Inner Product index for normalized vectors (cosine similarity)
            index = faiss.IndexFlatIP(self.dimension)
        elif self.index_type == "hnsw":
            # HNSW index for faster search with approximate results
            index = faiss.IndexHNSWFlat(self.dimension, 32)
            index.hnsw.efConstruction = 40
            index.hnsw.efSearch = 16
        elif self.index_type == "ivf":
            # IVF index for very large datasets
            quantizer = faiss.IndexFlatIP(self.dimension)
            index = faiss.IndexIVFFlat(quantizer, self.dimension, min(100, max(1, self.max_vectors_in_memory // 1000)))
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")
        
        logger.info(f"Created new {self.index_type} FAISS index")
        return index
    
    def _load_metadata(self) -> Dict[str, Dict]:
        """Load metadata mapping internal IDs to content information."""
        if os.path.exists(self.metadata_file):
            try:
                with builtins.open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load metadata: {e}")
        return {}
    
    def _load_id_mapping(self) -> Dict[str, str]:
        """Load mapping from internal IDs to content IDs."""
        if os.path.exists(self.id_mapping_file):
            try:
                with builtins.open(self.id_mapping_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load ID mapping: {e}")
        return {}
    
    def _save_index(self):
        """Save FAISS index to disk."""
        if not FAISS_AVAILABLE or not self._index:
            return
            
        try:
            faiss.write_index(self._index, self.index_file)
            logger.info("FAISS index saved successfully")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def _save_metadata(self):
        """Save metadata to disk."""
        try:
            with builtins.open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self._metadata, f, indent=2, default=str, ensure_ascii=False)
            logger.info("Metadata saved successfully")
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def _save_id_mapping(self):
        """Save ID mapping to disk."""
        try:
            with builtins.open(self.id_mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self._id_mapping, f, indent=2)
            logger.info("ID mapping saved successfully")
        except Exception as e:
            logger.error(f"Failed to save ID mapping: {e}")
    
    def add_vector(
        self, 
        vector: np.ndarray, 
        content_id: str = None, 
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Add a single vector to the index.
        
        Args:
            vector: Normalized embedding vector
            content_id: Unique content identifier (auto-generated if None)
            metadata: Associated metadata
            
        Returns:
            Content ID of the added vector
        """
        if not FAISS_AVAILABLE:
            raise RuntimeError("FAISS not available")
        
        if content_id is None:
            content_id = str(uuid.uuid4())
        
        # Ensure vector is properly shaped and normalized
        if vector.ndim == 1:
            vector = vector.reshape(1, -1)
        
        # Verify vector is normalized for cosine similarity
        norm = np.linalg.norm(vector)
        if abs(norm - 1.0) > 0.001:
            logger.warning(f"Vector norm {norm} != 1.0, normalizing")
            vector = vector / norm
        
        # Add to index
        self._index.add(vector.astype(np.float32))
        
        # Store metadata and mapping
        internal_id = str(self._next_internal_id)
        self._id_mapping[internal_id] = content_id
        self._metadata[internal_id] = {
            'content_id': content_id,
            'metadata': metadata or {},
            'created_at': datetime.utcnow().isoformat(),
            'vector_norm': float(norm)
        }
        
        self._next_internal_id += 1
        
        # Save periodically or when reaching threshold
        if self._next_internal_id % 100 == 0:
            self._save_all()
        
        logger.info(f"Added vector for content_id: {content_id}")
        return content_id
    
    def add_vectors_batch(
        self, 
        vectors: np.ndarray, 
        content_ids: List[str] = None, 
        metadata_list: List[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Add multiple vectors in batch for better performance.
        
        Args:
            vectors: Array of normalized embedding vectors [n_vectors, dimension]
            content_ids: List of content IDs (auto-generated if None)
            metadata_list: List of metadata dicts
            
        Returns:
            List of content IDs for added vectors
        """
        if not FAISS_AVAILABLE:
            raise RuntimeError("FAISS not available")
        
        n_vectors = vectors.shape[0]
        
        if content_ids is None:
            content_ids = [str(uuid.uuid4()) for _ in range(n_vectors)]
        
        if metadata_list is None:
            metadata_list = [{} for _ in range(n_vectors)]
        
        # Normalize vectors if needed
        norms = np.linalg.norm(vectors, axis=1)
        mask = np.abs(norms - 1.0) > 0.001
        if np.any(mask):
            logger.warning(f"Normalizing {np.sum(mask)} vectors")
            vectors[mask] = vectors[mask] / norms[mask].reshape(-1, 1)
        
        # Add to index
        self._index.add(vectors.astype(np.float32))
        
        # Store metadata and mappings
        for i, (content_id, metadata) in enumerate(zip(content_ids, metadata_list)):
            internal_id = str(self._next_internal_id + i)
            self._id_mapping[internal_id] = content_id
            self._metadata[internal_id] = {
                'content_id': content_id,
                'metadata': metadata,
                'created_at': datetime.utcnow().isoformat(),
                'vector_norm': float(norms[i])
            }
        
        self._next_internal_id += n_vectors
        self._save_all()
        
        logger.info(f"Added {n_vectors} vectors in batch")
        return content_ids
    
    def search(
        self, 
        query_vector: np.ndarray, 
        k: int = 5, 
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of search results with content_id, score, and metadata
        """
        if not FAISS_AVAILABLE or self.total_vectors == 0:
            return []
        
        # Ensure query vector is properly shaped and normalized
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        
        norm = np.linalg.norm(query_vector)
        if abs(norm - 1.0) > 0.001:
            query_vector = query_vector / norm
        
        # Search index
        scores, indices = self._index.search(query_vector.astype(np.float32), k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1 or score < threshold:  # Invalid index or below threshold
                continue
                
            internal_id = str(idx)
            if internal_id in self._metadata:
                result = {
                    'content_id': self._id_mapping.get(internal_id),
                    'similarity_score': float(score),
                    'metadata': self._metadata[internal_id]['metadata'],
                    'created_at': self._metadata[internal_id]['created_at']
                }
                results.append(result)
        
        return results
    
    def get_vector_by_content_id(self, content_id: str) -> Optional[np.ndarray]:
        """
        Retrieve vector by content ID.
        Note: This is expensive as FAISS doesn't support direct ID lookup.
        """
        # Find internal ID
        internal_id = None
        for iid, cid in self._id_mapping.items():
            if cid == content_id:
                internal_id = int(iid)
                break
        
        if internal_id is None:
            return None
        
        # FAISS doesn't support direct vector retrieval by ID
        # This would require reconstructing from index, which is expensive
        logger.warning("Direct vector retrieval is expensive with FAISS")
        return None
    
    def remove_vector(self, content_id: str) -> bool:
        """
        Remove vector by content ID.
        Note: FAISS doesn't support efficient deletion, only metadata removal.
        """
        # Find and remove from metadata
        internal_id = None
        for iid, cid in self._id_mapping.items():
            if cid == content_id:
                internal_id = iid
                break
        
        if internal_id is None:
            return False
        
        # Remove from metadata and mapping
        self._metadata.pop(internal_id, None)
        self._id_mapping.pop(internal_id, None)
        
        self._save_metadata()
        self._save_id_mapping()
        
        logger.info(f"Removed metadata for content_id: {content_id}")
        logger.warning("Vector still exists in FAISS index (rebuild required for full removal)")
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            'total_vectors': self.total_vectors,
            'dimension': self.dimension,
            'index_type': self.index_type,
            'memory_usage_mb': self._estimate_memory_usage(),
            'faiss_available': FAISS_AVAILABLE,
            'metadata_count': len(self._metadata),
            'id_mapping_count': len(self._id_mapping)
        }
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB."""
        if not FAISS_AVAILABLE or not self._index:
            return 0.0
        
        # Rough estimate: vectors + metadata
        vector_size = self.total_vectors * self.dimension * 4  # float32
        metadata_size = len(json.dumps(self._metadata).encode('utf-8'))
        return (vector_size + metadata_size) / (1024 * 1024)
    
    def rebuild_index(self):
        """
        Rebuild index from scratch (useful after many deletions).
        This is expensive but ensures optimal performance.
        """
        if not FAISS_AVAILABLE:
            return
        
        logger.info("Rebuilding FAISS index...")
        
        # Create new index
        old_index = self._index
        self._index = self._create_or_load_index()
        
        # Note: Would need to re-add all valid vectors here
        # This is a placeholder for full implementation
        logger.warning("Index rebuild not fully implemented - requires vector storage")
    
    def _save_all(self):
        """Save all components to disk."""
        self._save_index()
        self._save_metadata()
        self._save_id_mapping()
    
    @property
    def total_vectors(self) -> int:
        """Get total number of vectors in index."""
        if not FAISS_AVAILABLE or not self._index:
            return 0
        return self._index.ntotal
    
    @property
    def is_trained(self) -> bool:
        """Check if index is trained (relevant for some index types)."""
        if not FAISS_AVAILABLE or not self._index:
            return False
        return self._index.is_trained
    
    def train(self, training_vectors: np.ndarray):
        """Train index with sample vectors (for IVF and other index types)."""
        if not FAISS_AVAILABLE or not self._index:
            return
        
        if hasattr(self._index, 'train') and not self.is_trained:
            logger.info(f"Training index with {training_vectors.shape[0]} vectors")
            self._index.train(training_vectors.astype(np.float32))
            self._save_index()
    
    def __del__(self):
        """Ensure data is saved when object is destroyed."""
        try:
            self._save_all()
        except:
            pass  # Ignore errors during cleanup

# Global instance
vector_store = VectorStore()