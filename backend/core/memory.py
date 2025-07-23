import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from openai import OpenAI
from backend.core.config import get_settings
import json
import uuid

settings = get_settings()

class FAISSMemorySystem:
    """Enhanced FAISS-based memory system for content storage and retrieval"""
    
    def __init__(self, dimension: int = 1536, index_path: str = "data/memory"):
        self.dimension = dimension
        self.index_path = index_path
        self.index_file = os.path.join(index_path, "faiss.index")
        self.metadata_file = os.path.join(index_path, "metadata.json")
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        
        # Create directories
        os.makedirs(index_path, exist_ok=True)
        
        # Initialize or load FAISS index
        self.index = self._load_or_create_index()
        self.metadata = self._load_metadata()
        
    def _load_or_create_index(self) -> faiss.Index:
        """Load existing FAISS index or create new one"""
        if os.path.exists(self.index_file):
            try:
                return faiss.read_index(self.index_file)
            except Exception as e:
                print(f"Error loading index: {e}. Creating new index.")
        
        # Create new index using IndexFlatIP (Inner Product) for cosine similarity
        return faiss.IndexFlatIP(self.dimension)
    
    def _load_metadata(self) -> Dict:
        """Load metadata mapping index IDs to content information"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}. Starting with empty metadata.")
        return {}
    
    def _save_index(self):
        """Save FAISS index to disk"""
        faiss.write_index(self.index, self.index_file)
    
    def _save_metadata(self):
        """Save metadata to disk"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)
    
    def embed_text(self, text: str) -> np.ndarray:
        """Create embedding for text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            # Normalize for cosine similarity
            return embedding / np.linalg.norm(embedding)
        except Exception as e:
            print(f"Embedding failed: {e}")
            return np.zeros(self.dimension, dtype=np.float32)
    
    def store_content(self, content: str, metadata: Dict[str, Any]) -> str:
        """Store content with embeddings and metadata"""
        content_id = str(uuid.uuid4())
        
        # Create embedding
        embedding = self.embed_text(content)
        
        if embedding.any():
            # Add to FAISS index
            self.index.add(embedding.reshape(1, -1))
            
            # Store metadata with index ID
            index_id = self.index.ntotal - 1
            self.metadata[str(index_id)] = {
                'content_id': content_id,
                'content': content,
                'metadata': metadata,
                'created_at': datetime.utcnow().isoformat(),
                'embedding_norm': float(np.linalg.norm(embedding))
            }
            
            # Save to disk
            self._save_index()
            self._save_metadata()
            
            return content_id
        
        return None
    
    def search_similar(self, query: str, top_k: int = 5, threshold: float = 0.7) -> List[Dict]:
        """Search for similar content"""
        if self.index.ntotal == 0:
            return []
        
        query_embedding = self.embed_text(query)
        
        if not query_embedding.any():
            return []
        
        # Search FAISS index
        scores, indices = self.index.search(query_embedding.reshape(1, -1), top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and score >= threshold:  # Valid index and above threshold
                metadata = self.metadata.get(str(idx), {})
                if metadata:
                    results.append({
                        'content_id': metadata.get('content_id'),
                        'content': metadata.get('content', ''),
                        'similarity_score': float(score),
                        'metadata': metadata.get('metadata', {}),
                        'created_at': metadata.get('created_at')
                    })
        
        return results
    
    def get_content_by_type(self, content_type: str, limit: int = 10) -> List[Dict]:
        """Retrieve content by type"""
        results = []
        for idx, meta in self.metadata.items():
            if meta.get('metadata', {}).get('type') == content_type:
                results.append({
                    'content_id': meta.get('content_id'),
                    'content': meta.get('content', ''),
                    'metadata': meta.get('metadata', {}),
                    'created_at': meta.get('created_at')
                })
                if len(results) >= limit:
                    break
        
        return sorted(results, key=lambda x: x['created_at'], reverse=True)
    
    def get_high_performing_content(self, min_engagement: float = 5.0, limit: int = 10) -> List[Dict]:
        """Retrieve high-performing content for learning"""
        results = []
        for idx, meta in self.metadata.items():
            engagement = meta.get('metadata', {}).get('engagement_rate', 0)
            if engagement >= min_engagement:
                results.append({
                    'content_id': meta.get('content_id'),
                    'content': meta.get('content', ''),
                    'engagement_rate': engagement,
                    'metadata': meta.get('metadata', {}),
                    'created_at': meta.get('created_at')
                })
        
        # Sort by engagement rate
        results.sort(key=lambda x: x['engagement_rate'], reverse=True)
        return results[:limit]
    
    def get_content_for_repurposing(self, days_old: int = 30, min_engagement: float = 3.0) -> List[Dict]:
        """Find content suitable for repurposing"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        results = []
        for idx, meta in self.metadata.items():
            created_at = datetime.fromisoformat(meta.get('created_at', ''))
            engagement = meta.get('metadata', {}).get('engagement_rate', 0)
            
            if created_at < cutoff_date and engagement >= min_engagement:
                results.append({
                    'content_id': meta.get('content_id'),
                    'content': meta.get('content', ''),
                    'engagement_rate': engagement,
                    'age_days': (datetime.utcnow() - created_at).days,
                    'metadata': meta.get('metadata', {}),
                    'created_at': meta.get('created_at')
                })
        
        # Sort by engagement rate
        results.sort(key=lambda x: x['engagement_rate'], reverse=True)
        return results
    
    def analyze_content_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in stored content"""
        if not self.metadata:
            return {'error': 'No content available for analysis'}
        
        patterns = {
            'total_content': len(self.metadata),
            'content_types': {},
            'platforms': {},
            'avg_engagement': 0,
            'top_topics': [],
            'temporal_patterns': {}
        }
        
        engagements = []
        for idx, meta in self.metadata.items():
            metadata = meta.get('metadata', {})
            
            # Content types
            content_type = metadata.get('type', 'unknown')
            patterns['content_types'][content_type] = patterns['content_types'].get(content_type, 0) + 1
            
            # Platforms
            platform = metadata.get('platform', 'unknown')
            patterns['platforms'][platform] = patterns['platforms'].get(platform, 0) + 1
            
            # Engagement
            engagement = metadata.get('engagement_rate', 0)
            if engagement > 0:
                engagements.append(engagement)
            
            # Topics
            topic = metadata.get('topic', 'general')
            patterns['top_topics'].append(topic)
        
        # Calculate averages
        if engagements:
            patterns['avg_engagement'] = sum(engagements) / len(engagements)
        
        # Top topics (simplified)
        from collections import Counter
        topic_counts = Counter(patterns['top_topics'])
        patterns['top_topics'] = [{'topic': topic, 'count': count} 
                                for topic, count in topic_counts.most_common(10)]
        
        return patterns
    
    def cleanup_old_content(self, days_to_keep: int = 365):
        """Remove content older than specified days"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        indices_to_remove = []
        for idx, meta in list(self.metadata.items()):
            created_at = datetime.fromisoformat(meta.get('created_at', ''))
            if created_at < cutoff_date:
                indices_to_remove.append(int(idx))
                del self.metadata[idx]
        
        # Note: FAISS doesn't support efficient deletion, so we'd need to rebuild index
        # For now, just remove from metadata
        if indices_to_remove:
            self._save_metadata()
            print(f"Cleaned up {len(indices_to_remove)} old content items from metadata")
        
        return len(indices_to_remove)

# Global memory instance
memory_system = FAISSMemorySystem()