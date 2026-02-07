"""
Medical capability ontology and synonym mappings
Defines canonical medical capabilities and their variations
"""

# Critical capabilities that define medical deserts when missing
CRITICAL_CAPABILITIES = [
    "emergency_care",
    "maternity_delivery",
    "basic_surgery",
    "blood_transfusion",
    "pediatric_care",
    "intensive_care_unit",
    "pharmacy",
    "laboratory_services",
    "ambulance_service",
]

# Comprehensive capability ontology (canonical names)
CAPABILITY_ONTOLOGY = {
    # Emergency & Critical Care
    "emergency_care": "24/7 Emergency Medical Services",
    "intensive_care_unit": "Intensive Care Unit (ICU)",
    "critical_care": "Critical Care Services",
    "trauma_center": "Trauma Center",
    "ambulance_service": "Ambulance/Emergency Transport",
    "burn_unit": "Burn Unit",
    
    # Surgical Services
    "basic_surgery": "Basic Surgical Services",
    "major_surgery": "Major Surgery (complex operations)",
    "cesarean_section": "Cesarean Section (C-section)",
    "orthopedic_surgery": "Orthopedic Surgery",
    "cardiac_surgery": "Cardiac Surgery",
    "neurosurgery": "Neurosurgery",
    "ophthalmic_surgery": "Eye Surgery/Ophthalmic Surgery",
    "dental_surgery": "Dental Surgery",
    "plastic_surgery": "Plastic Surgery",
    "laparoscopic_surgery": "Minimally Invasive/Laparoscopic Surgery",
    
    # Maternal & Child Health
    "maternity_delivery": "Maternity/Childbirth Delivery Services",
    "prenatal_care": "Prenatal/Antenatal Care",
    "postnatal_care": "Postnatal Care",
    "neonatal_intensive_care": "Neonatal ICU (NICU)",
    "pediatric_care": "Pediatric Care",
    "pediatric_intensive_care": "Pediatric ICU (PICU)",
    "immunization": "Immunization/Vaccination Services",
    "family_planning": "Family Planning Services",
    
    # Diagnostics & Imaging
    "laboratory_services": "Laboratory/Pathology Services",
    "xray": "X-ray/Radiography",
    "ultrasound": "Ultrasound/Sonography",
    "ct_scan": "CT Scan (Computed Tomography)",
    "mri": "MRI (Magnetic Resonance Imaging)",
    "ecg": "ECG/EKG (Electrocardiogram)",
    "blood_testing": "Blood Testing Services",
    "microbiology": "Microbiology Testing",
    
    # Specialty Care
    "cardiology": "Cardiology Services",
    "oncology": "Cancer/Oncology Services",
    "chemotherapy": "Chemotherapy",
    "radiotherapy": "Radiotherapy/Radiation Therapy",
    "dialysis": "Dialysis/Renal Services",
    "hiv_aids_care": "HIV/AIDS Treatment & Care",
    "tuberculosis_care": "Tuberculosis (TB) Treatment",
    "malaria_treatment": "Malaria Treatment",
    "mental_health": "Mental Health/Psychiatric Services",
    "ophthalmology": "Eye Care/Ophthalmology",
    "dentistry": "Dental Services",
    "dermatology": "Dermatology/Skin Care",
    
    # Support Services
    "pharmacy": "Pharmacy Services",
    "blood_bank": "Blood Bank/Blood Storage",
    "oxygen_supply": "Oxygen Supply/Generation",
    "operating_room": "Operating Room/Theatre",
    "sterilization": "Sterilization Services",
    "anesthesia": "Anesthesia Services",
    "physiotherapy": "Physiotherapy/Rehabilitation",
    "nutrition": "Nutrition/Dietary Services",
    
    # General Services
    "outpatient_care": "Outpatient Services",
    "inpatient_care": "Inpatient/Hospital Admission",
    "consultation": "General Medical Consultation",
    "health_screening": "Health Screening/Check-ups",
    "telemedicine": "Telemedicine/Virtual Consultation",
}

