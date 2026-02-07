"""
Capability Validator - Checks consistency and flags suspicious claims
"""
from typing import List, Dict, Tuple
from schemas import ExtractedCapability, FacilityWithCapabilities
from ontology import CAPABILITY_DEPENDENCIES, normalize_capability, CRITICAL_CAPABILITIES
import re

class CapabilityValidator:
    """
    Validates extracted capabilities for:
    1. Dependency consistency (e.g., surgery requires anesthesia)
    2. Facility type appropriateness (e.g., CHPS compounds unlikely to have ICU)
    3. Evidence quality (e.g., vague vs. specific claims)
    4. Contradictions (e.g., "no specialists" but claims specialty services)
    """
    
    # Facility type capability constraints
    FACILITY_CONSTRAINTS = {
        'chps': {
            'unlikely': ['icu', 'surgery', 'diagnostic_imaging', 'specialized_care'],
            'typical': ['basic_consultation', 'immunization', 'family_planning', 'antenatal_care']
        },
        'health_centre': {
            'unlikely': ['icu', 'advanced_surgery', 'dialysis'],
            'typical': ['basic_surgery', 'laboratory', 'xray', 'maternity', 'emergency_care']
        },
        'district_hospital': {
            'unlikely': ['organ_transplant', 'advanced_cardiology'],
            'typical': ['surgery', 'icu', 'laboratory', 'diagnostic_imaging', 'specialist_care']
        },
        'regional_hospital': {
            'unlikely': [],
            'typical': ['advanced_surgery', 'icu', 'specialist_care', 'diagnostic_imaging', 'emergency_care']
        },
        'teaching_hospital': {
            'unlikely': [],
            'typical': ['advanced_surgery', 'icu', 'specialist_care', 'research', 'training']
        }
    }
    
    # Evidence quality indicators
    WEAK_EVIDENCE_PATTERNS = [
        r'\bmay\b', r'\bpossibly\b', r'\bperhaps\b', r'\bsometimes\b',
        r'\bgeneral\b', r'\bbasic\b', r'\blimited\b', r'\bminimal\b'
    ]
    
    STRONG_EVIDENCE_PATTERNS = [
        r'\b\d+\b',  # Numbers (bed counts, staff counts)
        r'\bspecialized\b', r'\bequipped\b', r'\bcertified\b',
        r'\b24/7\b', r'\b24-hour\b', r'\bround-the-clock\b'
    ]
    
    def __init__(self):
        self.validation_stats = {
            'total_validated': 0,
            'dependency_violations': 0,
            'facility_type_mismatches': 0,
            'weak_evidence': 0,
            'high_confidence': 0
        }
    
    def validate_capability(
        self,
        capability: ExtractedCapability,
        all_capabilities: List[ExtractedCapability],
        facility_type: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate a single capability
        
        Returns:
            (is_valid, list_of_warnings)
        """
        warnings = []
        is_valid = True
        
        # Normalize capability name
        norm_cap = normalize_capability(capability.capability)
        
        # Check 1: Dependency validation
        if norm_cap in CAPABILITY_DEPENDENCIES:
            required_deps = CAPABILITY_DEPENDENCIES[norm_cap]
            present_caps = {normalize_capability(c.capability) for c in all_capabilities}
            
            for dep in required_deps:
                if dep not in present_caps:
                    warnings.append(
                        f"Missing dependency: {norm_cap} requires {dep} but it was not found"
                    )
                    is_valid = False
                    self.validation_stats['dependency_violations'] += 1
        
        # Check 2: Facility type appropriateness
        facility_type_norm = facility_type.lower().replace(' ', '_')
        if facility_type_norm in self.FACILITY_CONSTRAINTS:
            constraints = self.FACILITY_CONSTRAINTS[facility_type_norm]
            
            # Check if capability is unlikely for this facility type
            for unlikely_cap in constraints['unlikely']:
                if unlikely_cap in norm_cap or norm_cap in unlikely_cap:
                    warnings.append(
                        f"Unlikely for {facility_type}: {norm_cap} is uncommon in this facility type"
                    )
                    capability.flags.append('unlikely_for_facility_type')
                    self.validation_stats['facility_type_mismatches'] += 1
        
        # Check 3: Evidence quality
        evidence_text = ' '.join(capability.evidence)
        
        # Check for weak evidence
        weak_count = sum(
            len(re.findall(pattern, evidence_text, re.IGNORECASE))
            for pattern in self.WEAK_EVIDENCE_PATTERNS
        )
        
        # Check for strong evidence
        strong_count = sum(
            len(re.findall(pattern, evidence_text, re.IGNORECASE))
            for pattern in self.STRONG_EVIDENCE_PATTERNS
        )
        
        if weak_count > strong_count:
            warnings.append(
                f"Weak evidence: Evidence contains vague language without specific details"
            )
            capability.flags.append('weak_evidence')
            self.validation_stats['weak_evidence'] += 1
        
        # Check 4: Confidence threshold
        if capability.confidence < 0.5:
            warnings.append(
                f"Low confidence: Confidence score {capability.confidence:.2f} is below threshold"
            )
            capability.flags.append('low_confidence')
        elif capability.confidence >= 0.8:
            self.validation_stats['high_confidence'] += 1
        
        # Check 5: Availability issues
        if capability.availability in ['unavailable', 'unknown']:
            warnings.append(
                f"Availability issue: Capability marked as {capability.availability}"
            )
        
        self.validation_stats['total_validated'] += 1
        
        return is_valid, warnings
    
    def validate_facility(self, facility: FacilityWithCapabilities) -> Dict:
        """
        Validate all capabilities for a facility
        
        Returns:
            Validation report with warnings and statistics
        """
        report = {
            'facility_id': facility.facility_id,
            'facility_name': facility.facility_name,
            'facility_type': facility.facility_type,
            'total_capabilities': len(facility.capabilities),
            'valid_capabilities': 0,
            'invalid_capabilities': 0,
            'warnings': [],
            'critical_capabilities_present': [],
            'critical_capabilities_missing': []
        }
        
        # Validate each capability
        for capability in facility.capabilities:
            is_valid, warnings = self.validate_capability(
                capability,
                facility.capabilities,
                facility.facility_type
            )
            
            if is_valid:
                report['valid_capabilities'] += 1
            else:
                report['invalid_capabilities'] += 1
            
            if warnings:
                report['warnings'].extend([
                    f"{capability.capability}: {w}" for w in warnings
                ])
        
        # Check critical capabilities coverage
        present_caps = {normalize_capability(c.capability) for c in facility.capabilities}
        
        for critical_cap in CRITICAL_CAPABILITIES:
            if critical_cap in present_caps:
                report['critical_capabilities_present'].append(critical_cap)
            else:
                report['critical_capabilities_missing'].append(critical_cap)
        
        return report
    
    def validate_batch(self, facilities: List[FacilityWithCapabilities]) -> Dict:
        """
        Validate multiple facilities and generate aggregate statistics
        """
        reports = [self.validate_facility(f) for f in facilities]
        
        aggregate = {
            'total_facilities': len(facilities),
            'total_capabilities': sum(r['total_capabilities'] for r in reports),
            'valid_capabilities': sum(r['valid_capabilities'] for r in reports),
            'invalid_capabilities': sum(r['invalid_capabilities'] for r in reports),
            'facilities_with_warnings': len([r for r in reports if r['warnings']]),
            'validation_stats': self.validation_stats,
            'facility_reports': reports
        }
        
        return aggregate
    
    def get_suspicious_facilities(
        self,
        facilities: List[FacilityWithCapabilities],
        threshold: int = 3
    ) -> List[Dict]:
        """
        Identify facilities with multiple validation issues
        
        Args:
            facilities: List of facilities to check
            threshold: Minimum number of warnings to flag as suspicious
            
        Returns:
            List of suspicious facilities with their issues
        """
        suspicious = []
        
        for facility in facilities:
            report = self.validate_facility(facility)
            
            if len(report['warnings']) >= threshold:
                suspicious.append({
                    'facility': facility,
                    'warning_count': len(report['warnings']),
                    'warnings': report['warnings']
                })
        
        return sorted(suspicious, key=lambda x: x['warning_count'], reverse=True)


if __name__ == "__main__":
    # Test validation
    from schemas import ExtractedCapability, FacilityWithCapabilities
    
    # Create test facility with suspicious claims
    test_capabilities = [
        ExtractedCapability(
            capability="advanced_surgery",
            evidence=["The facility may have some surgical capabilities"],
            confidence=0.4,
            availability="available",
            dependencies=[],
            flags=[],
            facility_id="test_001",
            facility_name="Test CHPS",
            region="Test Region",
            source_row_id="test_001"
        ),
        ExtractedCapability(
            capability="icu",
            evidence=["General care available"],
            confidence=0.3,
            availability="unknown",
            dependencies=[],
            flags=[],
            facility_id="test_001",
            facility_name="Test CHPS",
            region="Test Region",
            source_row_id="test_001"
        )
    ]
    
    test_facility = FacilityWithCapabilities(
        facility_id="test_001",
        facility_name="Test CHPS Compound",
        region="Test Region",
        district="Test District",
        ownership="Government",
        facility_type="CHPS Compound",
        capabilities=test_capabilities,
        raw_data="Test data"
    )
    
    validator = CapabilityValidator()
    report = validator.validate_facility(test_facility)
    
    print("Validation Report:")
    print(f"Facility: {report['facility_name']}")
    print(f"Valid: {report['valid_capabilities']}/{report['total_capabilities']}")
    print(f"Warnings: {len(report['warnings'])}")
    for warning in report['warnings']:
        print(f"  - {warning}")
