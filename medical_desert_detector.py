"""
Medical Desert Detector - Identifies regions with critical capability gaps
"""
from typing import List, Dict, Set, Tuple
from collections import defaultdict
from schemas import FacilityWithCapabilities
from ontology import CRITICAL_CAPABILITIES, normalize_capability
from trust_scorer import TrustScorer

class MedicalDesertDetector:
    """
    Detects medical deserts by analyzing:
    1. Critical capability coverage by region/district
    2. Geographic distribution gaps
    3. Population-adjusted access metrics
    4. High-trust vs low-trust facility ratios
    """
    
    # Thresholds for desert classification
    DESERT_THRESHOLDS = {
        'critical_missing': 3,  # Missing 3+ critical capabilities
        'low_trust_ratio': 0.3,  # <30% of capabilities are high-trust
        'min_facilities': 2,  # Region needs at least 2 facilities with critical care
    }
    
    def __init__(self, trust_scorer: TrustScorer = None):
        self.trust_scorer = trust_scorer or TrustScorer()
        self.analysis_cache = {}
    
    def analyze_region(
        self,
        facilities: List[FacilityWithCapabilities],
        region: str,
        min_trust: float = 0.7
    ) -> Dict:
        """
        Analyze capability coverage for a specific region
        
        Returns:
            Region analysis with capability gaps and trust metrics
        """
        # Filter facilities in this region
        region_facilities = [f for f in facilities if f.address_stateOrRegion == region]
        
        if not region_facilities:
            return {
                'region': region,
                'is_desert': True,
                'severity': 'critical',
                'reason': 'No facilities found',
                'facilities_count': 0,
                'critical_capabilities_present': [],
                'critical_capabilities_missing': CRITICAL_CAPABILITIES
            }
        
        # Track which critical capabilities are available (high-trust)
        capabilities_present = set()
        capabilities_low_trust = set()
        
        facility_details = []
        
        for facility in region_facilities:
            # Score facility capabilities
            facility_score = self.trust_scorer.score_facility(facility)
            
            # Track high-trust critical capabilities
            for cap_score in facility_score['capabilities']:
                norm_cap = normalize_capability(cap_score['capability'])
                
                if norm_cap in CRITICAL_CAPABILITIES:
                    if cap_score['trust_score'] >= min_trust:
                        capabilities_present.add(norm_cap)
                    else:
                        capabilities_low_trust.add(norm_cap)
            
            facility_details.append({
                'name': facility.name,
                'type': facility.facilityTypeId or facility.organization_type,
                'district': facility.address_city,
                'average_trust': facility_score['statistics']['average_trust'],
                'high_trust_count': facility_score['statistics']['high_trust_count']
            })
        
        # Calculate missing critical capabilities
        capabilities_missing = set(CRITICAL_CAPABILITIES) - capabilities_present
        
        # Calculate desert severity
        missing_count = len(capabilities_missing)
        low_trust_count = len(capabilities_low_trust)
        facility_count = len(region_facilities)
        
        is_desert = (
            missing_count >= self.DESERT_THRESHOLDS['critical_missing'] or
            facility_count < self.DESERT_THRESHOLDS['min_facilities']
        )
        
        # Determine severity
        if missing_count >= 6:
            severity = 'critical'
        elif missing_count >= 4:
            severity = 'severe'
        elif missing_count >= 2:
            severity = 'moderate'
        else:
            severity = 'minimal'
        
        return {
            'region': region,
            'is_desert': is_desert,
            'severity': severity,
            'facilities_count': facility_count,
            'critical_capabilities_present': sorted(list(capabilities_present)),
            'critical_capabilities_missing': sorted(list(capabilities_missing)),
            'critical_capabilities_low_trust': sorted(list(capabilities_low_trust)),
            'coverage_percentage': (len(capabilities_present) / len(CRITICAL_CAPABILITIES)) * 100,
            'facilities': facility_details
        }
    
    def analyze_district(
        self,
        facilities: List[FacilityWithCapabilities],
        region: str,
        district: str,
        min_trust: float = 0.7
    ) -> Dict:
        """
        Analyze capability coverage for a specific district within a region
        """
        # Filter facilities in this district
        district_facilities = [
            f for f in facilities 
            if f.address_stateOrRegion == region and f.address_city == district
        ]
        
        if not district_facilities:
            return {
                'region': region,
                'district': district,
                'is_desert': True,
                'severity': 'critical',
                'reason': 'No facilities found',
                'facilities_count': 0,
                'critical_capabilities_present': [],
                'critical_capabilities_missing': CRITICAL_CAPABILITIES
            }
        
        # Similar analysis as region but at district level
        capabilities_present = set()
        
        for facility in district_facilities:
            high_trust_caps = self.trust_scorer.filter_high_trust_capabilities(
                facility,
                min_trust
            )
            
            for cap in high_trust_caps:
                norm_cap = normalize_capability(cap.capability)
                if norm_cap in CRITICAL_CAPABILITIES:
                    capabilities_present.add(norm_cap)
        
        capabilities_missing = set(CRITICAL_CAPABILITIES) - capabilities_present
        
        return {
            'region': region,
            'district': district,
            'is_desert': len(capabilities_missing) >= self.DESERT_THRESHOLDS['critical_missing'],
            'severity': self._calculate_severity(len(capabilities_missing)),
            'facilities_count': len(district_facilities),
            'critical_capabilities_present': sorted(list(capabilities_present)),
            'critical_capabilities_missing': sorted(list(capabilities_missing)),
            'coverage_percentage': (len(capabilities_present) / len(CRITICAL_CAPABILITIES)) * 100
        }
    
    def analyze_all_regions(
        self,
        facilities: List[FacilityWithCapabilities],
        min_trust: float = 0.7
    ) -> Dict:
        """
        Analyze all regions and identify medical deserts
        """
        # Get unique regions
        regions = set(f.address_stateOrRegion for f in facilities if f.address_stateOrRegion)
        
        region_analyses = []
        desert_regions = []
        
        for region in regions:
            analysis = self.analyze_region(facilities, region, min_trust)
            region_analyses.append(analysis)
            
            if analysis['is_desert']:
                desert_regions.append({
                    'region': region,
                    'severity': analysis['severity'],
                    'missing_capabilities': analysis['critical_capabilities_missing']
                })
        
        # Sort deserts by severity
        severity_order = {'critical': 0, 'severe': 1, 'moderate': 2, 'minimal': 3}
        desert_regions.sort(key=lambda x: severity_order[x['severity']])
        
        return {
            'total_regions': len(regions),
            'desert_regions_count': len(desert_regions),
            'desert_regions': desert_regions,
            'all_regions': region_analyses,
            'most_common_gaps': self._identify_common_gaps(region_analyses)
        }
    
    def analyze_all_districts(
        self,
        facilities: List[FacilityWithCapabilities],
        min_trust: float = 0.7
    ) -> Dict:
        """
        Analyze all districts across all regions
        """
        # Get unique region-district pairs
        districts = defaultdict(set)
        for f in facilities:
            if f.address_city and f.address_stateOrRegion:
                districts[f.address_stateOrRegion].add(f.address_city)
        
        district_analyses = []
        desert_districts = []
        
        for region, district_set in districts.items():
            for district in district_set:
                analysis = self.analyze_district(facilities, region, district, min_trust)
                district_analyses.append(analysis)
                
                if analysis['is_desert']:
                    desert_districts.append({
                        'region': region,
                        'district': district,
                        'severity': analysis['severity'],
                        'missing_capabilities': analysis['critical_capabilities_missing']
                    })
        
        return {
            'total_districts': len(district_analyses),
            'desert_districts_count': len(desert_districts),
            'desert_districts': desert_districts,
            'all_districts': district_analyses
        }
    
    def identify_capability_deserts(
        self,
        facilities: List[FacilityWithCapabilities],
        capability: str,
        min_trust: float = 0.7
    ) -> Dict:
        """
        Identify regions/districts lacking a specific capability
        
        Args:
            capability: Specific capability to check (e.g., 'emergency_care')
        """
        norm_capability = normalize_capability(capability)
        
        # Track regions with/without this capability
        regions_with = set()
        regions_without = set()
        
        for facility in facilities:
            region = facility.address_stateOrRegion
            
            if not region:
                continue
            
            # Check if facility has this capability with high trust
            high_trust_caps = self.trust_scorer.filter_high_trust_capabilities(
                facility,
                min_trust
            )
            
            has_capability = any(
                normalize_capability(cap.capability) == norm_capability
                for cap in high_trust_caps
            )
            
            if has_capability:
                regions_with.add(region)
            else:
                regions_without.add(region)
        
        # Regions without this capability
        desert_regions = regions_without - regions_with
        
        return {
            'capability': capability,
            'regions_with_capability': sorted(list(regions_with)),
            'regions_without_capability': sorted(list(desert_regions)),
            'coverage_percentage': (len(regions_with) / (len(regions_with) + len(desert_regions))) * 100 if (regions_with or desert_regions) else 0
        }
    
    def _calculate_severity(self, missing_count: int) -> str:
        """Helper to calculate severity from missing capability count"""
        if missing_count >= 6:
            return 'critical'
        elif missing_count >= 4:
            return 'severe'
        elif missing_count >= 2:
            return 'moderate'
        else:
            return 'minimal'
    
    def _identify_common_gaps(self, region_analyses: List[Dict]) -> List[Tuple[str, int]]:
        """Identify the most commonly missing critical capabilities"""
        gap_counts = defaultdict(int)
        
        for analysis in region_analyses:
            for missing_cap in analysis['critical_capabilities_missing']:
                gap_counts[missing_cap] += 1
        
        # Sort by frequency
        common_gaps = sorted(
            gap_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return common_gaps


if __name__ == "__main__":
    # Test medical desert detection
    from schemas import ExtractedCapability, FacilityWithCapabilities
    
    # Create test facilities in different regions
    test_facilities = [
        FacilityWithCapabilities(
            facility_id="f001",
            facility_name="Greater Accra Regional Hospital",
            region="Greater Accra",
            district="Accra Metro",
            ownership="Government",
            facility_type="Regional Hospital",
            capabilities=[
                ExtractedCapability(
                    capability="emergency_care",
                    evidence=["24/7 emergency with 5 doctors"],
                    confidence=0.9,
                    availability="available",
                    dependencies=[],
                    flags=[],
                    facility_id="f001",
                    facility_name="Greater Accra Regional Hospital",
                    region="Greater Accra",
                    source_row_id="f001"
                ),
                ExtractedCapability(
                    capability="icu",
                    evidence=["10-bed ICU with ventilators"],
                    confidence=0.85,
                    availability="available",
                    dependencies=[],
                    flags=[],
                    facility_id="f001",
                    facility_name="Greater Accra Regional Hospital",
                    region="Greater Accra",
                    source_row_id="f001"
                )
            ],
            raw_data="Test"
        ),
        FacilityWithCapabilities(
            facility_id="f002",
            facility_name="Rural CHPS Compound",
            region="Upper East",
            district="Bawku West",
            ownership="Government",
            facility_type="CHPS Compound",
            capabilities=[
                ExtractedCapability(
                    capability="basic_consultation",
                    evidence=["General outpatient services"],
                    confidence=0.7,
                    availability="available",
                    dependencies=[],
                    flags=[],
                    facility_id="f002",
                    facility_name="Rural CHPS Compound",
                    region="Upper East",
                    source_row_id="f002"
                )
            ],
            raw_data="Test"
        )
    ]
    
    detector = MedicalDesertDetector()
    
    # Analyze all regions
    results = detector.analyze_all_regions(test_facilities)
    
    print("Medical Desert Analysis:")
    print(f"Total Regions: {results['total_regions']}")
    print(f"Desert Regions: {results['desert_regions_count']}")
    print("\nDesert Regions:")
    for desert in results['desert_regions']:
        print(f"  {desert['region']} - {desert['severity']}")
        print(f"    Missing: {', '.join(desert['missing_capabilities'][:3])}...")
