"""
Data ingestion and preprocessing utilities
Loads and normalizes the Ghana facility dataset for IDP processing
VF-compliant: Parses all official VF columns including procedure, equipment, capability, specialties
"""
import pandas as pd
import re
import json
from typing import Dict, List, Optional
from pathlib import Path
import logging

from config import RAW_DATA_FILE, ENRICHED_DATA_FILE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def safe_parse_json_list(value) -> List[str]:
    """
    Safely parse JSON list strings from VF dataset
    Handles: '["item1", "item2"]' format
    """
    if pd.isna(value) or value is None or value == '':
        return []
    
    if isinstance(value, list):
        return value
    
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
        return [str(parsed)]
    except (json.JSONDecodeError, TypeError):
        # Try string split as fallback
        if isinstance(value, str):
            # Remove brackets and quotes
            cleaned = value.strip('[]"\'')
            if ',' in cleaned:
                return [item.strip(' "\'"') for item in cleaned.split(',')]
            return [cleaned] if cleaned else []
        return []


def clean_text_for_llm(text) -> str:
    """
    Normalize text for LLM processing:
    - Remove excessive whitespace
    - Fix encoding issues
    - Strip leading/trailing spaces
    - Handle empty/null values
    """
    if pd.isna(text) or text is None:
        return ""
    
    text = str(text).strip()
    
    # Fix common encoding issues
    text = text.replace('\xa0', ' ')  # non-breaking space
    text = text.replace('\u200b', '')  # zero-width space
    text = text.replace('\ufeff', '')  # BOM
    
    # Remove excessive whitespace (multiple spaces, tabs, newlines)
    text = re.sub(r'\s+', ' ', text)
    
    # Remove any remaining control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
    
    return text.strip()


def create_facility_context(row: pd.Series) -> str:
    """
    Create a comprehensive text context for each facility
    combining name, location, specialties, and content
    """
    parts = []
    
    # Facility name
    if pd.notna(row.get('name')):
        parts.append(f"Facility Name: {row['name']}")
    
    # Location
    if pd.notna(row.get('address_city')):
        city = row['address_city']
        region = row.get('region_norm', '')
        if region:
            parts.append(f"Location: {city}, {region}, Ghana")
        else:
            parts.append(f"Location: {city}, Ghana")
    elif pd.notna(row.get('region_norm')):
        parts.append(f"Location: {row['region_norm']}, Ghana")
    
    # Facility type
    if pd.notna(row.get('facility_type_simple')):
        parts.append(f"Type: {row['facility_type_simple']}")
    
    # Specialties
    if pd.notna(row.get('specialties_list')) and row['specialties_list']:
        if isinstance(row['specialties_list'], list):
            specs = ', '.join(row['specialties_list'][:5])  # limit to first 5
            parts.append(f"Specialties: {specs}")
    
    # Main content blob
    if pd.notna(row.get('_blob')) and row['_blob']:
        cleaned_blob = clean_text_for_llm(row['_blob'])
        if cleaned_blob:
            parts.append(f"\nDetails: {cleaned_blob}")
    
    return '\n'.join(parts)


