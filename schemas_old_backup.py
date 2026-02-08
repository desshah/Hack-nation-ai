"""
Pydantic schemas for IDP agent output and data models
"""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ExtractedCapability(BaseModel):
    """Schema for extracted facility capabilities"""
    
    capability: str = Field(
        description="Canonical name of the medical capability (from CAPABILITY_ONTOLOGY)"
    )
    evidence: List[str] = Field(
        description="Direct text quotes supporting this capability",
        default_factory=list
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score: 1.0=explicit, 0.7=implied, 0.4=uncertain, 0.2=suspicious"
    )
    availability: Literal["available", "limited", "unavailable", "unknown"] = Field(
        description="Service availability status"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="Required capabilities for this service to function properly"
    )
    flags: List[str] = Field(
        default_factory=list,
        description="Quality/anomaly flags for this capability"
    )
    
    # Metadata for citations
    facility_id: str = Field(description="Unique facility identifier (unique_id)")
    facility_name: str = Field(description="Name of the facility")
    region: Optional[str] = Field(None, description="Normalized region name")
    source_row_id: int = Field(description="Original CSV row index")
    chunk_id: Optional[str] = Field(None, description="Hash of the text chunk used")
    extraction_timestamp: Optional[str] = Field(None, description="When this was extracted")


class FacilityProfile(BaseModel):
    """Aggregated profile of a facility with all capabilities"""
    
    facility_id: str
    facility_name: str
    region: str
    district: str = ""
    ownership: str = ""
    facility_type: str = ""
    capabilities: List[ExtractedCapability]
    raw_data: str = ""
    
    # Optional trust metrics
    trust_score: float = Field(
        default=0.0,
        ge=0.0, le=1.0,
        description="Overall trust score for this facility"
    )
    completeness_score: float = Field(
        ge=0.0, le=1.0,
        description="How complete is the facility data"
    )
    contradiction_count: int = Field(default=0)
    
    total_capabilities: int = Field(default=0)
    verified_capabilities: int = Field(default=0)
    suspicious_capabilities: int = Field(default=0)


class RegionCapabilityGap(BaseModel):
    """Identifies missing capabilities in a region"""
    
    region: str
    missing_critical_services: List[str]
    available_services: List[str]
    low_trust_services: List[str]  # Available but trust score < 0.5
    
    total_facilities: int
    trusted_facilities: int  # trust_score >= 0.7
    untrusted_facilities: int  # trust_score < 0.5
    
    population_at_risk: Optional[int] = None
    severity_score: float = Field(
        ge=0.0, le=1.0,
        description="How severe is this medical desert (1.0 = critical)"
    )


class ActionPlan(BaseModel):
    """Planner agent output - recommended actions"""
    
    region: str
    priority: Literal["critical", "high", "medium", "low"]
    
    recommended_actions: List[str] = Field(
        description="Top 3-5 specific interventions"
    )
    rationale: str = Field(
        description="Why these actions are recommended"
    )
    expected_impact: str = Field(
        description="Expected outcomes if implemented"
    )
    
    resources_needed: List[str] = Field(default_factory=list)
    estimated_cost: Optional[str] = None
    timeline: Optional[str] = None
    
    # Evidence
    evidence_facilities: List[str] = Field(
        default_factory=list,
        description="Facility IDs supporting this recommendation"
    )
    citations: List[dict] = Field(
        default_factory=list,
        description="Row-level citations"
    )


# Alias for backward compatibility
FacilityWithCapabilities = FacilityProfile
