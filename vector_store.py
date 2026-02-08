"""
Vector store management using LanceDB
Stores embeddings and enables similarity search
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Optional
import logging
from pathlib import Path

try:
    import lancedb
except ImportError:
    print("Installing lancedb...")
    import subprocess
    subprocess.check_call(["pip", "install", "lancedb"])
    import lancedb

from config import VECTOR_DB_PATH
from embeddings import EmbeddingGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store for facility embeddings using LanceDB"""
    
    def __init__(self, db_path: Path = None):
        """
        Initialize vector store
        
        Args:
            db_path: Path to LanceDB database
        """
        self.db_path = db_path or VECTOR_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initializing LanceDB at: {self.db_path}")
        self.db = lancedb.connect(str(self.db_path))
        self.table_name = "facilities"
        self.table = None
        
    def create_table(self, embeddings_data: Dict) -> None:
        """
        Create or replace table with embeddings
        
        Args:
            embeddings_data: Dictionary from EmbeddingGenerator with embeddings and metadata
        """
        logger.info(f"Creating table '{self.table_name}'...")
        
        # Prepare data for LanceDB
        records = []
        for i, metadata in enumerate(embeddings_data['metadata']):
            record = {
                'vector': embeddings_data['embeddings'][i].tolist(),
                'facility_id': str(metadata['facility_id']),
                'facility_name': str(metadata['facility_name']),
                'region': str(metadata.get('region', '')),
                'city': str(metadata.get('city', '')),
                'facility_type': str(metadata.get('facility_type', '')),
                'row_id': str(metadata['row_id']),
                'source_url': str(metadata.get('source_url', '')),
                'text': str(metadata['text'])
            }
            records.append(record)
        
        # Create table
        if self.table_name in self.db.table_names():
            logger.info(f"Table '{self.table_name}' exists, dropping...")
            self.db.drop_table(self.table_name)
        
        self.table = self.db.create_table(self.table_name, records)
        logger.info(f"✅ Created table with {len(records)} records")
        
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> pd.DataFrame:
        """
        Search for similar facilities
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter_dict: Optional filters (e.g., {'region': 'Ashanti'})
            
        Returns:
            DataFrame with search results and scores
        """
        if self.table is None:
            self.table = self.db.open_table(self.table_name)
        
        # Convert to list for LanceDB
        query_list = query_vector.tolist() if isinstance(query_vector, np.ndarray) else query_vector
        
        # Perform search
        results = self.table.search(query_list).limit(top_k)
        
        # Apply filters if provided
        if filter_dict:
            for key, value in filter_dict.items():
                results = results.where(f"{key} = '{value}'")
        
        # Execute and convert to DataFrame
        results_df = results.to_pandas()
        
        return results_df
    
    def search_by_text(
        self,
        query_text: str,
        embedding_generator: EmbeddingGenerator,
        top_k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> pd.DataFrame:
        """
        Search by text query
        
        Args:
            query_text: Text query
            embedding_generator: Generator to embed the query
            top_k: Number of results
            filter_dict: Optional filters
            
        Returns:
            DataFrame with search results
        """
        logger.info(f"Searching for: '{query_text}'")
        
        # Embed query
        query_vector = embedding_generator.embed_query(query_text)
        
        # Search
        results = self.search(query_vector, top_k=top_k, filter_dict=filter_dict)
        
        logger.info(f"Found {len(results)} results")
        return results
    
    def get_by_facility_id(self, facility_id: str) -> Optional[Dict]:
        """
        Get facility by ID
        
        Args:
            facility_id: Facility unique ID
            
        Returns:
            Facility record or None
        """
        if self.table is None:
            self.table = self.db.open_table(self.table_name)
        
        results = self.table.search().where(f"facility_id = '{facility_id}'").limit(1).to_pandas()
        
        if len(results) > 0:
            return results.iloc[0].to_dict()
        return None
    
    def get_by_region(self, region: str) -> pd.DataFrame:
        """
        Get all facilities in a region
        
        Args:
            region: Region name
            
        Returns:
            DataFrame with facilities
        """
        if self.table is None:
            self.table = self.db.open_table(self.table_name)
        
        # Create a dummy vector for the search (LanceDB requires vector search)
        dummy_vector = np.zeros(self.table.schema.field('vector').type.value_type.list_size)
        
        results = self.table.search(dummy_vector.tolist()).where(f"region = '{region}'").limit(1000).to_pandas()
        
        return results
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store
        
        Returns:
            Dictionary with stats
        """
        if self.table is None:
            self.table = self.db.open_table(self.table_name)
        
        # Get all data for stats
        all_data = self.table.to_pandas()
        
        stats = {
            'total_facilities': len(all_data),
            'regions': all_data['region'].nunique(),
            'facility_types': all_data['facility_type'].value_counts().to_dict(),
            'cities': all_data['city'].nunique(),
            'regions_list': sorted(all_data['region'].unique().tolist())
        }
        
        return stats


def build_vector_store(embeddings_data: Dict) -> VectorStore:
    """
    Build vector store from embeddings
    
    Args:
        embeddings_data: Output from create_embeddings_for_dataset()
        
    Returns:
        VectorStore instance
    """
    logger.info("=" * 80)
    logger.info("Building Vector Store (LanceDB)")
    logger.info("=" * 80)
    
    store = VectorStore()
    store.create_table(embeddings_data)
    
    # Show stats
    stats = store.get_stats()
    logger.info("=" * 80)
    logger.info("📊 Vector Store Statistics:")
    logger.info(f"   - Total facilities: {stats['total_facilities']}")
    logger.info(f"   - Regions: {stats['regions']}")
    logger.info(f"   - Cities: {stats['cities']}")
    logger.info(f"   - Facility types: {stats['facility_types']}")
    logger.info("=" * 80)
    
    return store


if __name__ == "__main__":
    from embeddings import create_embeddings_for_dataset
    
    # Create embeddings
    embeddings_data = create_embeddings_for_dataset()
    
    # Build vector store
    store = build_vector_store(embeddings_data)
    
    # Test search
    print("\n🔍 Testing search...")
    generator = EmbeddingGenerator()
    
    test_queries = [
        "hospitals with emergency care in Ashanti",
        "maternity services",
        "X-ray and ultrasound equipment"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = store.search_by_text(query, generator, top_k=3)
        print(f"Top result: {results.iloc[0]['facility_name']} ({results.iloc[0]['region']})")
        print(f"Score: {results.iloc[0]['_distance']:.4f}")