def load_and_preprocess_data(force_reload: bool = False) -> pd.DataFrame:
    """
    Load the Ghana facility dataset and perform preprocessing
    VF-COMPLIANT: Parses all JSON columns (procedure, equipment, capability, specialties)
    
    Args:
        force_reload: If True, reload from raw CSV even if enriched exists
        
    Returns:
        Preprocessed DataFrame with all VF official fields
    """
    logger.info("Loading Ghana facility dataset...")
    
    # Try to load enriched version first
    if ENRICHED_DATA_FILE.exists() and not force_reload:
        logger.info(f"Loading enriched data from {ENRICHED_DATA_FILE}")
        df = pd.read_csv(ENRICHED_DATA_FILE)
        
        # Check if it has all necessary fields
        required_fields = ['row_id', 'facility_context']
        if all(field in df.columns for field in required_fields):
            logger.info(f"✅ Loaded {len(df):,} facilities with enriched fields")
            
            # Add _blob_clean if missing
            if '_blob_clean' not in df.columns and '_blob' in df.columns:
                df['_blob_clean'] = df['_blob'].apply(clean_text_for_llm)
                logger.info("✅ Added _blob_clean field")
            
            # Parse VF JSON columns
            json_columns = ['procedure', 'equipment', 'capability', 'specialties', 
                          'phone_numbers', 'websites', 'affiliationTypeIds']
            for col in json_columns:
                if col in df.columns and col not in [c for c in df.columns if c.endswith('_parsed')]:
                    df[f'{col}_parsed'] = df[col].apply(safe_parse_json_list)
                    logger.info(f"✅ Parsed {col} column")
            
            return df
        else:
            logger.warning("Enriched file missing fields, reprocessing...")
    
    # Load raw data
    logger.info(f"Loading raw data from {RAW_DATA_FILE}")
    df = pd.read_csv(RAW_DATA_FILE)
    
    logger.info(f"Loaded {len(df):,} facilities with {len(df.columns)} columns")
    
    # Add row_id
    if 'row_id' not in df.columns:
        df['row_id'] = df.index
        logger.info("✅ Added row_id column")
    
    # Clean _blob field for LLM
    if '_blob' in df.columns:
        df['_blob_clean'] = df['_blob'].apply(clean_text_for_llm)
        logger.info("✅ Applied LLM text normalization to _blob")
    
    # Create facility_context if not exists
    if 'facility_context' not in df.columns:
        df['facility_context'] = df.apply(create_facility_context, axis=1)
        logger.info("✅ Created facility_context field")
    
    # Save enriched version
    df.to_csv(ENRICHED_DATA_FILE, index=False)
    logger.info(f"✅ Saved enriched data to {ENRICHED_DATA_FILE}")
    
    return df


def get_facility_metadata(row: pd.Series) -> Dict:
    """
    Extract metadata from a facility row
    
    Returns:
        Dictionary with facility metadata for embedding storage
    """
    return {
        "facility_id": str(row.get('unique_id', '')),
        "facility_name": str(row.get('name', '')),
        "region": str(row.get('region_norm', '')),
        "city": str(row.get('address_city', '')),
        "facility_type": str(row.get('facility_type_simple', 'other')),
        "row_id": int(row.get('row_id', -1)),
        "source_url": str(row.get('source_url', '')),
    }


def extract_text_fields(row: pd.Series) -> Dict[str, str]:
    """
    Extract individual text fields for detailed analysis
    
    Returns:
        Dictionary with separated text fields
    """
    return {
        "specialties": str(row.get('specialties', '')),
        "procedure": str(row.get('procedure', '')),
        "equipment": str(row.get('equipment', '')),
        "capability": str(row.get('capability', '')),
        "description": str(row.get('description', '')),
        "_blob": str(row.get('_blob_clean', '')),
        "full_context": str(row.get('facility_context', '')),
    }


if __name__ == "__main__":
    # Test data loading
    df = load_and_preprocess_data()
    
    print(f"\n📊 Dataset Summary:")
    print(f"   - Total facilities: {len(df):,}")
    print(f"   - Total columns: {len(df.columns)}")
    
    # Check which columns exist
    if 'region_norm' in df.columns:
        print(f"   - Regions: {df['region_norm'].nunique()}")
    elif 'address_stateOrRegion' in df.columns:
        print(f"   - Regions: {df['address_stateOrRegion'].nunique()}")
    
    if 'facility_type_simple' in df.columns:
        print(f"   - Facility types: {df['facility_type_simple'].value_counts().to_dict()}")
    elif 'facilityTypeId' in df.columns:
        print(f"   - Facility types: {df['facilityTypeId'].value_counts().to_dict()}")
    
    # Show sample
    print(f"\n📄 Sample facility context:")
    print("="*80)
    sample = df[df['facility_context'].str.len() > 100].iloc[0]
    print(sample['facility_context'][:500])
    print("...")
