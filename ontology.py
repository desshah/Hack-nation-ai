"""
Medical capability ontology for healthcare facilities
Defines canonical capability names, dependencies, and categorization
"""
from typing import Dict, List, Set

# Canonical capability names and descriptions
CAPABILITY_ONTOLOGY = {
    # Emergency & Critical Care
    "emergency_care": "24/7 emergency department with trauma capability",
    "intensive_care": "ICU with ventilators and monitoring",
    "trauma_center": "Advanced trauma life support capability",
    "resuscitation": "Emergency resuscitation and life support",
    
    # Surgical Services
    "general_surgery": "General surgical procedures",
    "orthopedic_surgery": "Bone and joint surgery",
    "cesarean_section": "C-section delivery capability",
    "minor_surgery": "Minor surgical procedures and wound care",
    "operating_room": "Equipped operating theater",
    
    # Maternal & Child Health
    "maternity_delivery": "Normal delivery and birthing services",
    "prenatal_care": "Antenatal and pregnancy monitoring",
    "postnatal_care": "Postpartum care and monitoring",
    "family_planning": "Contraception and reproductive health",
    "child_immunization": "Childhood vaccination programs",
    "pediatric_care": "General pediatric services",
    "neonatal_care": "Newborn intensive care",
    
    # Diagnostics
    "laboratory_services": "Clinical laboratory testing",
    "xray": "X-ray imaging capability",
    "ultrasound": "Ultrasound imaging",
    "ct_scan": "CT scanning capability",
    "blood_bank": "Blood storage and transfusion",
    "pathology": "Tissue and disease diagnosis",
    
    # Chronic Disease Management
    "diabetes_care": "Diabetes management and monitoring",
    "hypertension_management": "Blood pressure management",
    "hiv_treatment": "HIV/AIDS treatment and monitoring",
    "tuberculosis_treatment": "TB diagnosis and treatment",
    "malaria_treatment": "Malaria diagnosis and treatment",
    
    # Specialized Services
    "dental_services": "Dental care and oral health",
    "eye_care": "Ophthalmology services",
    "mental_health": "Psychiatric and counseling services",
    "physiotherapy": "Physical rehabilitation",
    "dialysis": "Kidney dialysis services",
    "oncology": "Cancer treatment services",
    
    # Essential Infrastructure
    "pharmacy": "On-site pharmacy services",
    "oxygen_supply": "Medical oxygen availability",
    "ambulance_service": "Emergency transport",
    "sterilization": "Instrument sterilization capability",
    "electricity_backup": "Generator or backup power",
    "water_supply": "Clean water availability",
    
    # Outpatient Services
    "outpatient_consultation": "General outpatient visits",
    "vaccination": "Adult vaccination services",
    "health_screening": "Preventive health checks",
    "wound_care": "Wound dressing and management",
    
    # Additional Services
    "anesthesia": "Anesthesia services for surgery",
    "blood_transfusion": "Blood transfusion capability",
    "mortuary": "Morgue facilities",
    "medical_records": "Patient records system",
}

# Critical capabilities that every region should have access to
CRITICAL_CAPABILITIES = [
    "emergency_care",
    "maternity_delivery",
    "child_immunization",
    "laboratory_services",
    "pharmacy",
    "outpatient_consultation",
    "ambulance_service",
    "xray",
    "blood_bank"
]

# Dependencies between capabilities
CAPABILITY_DEPENDENCIES = {
    "emergency_care": ["laboratory_services", "xray", "oxygen_supply", "pharmacy"],
    "intensive_care": ["oxygen_supply", "laboratory_services", "pharmacy", "electricity_backup"],
    "general_surgery": ["operating_room", "anesthesia", "sterilization", "blood_bank", "pharmacy"],
    "cesarean_section": ["operating_room", "anesthesia", "blood_bank", "oxygen_supply"],
    "maternity_delivery": ["blood_bank", "oxygen_supply", "laboratory_services"],
    "neonatal_care": ["oxygen_supply", "laboratory_services", "pharmacy"],
    "blood_transfusion": ["blood_bank", "laboratory_services"],
    "dialysis": ["water_supply", "electricity_backup", "laboratory_services"],
    "trauma_center": ["emergency_care", "operating_room", "blood_bank", "xray"],
    "orthopedic_surgery": ["operating_room", "anesthesia", "xray"],
}

# Keywords indicating availability status
AVAILABILITY_KEYWORDS = {
    "permanent": ["24/7", "always", "full-time", "permanent", "continuous", "daily"],
    "intermittent": ["part-time", "scheduled", "certain days", "specific hours", "weekly"],
    "visiting": ["visiting", "mobile", "outreach", "consultant", "specialist visits"],
    "planned": ["under construction", "future", "planned", "proposed", "upcoming"],
    "unknown": ["available", "offers", "provides"]  # Default when no specific timing
}

# Keywords that indicate suspicious or unverified claims
SUSPICIOUS_KEYWORDS = [
    "allegedly", "supposedly", "claims to", "reported to", "said to",
    "unverified", "unconfirmed", "rumored", "possibly", "might have"
]


