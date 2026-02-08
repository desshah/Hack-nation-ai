"""
Capability extraction agent using Groq LLM
Extracts structured medical capabilities from facility text
"""
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import hashlib

from groq import Groq

from config import GROQ_API_KEY, GROQ_PRIMARY_MODEL, TEMPERATURE_EXTRACTION
from schemas import ExtractedCapability
from ontology import (
    normalize_capability,
    get_dependencies,
    is_critical_capability,
    CAPABILITY_ONTOLOGY,
    AVAILABILITY_KEYWORDS,
    SUSPICIOUS_KEYWORDS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CapabilityExtractor:
    """Extract medical capabilities from facility text using Groq LLM"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize the extractor
        
        Args:
            api_key: Groq API key
            model: Groq model name
        """
        self.api_key = api_key or GROQ_API_KEY
        self.model = model or GROQ_PRIMARY_MODEL
        self.client = Groq(api_key=self.api_key)
        
        logger.info(f"Initialized CapabilityExtractor with model: {self.model}")
    
    def create_extraction_prompt(self, facility_text: str, facility_name: str) -> str:
        """
        Create prompt for capability extraction
        
        Args:
            facility_text: Facility context text
            facility_name: Name of facility
            
        Returns:
            Formatted prompt
        """
        capabilities_list = "\n".join([f"- {k}: {v}" for k, v in list(CAPABILITY_ONTOLOGY.items())[:30]])
        
        prompt = f"""You are a medical facility capability extraction expert. Extract ALL medical capabilities from the facility information below.

FACILITY: {facility_name}

FACILITY INFORMATION:
{facility_text}

TASK: Extract medical capabilities and output as JSON array. For each capability found:

1. **capability**: Use EXACT canonical name from ontology (see list below)
2. **evidence**: List of direct quotes from text supporting this capability
3. **confidence**: 
   - 1.0 = Explicitly stated with details
   - 0.7 = Clearly implied
   - 0.4 = Vague mention
   - 0.2 = Suspicious/unverified claim
4. **availability**: Determine from keywords:
   - "permanent" = 24/7, always available, full-time
   - "intermittent" = part-time, scheduled, certain days
   - "visiting" = visiting doctor/consultant, mobile, outreach
   - "planned" = under construction, future, planned
   - "unknown" = not specified
5. **dependencies**: List required capabilities (e.g., surgery needs: operating_room, anesthesia, sterilization)
6. **flags**: Add if applicable:
   - "suspicious" = unverified claims, vague statements
   - "incomplete" = missing key details
   - "contradictory" = conflicts with other information
   - "unverified" = no concrete evidence

CANONICAL CAPABILITIES (use these exact names):
{capabilities_list}
... (60+ total capabilities available)

IMPORTANT RULES:
- Only extract capabilities with clear evidence
- Use canonical names EXACTLY as shown
- Be conservative with confidence scores
- Check for availability patterns in text
- Flag suspicious or incomplete claims
- Infer logical dependencies

OUTPUT FORMAT:
```json
[
  {{
    "capability": "emergency_care",
    "evidence": ["Provides 24/7 emergency services", "Has dedicated emergency department"],
    "confidence": 1.0,
    "availability": "permanent",
    "dependencies": ["laboratory_services", "xray", "oxygen_supply", "pharmacy"],
    "flags": []
  }},
  {{
    "capability": "maternity_delivery",
    "evidence": ["Offers maternity services", "delivery room available"],
    "confidence": 0.7,
    "availability": "permanent",
    "dependencies": ["blood_bank", "oxygen_supply"],
    "flags": ["incomplete"]
  }}
]
```

Extract ALL capabilities found. Return ONLY the JSON array, no other text."""
        
        return prompt
    
    def extract_capabilities(
        self,
        facility_text: str,
        facility_metadata: Dict
    ) -> List[ExtractedCapability]:
        """
        Extract capabilities from facility text
        
        Args:
            facility_text: Facility context text
            facility_metadata: Facility metadata (id, name, region, etc.)
            
        Returns:
            List of ExtractedCapability objects
        """
        facility_name = facility_metadata.get('facility_name', 'Unknown')
        
        logger.info(f"Extracting capabilities for: {facility_name}")
        
        # Create prompt
        prompt = self.create_extraction_prompt(facility_text, facility_name)
        
        # Call Groq API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical facility capability extraction expert. Output only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=TEMPERATURE_EXTRACTION,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Try to extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            capabilities_data = json.loads(content)
            
            # Handle if wrapped in object
            if isinstance(capabilities_data, dict):
                if 'capabilities' in capabilities_data:
                    capabilities_data = capabilities_data['capabilities']
                else:
                    capabilities_data = list(capabilities_data.values())[0]
            
            # Create ExtractedCapability objects
            capabilities = []
            chunk_id = hashlib.md5(facility_text.encode()).hexdigest()[:16]
            timestamp = datetime.now().isoformat()
            
            for cap_data in capabilities_data:
                # Normalize capability name
                cap_name = cap_data.get('capability', '')
                normalized_name = normalize_capability(cap_name)
                
                # If not in ontology, use original but flag it
                if normalized_name not in CAPABILITY_ONTOLOGY and cap_name not in CAPABILITY_ONTOLOGY:
                    normalized_name = cap_name
                    cap_data.setdefault('flags', []).append('unverified')
                
                # Auto-add dependencies if not provided
                if not cap_data.get('dependencies'):
                    cap_data['dependencies'] = get_dependencies(normalized_name)
                
                # Create capability object
                capability = ExtractedCapability(
                    capability=normalized_name,
                    evidence=cap_data.get('evidence', []),
                    confidence=cap_data.get('confidence', 0.5),
                    availability=cap_data.get('availability', 'unknown'),
                    dependencies=cap_data.get('dependencies', []),
                    flags=cap_data.get('flags', []),
                    facility_id=facility_metadata.get('facility_id', ''),
                    facility_name=facility_name,
                    region=facility_metadata.get('region', ''),
                    source_row_id=facility_metadata.get('row_id', -1),
                    chunk_id=chunk_id,
                    extraction_timestamp=timestamp
                )
                
                capabilities.append(capability)
            
            logger.info(f"  Extracted {len(capabilities)} capabilities")
            return capabilities
            
        except Exception as e:
            logger.error(f"  Error extracting capabilities: {e}")
            return []
    
    def extract_batch(
        self,
        facilities: List[Dict]
    ) -> Dict[str, List[ExtractedCapability]]:
        """
        Extract capabilities for multiple facilities
        
        Args:
            facilities: List of facility dictionaries with 'text' and metadata
            
        Returns:
            Dictionary mapping facility_id to list of capabilities
        """
        results = {}
        
        for i, facility in enumerate(facilities, 1):
            logger.info(f"Processing facility {i}/{len(facilities)}")
            
            text = facility.get('text', '')
            metadata = {k: v for k, v in facility.items() if k != 'text'}
            
            capabilities = self.extract_capabilities(text, metadata)
            facility_id = metadata.get('facility_id', f'facility_{i}')
            results[facility_id] = capabilities
        
        return results


if __name__ == "__main__":
    # Test extraction
    from data_loader import load_and_preprocess_data, get_facility_metadata, extract_text_fields
    
    # Load data
    df = load_and_preprocess_data()
    
    # Test on first facility
    sample = df.iloc[0]
    metadata = get_facility_metadata(sample)
    text = sample.get('facility_context', '')
    
    print(f"Testing extraction on: {metadata['facility_name']}\n")
    print(f"Text preview:\n{text[:300]}...\n")
    
    # Extract
    extractor = CapabilityExtractor()
    capabilities = extractor.extract_capabilities(text, metadata)
    
    print(f"\nExtracted {len(capabilities)} capabilities:")
    for cap in capabilities[:5]:
        print(f"\n  • {cap.capability}")
        print(f"    Confidence: {cap.confidence}")
        print(f"    Availability: {cap.availability}")
        print(f"    Evidence: {cap.evidence[0][:100] if cap.evidence else 'None'}...")
        if cap.flags:
            print(f"    Flags: {cap.flags}")


# Alias for backward compatibility
ExtractionAgent = CapabilityExtractor