# Synonym mappings: variations → canonical name
CAPABILITY_SYNONYMS = {
    # Emergency
    "emergency": "emergency_care",
    "er": "emergency_care",
    "ed": "emergency_care",
    "a&e": "emergency_care",
    "casualty": "emergency_care",
    "24/7 emergency": "emergency_care",
    "accident emergency": "emergency_care",
    
    # ICU
    "icu": "intensive_care_unit",
    "intensive care": "intensive_care_unit",
    "critical care unit": "intensive_care_unit",
    "nicu": "neonatal_intensive_care",
    "picu": "pediatric_intensive_care",
    
    # Surgery
    "surgery": "basic_surgery",
    "surgical": "basic_surgery",
    "operation": "basic_surgery",
    "or": "operating_room",
    "theatre": "operating_room",
    "c-section": "cesarean_section",
    "csection": "cesarean_section",
    "caesarean": "cesarean_section",
    
    # Maternity
    "maternity": "maternity_delivery",
    "delivery": "maternity_delivery",
    "childbirth": "maternity_delivery",
    "obstetrics": "maternity_delivery",
    "antenatal": "prenatal_care",
    "postnatal": "postnatal_care",
    
    # Imaging
    "x-ray": "xray",
    "xray": "xray",
    "radiography": "xray",
    "roentgen": "xray",
    "x ray": "xray",
    "ultrasound": "ultrasound",
    "sonography": "ultrasound",
    "echo": "ultrasound",
    "us": "ultrasound",
    "u/s": "ultrasound",
    "ct": "ct_scan",
    "cat scan": "ct_scan",
    "computed tomography": "ct_scan",
    "mri": "mri",
    "magnetic resonance": "mri",
    
    # Lab
    "laboratory": "laboratory_services",
    "lab": "laboratory_services",
    "pathology": "laboratory_services",
    "blood test": "blood_testing",
    "blood work": "blood_testing",
    
    # Cardiology
    "ekg": "ecg",
    "electrocardiogram": "ecg",
    "heart monitor": "ecg",
    
    # Other
    "pharmacy": "pharmacy",
    "dispensary": "pharmacy",
    "blood bank": "blood_bank",
    "oxygen": "oxygen_supply",
    "o2": "oxygen_supply",
    "rehab": "physiotherapy",
    "physical therapy": "physiotherapy",
    "pt": "physiotherapy",
    "hiv": "hiv_aids_care",
    "aids": "hiv_aids_care",
    "tb": "tuberculosis_care",
    "cancer": "oncology",
    "chemo": "chemotherapy",
    "radiation": "radiotherapy",
    "kidney": "dialysis",
    "renal": "dialysis",
    "hemodialysis": "dialysis",
    "mental": "mental_health",
    "psychiatric": "mental_health",
    "psych": "mental_health",
    "eye": "ophthalmology",
    "vision": "ophthalmology",
    "dental": "dentistry",
    "teeth": "dentistry",
    "pediatric": "pediatric_care",
    "paediatric": "pediatric_care",
    "children": "pediatric_care",
    "child": "pediatric_care",
    "vaccine": "immunization",
    "vaccination": "immunization",
    "immunization": "immunization",
}

# Required dependencies: capability → list of required capabilities
CAPABILITY_DEPENDENCIES = {
    "basic_surgery": ["operating_room", "anesthesia", "sterilization"],
    "major_surgery": ["operating_room", "anesthesia", "sterilization", "intensive_care_unit", "blood_bank"],
    "cesarean_section": ["operating_room", "anesthesia", "sterilization", "blood_bank"],
    "cardiac_surgery": ["operating_room", "anesthesia", "intensive_care_unit", "blood_bank", "ecg"],
    "neurosurgery": ["operating_room", "anesthesia", "intensive_care_unit", "ct_scan"],
    "orthopedic_surgery": ["operating_room", "anesthesia", "xray"],
    "ophthalmic_surgery": ["operating_room", "anesthesia"],
    "dental_surgery": ["operating_room", "anesthesia"],
    
    "intensive_care_unit": ["oxygen_supply", "pharmacy"],
    "neonatal_intensive_care": ["oxygen_supply", "pharmacy"],
    "pediatric_intensive_care": ["oxygen_supply", "pharmacy"],
    
    "maternity_delivery": ["blood_bank", "oxygen_supply"],
    "emergency_care": ["laboratory_services", "xray", "oxygen_supply", "pharmacy"],
    "trauma_center": ["emergency_care", "blood_bank", "operating_room", "intensive_care_unit"],
    
    "chemotherapy": ["pharmacy", "laboratory_services"],
    "dialysis": ["laboratory_services", "pharmacy"],
    
    "blood_transfusion": ["blood_bank", "laboratory_services"],
}

# Keywords indicating availability patterns
AVAILABILITY_KEYWORDS = {
    "permanent": [
        "24/7", "24 hours", "always open", "round the clock",
        "daily", "every day", "full time", "permanent"
    ],
    "intermittent": [
        "part time", "certain days", "scheduled", "weekly",
        "monthly", "occasional", "periodic"
    ],
    "visiting": [
        "visiting", "visiting consultant", "visiting doctor",
        "visiting specialist", "mobile", "outreach", "camp"
    ],
    "planned": [
        "planned", "upcoming", "will be", "to be established",
        "under construction", "future"
    ],
}

# Keywords indicating suspicious/low confidence claims
SUSPICIOUS_KEYWORDS = [
    "may have", "might have", "possibly", "potentially",
    "unclear", "unverified", "needs confirmation",
    "reported to have", "claims to", "allegedly"
]


def normalize_capability(text: str) -> str:
    """
    Normalize a capability text to its canonical form
    
    Args:
        text: Raw capability text
        
    Returns:
        Canonical capability name or original text if no match
    """
    if not text:
        return ""
    
    text_lower = text.lower().strip()
    
    # Direct match in synonyms
    if text_lower in CAPABILITY_SYNONYMS:
        return CAPABILITY_SYNONYMS[text_lower]
    
    # Partial match
    for synonym, canonical in CAPABILITY_SYNONYMS.items():
        if synonym in text_lower or text_lower in synonym:
            return canonical
    
    # Return original if no match (for manual review)
    return text


def get_dependencies(capability: str) -> list:
    """
    Get required dependencies for a capability
    
    Args:
        capability: Canonical capability name
        
    Returns:
        List of required capability names
    """
    return CAPABILITY_DEPENDENCIES.get(capability, [])


def is_critical_capability(capability: str) -> bool:
    """
    Check if a capability is critical (defines medical desert)
    
    Args:
        capability: Canonical capability name
        
    Returns:
        True if critical
    """
    return capability in CRITICAL_CAPABILITIES
