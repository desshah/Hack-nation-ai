"""
VF-COMPLIANT Capability extraction agent using Groq LLM
Extracts structured medical capabilities using official VF 3-category format:
- procedure: Clinical interventions
- equipment: Physical devices  
- capability: Care levels and programs
"""
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import hashlib

from groq import Groq

from config import GROQ_API_KEY, GROQ_PRIMARY_MODEL, TEMPERATURE_EXTRACTION
from schemas import ExtractedCapability, FacilityFacts
from ontology import (
    normalize_capability,
    get_dependencies,
    is_critical_capability,
    CAPABILITY_ONTOLOGY,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# VF OFFICIAL FREE_FORM_SYSTEM_PROMPT
FREE_FORM_SYSTEM_PROMPT = """
ROLE
You are a specialized medical facility information extractor. Your task is to analyze content to extract structured facts about healthcare facilities.

TASK OVERVIEW
Extract verifiable facts about this medical facility: `{organization}` from provided content and output in structured JSON format.

CATEGORY DEFINITIONS (VF Official):
- **procedure**
  - Clinical procedures, surgical operations, and medical interventions performed at the facility
  - Include specific medical procedures and treatments
  - Mention surgical services and specialties
  - List diagnostic procedures and screenings
  - Examples: "Performs emergency cesarean sections", "Conducts minimally invasive cardiac surgery"

- **equipment**
  - Physical medical devices, diagnostic machines, infrastructure, and utilities
  - Medical imaging equipment (MRI, CT, X-ray, ultrasound)
  - Surgical equipment and operating room technology
  - Infrastructure (beds, rooms, buildings, backup power)
  - Laboratory equipment and diagnostic tools
  - Examples: "Has Siemens SOMATOM Force CT scanner", "Operates 8 surgical theaters"

- **capability**
  - Medical capabilities defining what level and types of clinical care the facility can deliver
  - Trauma/emergency care levels (e.g., "Level I trauma center", "24/7 emergency care")
  - Specialized medical units (ICU, NICU, burn unit, stroke unit, cardiac care unit)
  - Clinical programs (stroke care program, IVF program, cancer center)
  - Diagnostic capabilities (MRI services, neurodiagnostics, pulmonary function testing)
  - Clinical accreditations and certifications (e.g., "Joint Commission accredited")
  - Care setting (inpatient, outpatient, or both)
  - Staffing levels and patient capacity/volume
  - DO NOT include: addresses, contact info, business hours, pricing
  - Examples: "Level II trauma center", "Joint Commission accredited", "Has 15 neonatal specialists"

EXTRACTION GUIDELINES (VF Official):
- Content Analysis Rules:
  - Only extract facts directly supported by the provided content
  - Be conservative: If attribution is uncertain, exclude it
  - Include a fact only if evidence explicitly names {organization}
  - If multiple facilities mentioned, ignore all others - NO cross-facility contamination
  - Each fact must be traceable to the input content

- Fact Format Requirements:
  - Use clear, declarative statements in plain English
  - Include specific quantities when available (e.g., "Has 12 ICU beds")
  - State facts in present tense unless historical context is needed
  - Each fact should be self-contained and understandable without context
  - No generic statements that could apply to any facility
  - Remove duplicate information across categories

CRITICAL REQUIREMENTS (VF Official):
- All arrays can be empty if no relevant facts are found
- Do NOT infer missing details
- Do NOT paraphrase into new facts
- Do NOT fill gaps with assumptions
- Each fact must explicitly name or clearly reference {organization}

OUTPUT FORMAT:
```json
{{
  "procedure": [
    "Performs emergency cesarean sections",
    "Conducts minimally invasive cardiac surgery",
    "Offers hemodialysis treatment 3 times weekly"
  ],
  "equipment": [
    "Operates 8 surgical theaters with laminar flow",
    "Has Siemens SOMATOM Force dual-source CT scanner",
    "Maintains 45-bed intensive care unit"
  ],
  "capability": [
    "Level II trauma center",
    "Level III NICU",
    "Joint Commission accredited",
    "Offers inpatient and outpatient services"
  ]
}}
```
"""


class CapabilityExtractorVF:
    """
    VF-COMPLIANT: Extract medical capabilities using official 3-category format
    """
    
    def __init__(self, model_name: str = GROQ_PRIMARY_MODEL):
        """Initialize with Groq LLM"""
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model_name = model_name
        logger.info(f"Initialized VF-Compliant CapabilityExtractor with model: {model_name}")
    
    def extract_facility_facts(
        self,
        facility_context: str,
        facility_name: str,
        **kwargs
    ) -> FacilityFacts:
        """
        Extract facts using VF official 3-category format
        
        Args:
            facility_context: Text content about the facility
            facility_name: Official facility name for attribution
            
        Returns:
            FacilityFacts with procedure, equipment, capability lists
        """
        try:
            # Build VF-compliant prompt
            prompt = FREE_FORM_SYSTEM_PROMPT.format(organization=facility_name)
            
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"FACILITY CONTENT:\n{facility_context}\n\nExtract procedure, equipment, and capability facts as JSON."}
            ]
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=TEMPERATURE_EXTRACTION,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            # Create VF FacilityFacts object
            facts = FacilityFacts(
                procedure=parsed.get('procedure', []),
                equipment=parsed.get('equipment', []),
                capability=parsed.get('capability', [])
            )
            
            return facts
            
        except Exception as e:
            logger.error(f"Error extracting facility facts: {e}")
            return FacilityFacts(procedure=[], equipment=[], capability=[])
    
    def extract_capabilities_detailed(
        self,
        facility_context: str,
        facility_id: str,
        facility_name: str,
        region: str = "",
        source_row_id: int = 0
    ) -> List[ExtractedCapability]:
        """
        Extract detailed capabilities with evidence and trust scoring
        Converts VF 3-category format to our detailed ExtractedCapability format
        
        Args:
            facility_context: Text content about the facility
            facility_id: Facility identifier
            facility_name: Official facility name
            region: Geographic region
            source_row_id: Source data row ID
            
        Returns:
            List of ExtractedCapability objects with evidence and scoring
        """
        # First get VF 3-category extraction
        facts = self.extract_facility_facts(facility_context, facility_name)
        
        capabilities = []
        
        # Process capability category (highest confidence)
        for cap_text in facts.capability or []:
            normalized = normalize_capability(cap_text)
            
            # Find evidence in context
            evidence = [cap_text]
            if cap_text.lower() in facility_context.lower():
                # Extract surrounding context as evidence
                idx = facility_context.lower().find(cap_text.lower())
                if idx >= 0:
                    start = max(0, idx - 50)
                    end = min(len(facility_context), idx + len(cap_text) + 50)
                    evidence.append(facility_context[start:end].strip())
            
            capabilities.append(ExtractedCapability(
                capability=normalized,
                evidence=evidence,
                confidence=1.0 if normalized in CAPABILITY_ONTOLOGY else 0.8,
                availability="available",
                dependencies=get_dependencies(normalized),
                flags=[],
                vf_category="capability"
            ))
        
        # Process procedure category (medium-high confidence)
        for proc_text in facts.procedure or []:
            normalized = normalize_capability(proc_text)
            
            capabilities.append(ExtractedCapability(
                capability=normalized,
                evidence=[proc_text],
                confidence=0.9,
                availability="available",
                dependencies=get_dependencies(normalized),
                flags=[],
                vf_category="procedure"
            ))
        
        # Process equipment category (medium confidence)
        for equip_text in facts.equipment or []:
            normalized = normalize_capability(equip_text)
            
            capabilities.append(ExtractedCapability(
                capability=normalized,
                evidence=[equip_text],
                confidence=0.8,
                availability="available",
                dependencies=[],
                flags=[],
                vf_category="equipment"
            ))
        
        return capabilities


# Backward compatibility alias
CapabilityExtractor = CapabilityExtractorVF
ExtractionAgent = CapabilityExtractorVF
