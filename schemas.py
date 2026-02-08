"""
VF-Compliant Pydantic schemas for facility data and capability extraction
Aligned with official Virtue Foundation specifications
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# VF OFFICIAL BASE SCHEMA (from facility_and_ngo_fields.py)
# ============================================================================

class BaseOrganization(BaseModel):
    """
    Base model containing shared fields between Facility and NGO.
    Official VF specification from facility_and_ngo_fields.py
    """
    model_config = ConfigDict(protected_namespaces=())
    
    name: str = Field(..., description="Official name of the organization")
    phone_numbers: Optional[List[str]] = Field(
        None,
        description="The organization's phone numbers in E164 format (e.g. '+233392022664')",
    )
    officialPhone: Optional[str] = Field(
        None,
        description="Official phone number associated with the organization in E164 format",
    )
    email: Optional[str] = Field(None, description="The organization's primary email address")
    websites: Optional[List[str]] = Field(
        None, description="Websites associated with the organization"
    )
    officialWebsite: Optional[str] = Field(
        None, description="Official website associated with the organization"
    )
    yearEstablished: Optional[int] = Field(
        None, description="The year in which the organization was established"
    )
    acceptsVolunteers: Optional[bool] = Field(
        None, description="Indicates whether the organization accepts clinical volunteers"
    )
    facebookLink: Optional[str] = Field(None, description="URL to the organization's Facebook page")
    twitterLink: Optional[str] = Field(
        None, description="URL to the organization's Twitter profile"
    )
    linkedinLink: Optional[str] = Field(None, description="URL to the organization's LinkedIn page")
    instagramLink: Optional[str] = Field(
        None, description="URL to the organization's Instagram account"
    )
    logo: Optional[str] = Field(None, description="URL linking to the organization's logo image")

    # Flattened address fields (VF official structure)
    address_line1: Optional[str] = Field(
        None,
        description="Street address only (building number, street name). Do NOT include city, state, or country.",
    )
    address_line2: Optional[str] = Field(
        None, description="Additional street address information (apartment, suite, building name)"
    )
    address_line3: Optional[str] = Field(None, description="Third line of street address if needed")
    address_city: Optional[str] = Field(
        None,
        description="City or town name of the organization.",
    )
    address_stateOrRegion: Optional[str] = Field(
        None,
        description="State, region, or province of the organization.",
    )
    address_zipOrPostcode: Optional[str] = Field(
        None, description="ZIP or postal code of the organization"
    )
    address_country: Optional[str] = Field(
        None,
        description="Full country name of the organization.",
    )
    address_countryCode: Optional[str] = Field(
        None,
        description="ISO alpha-2 country code of the organization.",
    )


class VFFacility(BaseOrganization):
    """
    Official VF Facility schema from facility_and_ngo_fields.py
    Extends BaseOrganization with facility-specific fields
    """
    
    facilityTypeId: Optional[Literal["hospital", "pharmacy", "doctor", "clinic", "dentist"]] = Field(
        None, description="Type of facility (only one of these values)"
    )
    operatorTypeId: Optional[Literal["public", "private"]] = Field(
        None, description="Indicates if the facility is privately or publicly operated"
    )
    affiliationTypeIds: Optional[
        List[Literal["faith-tradition", "philanthropy-legacy", "community", "academic", "government"]]
    ] = Field(None, description="Indicates facility affiliations")
    description: Optional[str] = Field(
        None, description="A brief paragraph describing the facility's services and/or history"
    )
    area: Optional[int] = Field(
        None, description="Total floor area of the facility in square meters"
    )
    numberDoctors: Optional[int] = Field(
        None, description="Total number of medical doctors working at the facility"
    )
    capacity: Optional[int] = Field(
        None, description="Overall inpatient bed capacity of the facility"
    )


# ============================================================================
# VF OFFICIAL FREE-FORM EXTRACTION (from free_form.py)
# ============================================================================

class FacilityFacts(BaseModel):
    """
    Official VF free-form extraction schema from free_form.py
    Separates procedure, equipment, and capability as per VF specification
    """
    model_config = ConfigDict(protected_namespaces=())
    
    procedure: Optional[List[str]] = Field(
        default=[],
        description=(
            "Specific clinical services performed at the facility—medical/surgical interventions "
            "and diagnostic procedures and screenings (e.g., operations, endoscopy, imaging- or lab-based tests)."
        )
    )
    equipment: Optional[List[str]] = Field(
        default=[],
        description=(
            "Physical medical devices and infrastructure—imaging machines (MRI/CT/X-ray), surgical/OR technologies, "
            "monitors, laboratory analyzers, and critical utilities (e.g., piped oxygen, backup power)."
        )
    )
    capability: Optional[List[str]] = Field(
        default=[],
        description=(
            "Medical capabilities defining what level and types of clinical care the facility can deliver—"
            "trauma/emergency care levels, specialized units (ICU/NICU), clinical programs, "
            "diagnostic capabilities, accreditations, inpatient/outpatient, staffing levels, patient capacity."
        )
    )


# ============================================================================
# OUR ENHANCED EXTRACTION SCHEMAS (keeping our trust scoring additions)
# ============================================================================

class ExtractedCapability(BaseModel):
    """
    Enhanced capability extraction with trust scoring
    Combines VF official format with our validation layer
    """
    model_config = ConfigDict(protected_namespaces=())
    
    capability: str = Field(..., description="Canonical capability name from ontology")
    evidence: List[str] = Field(..., description="Direct quotes from facility text supporting this capability")
    confidence: float = Field(..., description="Confidence score 0.2-1.0")
    availability: Literal["available", "limited", "unavailable", "unknown"] = Field(
        ..., description="Availability status of this capability"
    )
    dependencies: List[str] = Field(default=[], description="Required supporting capabilities")
    flags: List[str] = Field(default=[], description="Quality flags: suspicious, incomplete, contradictory, unverified")
    
    # VF category classification
    vf_category: Optional[Literal["procedure", "equipment", "capability"]] = Field(
        None, description="VF official category: procedure, equipment, or capability"
    )


class FacilityProfile(BaseModel):
    """
    Complete facility profile combining VF official fields with our extraction
    """
    model_config = ConfigDict(protected_namespaces=())
    
    # Core identification (from dataset)
    facility_id: str = Field(..., description="Internal facility ID (row_id from dataset)")
    pk_unique_id: Optional[int] = Field(None, description="VF primary key unique ID")
    unique_id: Optional[str] = Field(None, description="VF UUID unique identifier")
    source_url: Optional[str] = Field(None, description="Source URL for facility data")
    
    # VF BaseOrganization fields
    name: str = Field(..., description="Official facility name")
    phone_numbers: Optional[List[str]] = None
    officialPhone: Optional[str] = None
    email: Optional[str] = None
    websites: Optional[List[str]] = None
    officialWebsite: Optional[str] = None
    yearEstablished: Optional[int] = None
    acceptsVolunteers: Optional[bool] = None
    facebookLink: Optional[str] = None
    twitterLink: Optional[str] = None
    linkedinLink: Optional[str] = None
    instagramLink: Optional[str] = None
    logo: Optional[str] = None
    
    # VF Flattened address structure
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    address_line3: Optional[str] = None
    address_city: Optional[str] = None
    address_stateOrRegion: Optional[str] = None  # This is our "region"
    address_zipOrPostcode: Optional[str] = None
    address_country: Optional[str] = None
    address_countryCode: Optional[str] = None
    
    # VF Facility-specific fields
    facilityTypeId: Optional[Literal["hospital", "pharmacy", "doctor", "clinic", "dentist"]] = None
    operatorTypeId: Optional[Literal["public", "private"]] = None
    affiliationTypeIds: Optional[List[str]] = None
    organization_type: Optional[str] = None  # From dataset
    description: Optional[str] = None
    organizationDescription: Optional[str] = None
    missionStatement: Optional[str] = None
    missionStatementLink: Optional[str] = None
    area: Optional[int] = None
    numberDoctors: Optional[int] = None
    capacity: Optional[int] = None
    
    # VF Free-form extraction (official 3 categories)
    specialties: Optional[List[str]] = Field(default=[], description="Medical specialties from VF taxonomy")
    procedure: Optional[List[str]] = Field(default=[], description="Clinical procedures performed")
    equipment: Optional[List[str]] = Field(default=[], description="Medical equipment and infrastructure")
    capability: Optional[List[str]] = Field(default=[], description="Medical capabilities and care levels")
    
    # Our enhanced extraction with trust scoring
    capabilities: List[ExtractedCapability] = Field(default=[], description="Detailed capability extraction with evidence")
    trust_score: Optional[float] = Field(None, description="Overall facility trust score 0.0-1.0")
    
    # Context and metadata
    raw_data: Optional[str] = Field(None, description="Raw facility context used for extraction")
    content_table_id: Optional[str] = None


# Backward compatibility aliases
FacilityWithCapabilities = FacilityProfile


# ============================================================================
# REGIONAL ANALYSIS SCHEMAS
# ============================================================================

class RegionCapabilityGap(BaseModel):
    """Analysis of capability gaps in a region"""
    model_config = ConfigDict(protected_namespaces=())
    
    region: str
    critical_capabilities_present: List[str]
    critical_capabilities_missing: List[str]
    facilities_with_capability: int
    total_facilities: int
    coverage_percentage: float
    trust_score: float
    recommendations: List[str]


class ActionPlan(BaseModel):
    """Recommended actions to address healthcare gaps"""
    model_config = ConfigDict(protected_namespaces=())
    
    region: str
    priority: Literal["critical", "high", "medium", "low"]
    missing_capabilities: List[str]
    recommended_actions: List[str]
    estimated_population_impact: Optional[int] = None
    urgency_score: float


class MedicalDesertReport(BaseModel):
    """Complete medical desert analysis report"""
    model_config = ConfigDict(protected_namespaces=())
    
    region: str
    is_medical_desert: bool
    desert_severity: Literal["severe", "moderate", "mild", "none"]
    critical_gaps: List[str]
    available_capabilities: List[str]
    nearest_facilities_with_gaps: List[dict]
    population_at_risk: Optional[int] = None
    action_plan: Optional[ActionPlan] = None


# ============================================================================
# CITATION AND TRACEABILITY
# ============================================================================

class Citation(BaseModel):
    """Citation linking extracted data to source"""
    model_config = ConfigDict(protected_namespaces=())
    
    source_row_id: int
    facility_name: str
    evidence_text: str
    capability: str
    confidence: float
    extraction_timestamp: str
    agent_step: str  # Which agent step produced this


class AgenticStepTrace(BaseModel):
    """Traceability for multi-step agentic reasoning"""
    model_config = ConfigDict(protected_namespaces=())
    
    step_number: int
    step_name: str
    input_data: dict
    output_data: dict
    citations: List[Citation]
    model_used: str
    timestamp: str