def normalize_capability(capability: str) -> str:
    """
    Normalize a capability name to its canonical form
    
    Args:
        capability: Raw capability name
        
    Returns:
        Normalized canonical name
    """
    # Convert to lowercase and replace common separators
    normalized = capability.lower().strip()
    normalized = normalized.replace("-", "_").replace(" ", "_")
    
    # Common aliases
    aliases = {
        "maternity": "maternity_delivery",
        "delivery": "maternity_delivery",
        "labour_ward": "maternity_delivery",
        "labor_ward": "maternity_delivery",
        "emergency": "emergency_care",
        "emergency_department": "emergency_care",
        "a&e": "emergency_care",
        "casualty": "emergency_care",
        "lab": "laboratory_services",
        "laboratory": "laboratory_services",
        "xray_services": "xray",
        "x_ray": "xray",
        "radiology": "xray",
        "ultrasound_services": "ultrasound",
        "pharmacy_services": "pharmacy",
        "dispensary": "pharmacy",
        "immunization": "child_immunization",
        "vaccination_services": "vaccination",
        "icu": "intensive_care",
        "critical_care": "intensive_care",
        "surgery": "general_surgery",
        "surgical_services": "general_surgery",
        "csection": "cesarean_section",
        "c_section": "cesarean_section",
        "antenatal": "prenatal_care",
        "anc": "prenatal_care",
        "postnatal": "postnatal_care",
        "pnc": "postnatal_care",
        "paediatric": "pediatric_care",
        "paediatrics": "pediatric_care",
        "pediatrics": "pediatric_care",
        "child_health": "pediatric_care",
    }
    
    return aliases.get(normalized, normalized)


def get_dependencies(capability: str) -> List[str]:
    """
    Get required dependencies for a capability
    
    Args:
        capability: Capability name (normalized)
        
    Returns:
        List of required capability dependencies
    """
    return CAPABILITY_DEPENDENCIES.get(capability, [])


def is_critical_capability(capability: str) -> bool:
    """
    Check if a capability is critical (should be available in every region)
    
    Args:
        capability: Capability name (normalized)
        
    Returns:
        True if capability is critical
    """
    return normalize_capability(capability) in CRITICAL_CAPABILITIES


def get_capability_category(capability: str) -> str:
    """
    Get the category of a capability
    
    Args:
        capability: Capability name
        
    Returns:
        Category name
    """
    emergency_critical = ["emergency_care", "intensive_care", "trauma_center", "resuscitation"]
    surgical = ["general_surgery", "orthopedic_surgery", "cesarean_section", "minor_surgery", "operating_room"]
    maternal_child = ["maternity_delivery", "prenatal_care", "postnatal_care", "family_planning", 
                      "child_immunization", "pediatric_care", "neonatal_care"]
    diagnostics = ["laboratory_services", "xray", "ultrasound", "ct_scan", "blood_bank", "pathology"]
    chronic = ["diabetes_care", "hypertension_management", "hiv_treatment", "tuberculosis_treatment", "malaria_treatment"]
    specialized = ["dental_services", "eye_care", "mental_health", "physiotherapy", "dialysis", "oncology"]
    infrastructure = ["pharmacy", "oxygen_supply", "ambulance_service", "sterilization", 
                     "electricity_backup", "water_supply"]
    outpatient = ["outpatient_consultation", "vaccination", "health_screening", "wound_care"]
    
    normalized = normalize_capability(capability)
    
    if normalized in emergency_critical:
        return "Emergency & Critical Care"
    elif normalized in surgical:
        return "Surgical Services"
    elif normalized in maternal_child:
        return "Maternal & Child Health"
    elif normalized in diagnostics:
        return "Diagnostics"
    elif normalized in chronic:
        return "Chronic Disease Management"
    elif normalized in specialized:
        return "Specialized Services"
    elif normalized in infrastructure:
        return "Essential Infrastructure"
    elif normalized in outpatient:
        return "Outpatient Services"
    else:
        return "Other Services"


def validate_capability_set(capabilities: List[str]) -> Dict[str, List[str]]:
    """
    Validate a set of capabilities and identify missing dependencies
    
    Args:
        capabilities: List of capability names
        
    Returns:
        Dictionary with 'valid', 'missing_dependencies', and 'unknown' capabilities
    """
    normalized_caps = {normalize_capability(c) for c in capabilities}
    missing_deps = set()
    unknown = set()
    
    for cap in capabilities:
        norm_cap = normalize_capability(cap)
        
        # Check if capability is known
        if norm_cap not in CAPABILITY_ONTOLOGY:
            unknown.add(cap)
            continue
            
        # Check dependencies
        deps = get_dependencies(norm_cap)
        for dep in deps:
            if dep not in normalized_caps:
                missing_deps.add(dep)
    
    return {
        "valid": list(normalized_caps - unknown),
        "missing_dependencies": list(missing_deps),
        "unknown": list(unknown)
    }
