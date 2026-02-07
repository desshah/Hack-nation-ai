"""
Retriever for RAG - searches vector store and returns relevant facilities
"""
import numpy as np
from typing import List, Dict, Optional
import logging

from vector_store import VectorStore
from embeddings import EmbeddingGenerator
from config import TOP_K_RETRIEVAL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Retriever:
    """Retrieves relevant facilities using vector search"""
    
    def __init__(self):
        """Initialize retriever with vector store and embedding generator"""
        self.vector_store = VectorStore()
        self.embedding_generator = EmbeddingGenerator()
        logger.info("✅ Retriever initialized")
    
    def search(
        self,
        query: str,
        top_k: int = None,
        region_filter: Optional[str] = None,
        facility_type_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for relevant facilities
        
        Args:
            query: Search query text
            top_k: Number of results to return
            region_filter: Optional region to filter by
            facility_type_filter: Optional facility type to filter by
            
        Returns:
            List of facility dictionaries with scores
        """
        top_k = top_k or TOP_K_RETRIEVAL
        
        # Build filter dict
        filters = {}
        if region_filter:
            filters['region'] = region_filter
        if facility_type_filter:
            filters['facility_type'] = facility_type_filter
        
        # Search
        results_df = self.vector_store.search_by_text(
            query,
            self.embedding_generator,
            top_k=top_k,
            filter_dict=filters if filters else None
        )
        
        # Convert to list of dicts
        results = []
        for idx, row in results_df.iterrows():
            result = {
                'facility_id': row['facility_id'],
                'facility_name': row['facility_name'],
                'region': row['region'],
                'city': row['city'],
                'facility_type': row['facility_type'],
                'row_id': row['row_id'],
                'text': row['text'],
                'score': float(row['_distance']),
                'source_url': row.get('source_url', '')
            }
            results.append(result)
        
        return results
    
    def get_facility_by_id(self, facility_id: str) -> Optional[Dict]:
        """Get specific facility by ID"""
        return self.vector_store.get_by_facility_id(facility_id)
    
    def get_facilities_by_region(self, region: str) -> List[Dict]:
        """Get all facilities in a region"""
        results_df = self.vector_store.get_by_region(region)
        return results_df.to_dict('records')


if __name__ == "__main__":
    retriever = Retriever()
    
    test_queries = [
        "emergency care cardiac surgery",
        "maternity delivery services",
        "X-ray ultrasound diagnostic imaging"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        results = retriever.search(query, top_k=3)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['facility_name']} ({result['region']}) - Score: {result['score']:.4f}")
