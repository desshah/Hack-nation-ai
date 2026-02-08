"""
Capability Extractor - Orchestrates retrieval and extraction for facility capabilities
"""
import json
from typing import List, Dict, Optional
from groq import Groq
from schemas import ExtractedCapability, FacilityWithCapabilities
from retriever import Retriever
from extractor_agent import ExtractionAgent
from ontology import CRITICAL_CAPABILITIES, normalize_capability
from config import GROQ_API_KEY, MODEL_CONFIG
import pandas as pd

class CapabilityExtractor:
    """
    Orchestrates the full capability extraction pipeline:
    1. Retrieval: Find relevant facilities for a query
    2. Extraction: Extract structured capabilities from each facility
    3. Normalization: Map to standard ontology
    4. Aggregation: Combine results
    """
    
    def __init__(self, retriever: Retriever, facilities_df: pd.DataFrame):
        self.retriever = retriever
        self.extractor = ExtractionAgent(api_key=GROQ_API_KEY)
        self.facilities_df = facilities_df
        
    def extract_for_query(self, query: str, top_k: int = 10) -> List[FacilityWithCapabilities]:
        """
        Extract capabilities for facilities matching the query
        
        Args:
            query: Natural language query (e.g., "facilities with maternity services")
            top_k: Number of facilities to retrieve
            
        Returns:
            List of FacilityWithCapabilities objects
        """
        # Step 1: Retrieve relevant facilities
        results = self.retriever.search(query, top_k=top_k)
        
        extracted_facilities = []
        
        for result in results:
            facility_id = result['metadata']['facility_id']
            
            # Get full facility data
            facility_row = self.facilities_df[
                self.facilities_df['row_id'] == facility_id
            ].iloc[0]
            
            # Step 2: Extract capabilities
            capabilities = self.extractor.extract_capabilities(
                facility_context=result['text'],
                facility_id=facility_id,
                facility_name=result['metadata']['facility_name'],
                region=result['metadata']['region'],
                source_row_id=facility_id
            )
            
            # Step 3: Create FacilityWithCapabilities object
            facility_with_caps = FacilityWithCapabilities(
                facility_id=facility_id,
                facility_name=result['metadata']['facility_name'],
                region=result['metadata']['region'],
                district=facility_row.get('district', ''),
                ownership=facility_row.get('ownership', ''),
                facility_type=facility_row.get('facility_type', ''),
                capabilities=capabilities,
                raw_data=result['text']
            )
            
            extracted_facilities.append(facility_with_caps)
        
        return extracted_facilities
    
    def extract_critical_capabilities(self, region: Optional[str] = None) -> Dict[str, List[FacilityWithCapabilities]]:
        """
        Extract all critical capabilities across regions
        
        Args:
            region: Optional filter by region
            
        Returns:
            Dictionary mapping capability to list of facilities offering it
        """
        capability_map = {cap: [] for cap in CRITICAL_CAPABILITIES}
        
        for capability in CRITICAL_CAPABILITIES:
            query = f"facilities offering {capability.replace('_', ' ')}"
            facilities = self.extract_for_query(query, top_k=20)
            
            # Filter by region if specified
            if region:
                facilities = [f for f in facilities if f.region == region]
            
            # Filter facilities that actually have this capability
            filtered_facilities = []
            for facility in facilities:
                has_capability = any(
                    normalize_capability(cap.capability) == capability
                    for cap in facility.capabilities
                )
                if has_capability:
                    filtered_facilities.append(facility)
            
            capability_map[capability] = filtered_facilities
        
        return capability_map
    
    def save_extractions(self, facilities: List[FacilityWithCapabilities], output_path: str):
        """Save extracted capabilities to JSON"""
        output = [
            {
                'facility_id': f.facility_id,
                'facility_name': f.facility_name,
                'region': f.region,
                'district': f.district,
                'ownership': f.ownership,
                'facility_type': f.facility_type,
                'capabilities': [
                    {
                        'capability': cap.capability,
                        'evidence': cap.evidence,
                        'confidence': cap.confidence,
                        'availability': cap.availability,
                        'dependencies': cap.dependencies,
                        'flags': cap.flags
                    }
                    for cap in f.capabilities
                ]
            }
            for f in facilities
        ]
        
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"Saved {len(facilities)} facility extractions to {output_path}")


if __name__ == "__main__":
    # Example usage
    from data_loader import load_and_preprocess_data
    
    print("Loading facilities data...")
    facilities_df = load_and_preprocess_data()
    
    print("Initializing retriever...")
    retriever = Retriever(db_path="vector_db")
    
    print("Creating capability extractor...")
    extractor = CapabilityExtractor(retriever, facilities_df)
    
    # Test query
    print("\nTest Query: 'emergency care facilities'")
    results = extractor.extract_for_query("emergency care facilities", top_k=5)
    
    print(f"\nFound {len(results)} facilities:")
    for facility in results:
        print(f"\n{facility.facility_name} ({facility.region})")
        print(f"  Capabilities: {len(facility.capabilities)}")
        for cap in facility.capabilities[:3]:  # Show first 3
            print(f"    - {cap.capability} (confidence: {cap.confidence:.2f})")
    
    # Save results
    extractor.save_extractions(results, "output/test_extractions.json")
