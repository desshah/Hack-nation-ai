"""
Embedding generation for RAG using Hugging Face models
Creates vector embeddings for facility contexts
"""
import numpy as np
import pandas as pd
from typing import List, Dict
import logging
from pathlib import Path
import pickle
from tqdm import tqdm

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Installing sentence-transformers...")
    import subprocess
    subprocess.check_call(["pip", "install", "sentence-transformers"])
    from sentence_transformers import SentenceTransformer

from config import (
    EMBEDDING_MODEL,
    EMBEDDING_MODEL_FALLBACK,
    EMBEDDING_BATCH_SIZE,
    CACHE_DIR,
    CACHE_EMBEDDINGS
)
from data_loader import load_and_preprocess_data, get_facility_metadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for facility contexts using HuggingFace models"""
    
    def __init__(self, model_name: str = None, use_cache: bool = True):
        """
        Initialize the embedding generator
        
        Args:
            model_name: Name of the HuggingFace model to use
            use_cache: Whether to cache embeddings
        """
        self.model_name = model_name or EMBEDDING_MODEL
        self.use_cache = use_cache
        self.cache_path = CACHE_DIR / f"embeddings_{self.model_name.replace('/', '_')}.pkl"
        
        logger.info(f"Initializing embedding model: {self.model_name}")
        
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✅ Loaded model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Failed to load {self.model_name}: {e}")
            logger.info(f"Falling back to: {EMBEDDING_MODEL_FALLBACK}")
            self.model_name = EMBEDDING_MODEL_FALLBACK
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✅ Loaded fallback model: {self.model_name}")
        
        # Check embedding dimension
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding dimension: {self.embedding_dim}")
    
    def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = None,
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            batch_size: Batch size for encoding
            show_progress: Whether to show progress bar
            
        Returns:
            Numpy array of embeddings (n_texts, embedding_dim)
        """
        batch_size = batch_size or EMBEDDING_BATCH_SIZE
        
        logger.info(f"Generating embeddings for {len(texts)} texts...")
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=True  # L2 normalization for cosine similarity
        )
        
        logger.info(f"✅ Generated {len(embeddings)} embeddings")
        return embeddings
    
    def embed_facility_data(
        self,
        df: pd.DataFrame,
        text_column: str = "facility_context"
    ) -> Dict:
        """
        Generate embeddings for all facilities in the dataset
        
        Args:
            df: DataFrame with facility data
            text_column: Column containing text to embed
            
        Returns:
            Dictionary with embeddings and metadata
        """
        # Check cache first
        if self.use_cache and self.cache_path.exists():
            logger.info(f"Loading cached embeddings from {self.cache_path}")
            with open(self.cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Verify cache is for same data
            if len(cache_data['embeddings']) == len(df):
                logger.info("✅ Using cached embeddings")
                return cache_data
            else:
                logger.warning("Cache size mismatch, regenerating...")
        
        # Get texts to embed
        texts = df[text_column].fillna("").tolist()
        
        # Generate embeddings
        embeddings = self.generate_embeddings(texts)
        
        # Prepare metadata for each facility
        metadata_list = []
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Extracting metadata"):
            metadata = get_facility_metadata(row)
            metadata['text'] = texts[idx]
            metadata_list.append(metadata)
        
        result = {
            'embeddings': embeddings,
            'metadata': metadata_list,
            'model_name': self.model_name,
            'embedding_dim': self.embedding_dim,
            'n_facilities': len(df)
        }
        
        # Cache the results
        if self.use_cache:
            logger.info(f"Caching embeddings to {self.cache_path}")
            with open(self.cache_path, 'wb') as f:
                pickle.dump(result, f)
        
        return result
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a search query
        
        Args:
            query: Query text
            
        Returns:
            Query embedding vector
        """
        embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )[0]
        return embedding


def create_embeddings_for_dataset(
    force_regenerate: bool = False
) -> Dict:
    """
    Main function to create embeddings for the entire dataset
    
    Args:
        force_regenerate: Force regeneration even if cache exists
        
    Returns:
        Dictionary with embeddings and metadata
    """
    logger.info("=" * 80)
    logger.info("STEP 3: Creating Embeddings for RAG")
    logger.info("=" * 80)
    
    # Load data
    df = load_and_preprocess_data()
    logger.info(f"Loaded {len(df)} facilities")
    
    # Initialize embedding generator
    generator = EmbeddingGenerator(use_cache=not force_regenerate)
    
    # Generate embeddings
    result = generator.embed_facility_data(df)
    
    logger.info("=" * 80)
    logger.info("📊 Embedding Generation Complete!")
    logger.info(f"   - Model: {result['model_name']}")
    logger.info(f"   - Embeddings: {result['n_facilities']}")
    logger.info(f"   - Dimension: {result['embedding_dim']}")
    logger.info(f"   - Shape: {result['embeddings'].shape}")
    logger.info("=" * 80)
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate embeddings for facility data")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration even if cache exists"
    )
    args = parser.parse_args()
    
    result = create_embeddings_for_dataset(force_regenerate=args.force)
    
    # Show sample
    print(f"\n📄 Sample embedding:")
    print(f"   Facility: {result['metadata'][0]['facility_name']}")
    print(f"   Embedding vector (first 10 dims): {result['embeddings'][0][:10]}")
    print(f"   Embedding norm: {np.linalg.norm(result['embeddings'][0]):.4f}")
