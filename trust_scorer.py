"""
Trust Scoring System - Assigns reliability scores to extracted capabilities
"""
import re
from typing import List, Dict
from schemas import ExtractedCapability, FacilityWithCapabilities
from ontology import normalize_capability

class TrustScorer:
    """
    Calculates trust scores based on:
    1. Evidence specificity (numbers, names, details)
    2. Consistency with dependencies
    3. Source data quality
    4. Capability confidence
    5. Validation flags
    """
    
    # Weights for different trust factors
    WEIGHTS = {
        'confidence': 0.30,
        'evidence_quality': 0.25,
        'dependency_consistency': 0.20,
        'availability': 0.15,
        'flags_penalty': 0.10
    }
    
    # Evidence quality indicators
    HIGH_QUALITY_INDICATORS = [
        (r'\b\d+\s+(beds?|staff|doctors?|nurses?)\b', 3.0),  # Specific numbers
        (r'\b(dr\.|doctor|specialist)\s+\w+\b', 2.5),  # Named specialists
        (r'\b24/7\b|\b24-hour\b|\bround-the-clock\b', 2.0),  # Specific availability
        (r'\b(equipped|certified|licensed|accredited)\b', 2.0),  # Official status
        (r'\b\d{4}\b', 1.5),  # Years (e.g., "established 2015")
        (r'\b(department|unit|ward|theatre)\b', 1.5),  # Specific facilities
    ]
    
    LOW_QUALITY_INDICATORS = [
        (r'\b(may|might|possibly|perhaps|sometimes)\b', -2.0),  # Hedging
        (r'\b(limited|minimal|basic|general)\b', -1.5),  # Vague qualifiers
        (r'\b(no|none|not|lacking|absent)\b', -1.0),  # Negations
        (r'\bunknown\b', -2.0),  # Unknown information
    ]
    
    def __init__(self):
        self.scoring_stats = {
            'total_scored': 0,
            'high_trust': 0,  # >= 0.8
            'medium_trust': 0,  # 0.5 - 0.8
            'low_trust': 0,  # < 0.5
        }
    
    def score_evidence_quality(self, evidence: List[str]) -> float:
        """
        Score evidence quality based on specificity and detail
        
        Returns:
            Score between 0 and 1
        """
        if not evidence:
            return 0.0
        
        evidence_text = ' '.join(evidence).lower()
        
        # Calculate quality score
        quality_score = 0.0
        
        # Add points for high-quality indicators
        for pattern, weight in self.HIGH_QUALITY_INDICATORS:
            matches = len(re.findall(pattern, evidence_text, re.IGNORECASE))
            quality_score += matches * weight
        
        # Subtract points for low-quality indicators
        for pattern, penalty in self.LOW_QUALITY_INDICATORS:
            matches = len(re.findall(pattern, evidence_text, re.IGNORECASE))
            quality_score += matches * penalty
        
        # Normalize to 0-1 range
        # Base score of 0.5 for any evidence, adjusted by quality indicators
        base_score = 0.5
        adjustment = quality_score / 10.0  # Scale adjustment
        final_score = base_score + adjustment
        
        return max(0.0, min(1.0, final_score))
    
    def score_dependency_consistency(
        self,
        capability: ExtractedCapability,
        all_capabilities: List[ExtractedCapability]
    ) -> float:
        """
        Score how well capability dependencies are satisfied
        
        Returns:
            Score between 0 and 1
        """
        if not capability.dependencies:
            return 1.0  # No dependencies = full score
        
        present_caps = {normalize_capability(c.capability) for c in all_capabilities}
        
        satisfied = sum(
            1 for dep in capability.dependencies
            if normalize_capability(dep) in present_caps
        )
        
        return satisfied / len(capability.dependencies)
    
    def score_availability(self, availability: str) -> float:
        """
        Score based on availability status
        
        Returns:
            Score between 0 and 1
        """
        availability_scores = {
            'available': 1.0,
            'limited': 0.6,
            'unavailable': 0.2,
            'unknown': 0.3
        }
        
        return availability_scores.get(availability.lower(), 0.5)
    
    def calculate_flags_penalty(self, flags: List[str]) -> float:
        """
        Calculate penalty based on validation flags
        
        Returns:
            Penalty between 0 (no penalty) and 1 (maximum penalty)
        """
        flag_penalties = {
            'weak_evidence': 0.3,
            'low_confidence': 0.2,
            'unlikely_for_facility_type': 0.4,
            'missing_dependencies': 0.5,
            'contradiction': 0.6
        }
        
        total_penalty = sum(flag_penalties.get(flag, 0.1) for flag in flags)
        
        # Cap penalty at 1.0
        return min(1.0, total_penalty)
    
    def calculate_trust_score(
        self,
        capability: ExtractedCapability,
        all_capabilities: List[ExtractedCapability]
    ) -> float:
        """
        Calculate overall trust score for a capability
        
        Returns:
            Trust score between 0 and 1
        """
        # Component scores
        confidence_score = capability.confidence
        evidence_score = self.score_evidence_quality(capability.evidence)
        dependency_score = self.score_dependency_consistency(capability, all_capabilities)
        availability_score = self.score_availability(capability.availability)
        flags_penalty = self.calculate_flags_penalty(capability.flags)
        
        # Weighted combination
        trust_score = (
            self.WEIGHTS['confidence'] * confidence_score +
            self.WEIGHTS['evidence_quality'] * evidence_score +
            self.WEIGHTS['dependency_consistency'] * dependency_score +
            self.WEIGHTS['availability'] * availability_score -
            self.WEIGHTS['flags_penalty'] * flags_penalty
        )
        
        # Ensure score is between 0 and 1
        trust_score = max(0.0, min(1.0, trust_score))
        
        # Update statistics
        self.scoring_stats['total_scored'] += 1
        if trust_score >= 0.8:
            self.scoring_stats['high_trust'] += 1
        elif trust_score >= 0.5:
            self.scoring_stats['medium_trust'] += 1
        else:
            self.scoring_stats['low_trust'] += 1
        
        return trust_score
    
    def score_facility(self, facility: FacilityWithCapabilities) -> Dict:
        """
        Calculate trust scores for all capabilities in a facility
        
        Returns:
            Dictionary with scored capabilities and statistics
        """
        scored_capabilities = []
        
        for capability in facility.capabilities:
            trust_score = self.calculate_trust_score(
                capability,
                facility.capabilities
            )
            
            scored_capabilities.append({
                'capability': capability.capability,
                'confidence': capability.confidence,
                'trust_score': trust_score,
                'evidence': capability.evidence,
                'availability': capability.availability,
                'flags': capability.flags
            })
        
        # Sort by trust score
        scored_capabilities.sort(key=lambda x: x['trust_score'], reverse=True)
        
        # Calculate facility-level statistics
        trust_scores = [c['trust_score'] for c in scored_capabilities]
        
        return {
            'facility_id': facility.facility_id,
            'facility_name': facility.facility_name,
            'capabilities': scored_capabilities,
            'statistics': {
                'total_capabilities': len(scored_capabilities),
                'average_trust': sum(trust_scores) / len(trust_scores) if trust_scores else 0.0,
                'median_trust': sorted(trust_scores)[len(trust_scores) // 2] if trust_scores else 0.0,
                'high_trust_count': len([s for s in trust_scores if s >= 0.8]),
                'medium_trust_count': len([s for s in trust_scores if 0.5 <= s < 0.8]),
                'low_trust_count': len([s for s in trust_scores if s < 0.5])
            }
        }
    
    def score_batch(self, facilities: List[FacilityWithCapabilities]) -> Dict:
        """
        Score multiple facilities and generate aggregate statistics
        """
        facility_scores = [self.score_facility(f) for f in facilities]
        
        all_trust_scores = [
            cap['trust_score']
            for f_score in facility_scores
            for cap in f_score['capabilities']
        ]
        
        aggregate = {
            'total_facilities': len(facilities),
            'total_capabilities': len(all_trust_scores),
            'aggregate_statistics': {
                'mean_trust': sum(all_trust_scores) / len(all_trust_scores) if all_trust_scores else 0.0,
                'median_trust': sorted(all_trust_scores)[len(all_trust_scores) // 2] if all_trust_scores else 0.0,
                'high_trust_count': len([s for s in all_trust_scores if s >= 0.8]),
                'medium_trust_count': len([s for s in all_trust_scores if 0.5 <= s < 0.8]),
                'low_trust_count': len([s for s in all_trust_scores if s < 0.5])
            },
            'scoring_stats': self.scoring_stats,
            'facility_scores': facility_scores
        }
        
        return aggregate
    
    def filter_high_trust_capabilities(
        self,
        facility: FacilityWithCapabilities,
        min_trust: float = 0.7
    ) -> List[ExtractedCapability]:
        """
        Return only high-trust capabilities for a facility
        """
        high_trust = []
        
        for capability in facility.capabilities:
            trust_score = self.calculate_trust_score(
                capability,
                facility.capabilities
            )
            
            if trust_score >= min_trust:
                high_trust.append(capability)
        
        return high_trust


if __name__ == "__main__":
    # Test trust scoring
    from schemas import ExtractedCapability, FacilityWithCapabilities
    
    test_capabilities = [
        ExtractedCapability(
            capability="emergency_care",
            evidence=[
                "24-hour emergency department with 3 doctors",
                "Equipped with resuscitation equipment",
                "Ambulance service available"
            ],
            confidence=0.9,
            availability="available",
            dependencies=["basic_consultation"],
            flags=[],
            facility_id="test_001",
            facility_name="Test Hospital",
            region="Test Region",
            source_row_id="test_001"
        ),
        ExtractedCapability(
            capability="surgery",
            evidence=["May have some surgical capabilities"],
            confidence=0.4,
            availability="unknown",
            dependencies=["anesthesia"],
            flags=["weak_evidence", "low_confidence"],
            facility_id="test_001",
            facility_name="Test Hospital",
            region="Test Region",
            source_row_id="test_001"
        )
    ]
    
    test_facility = FacilityWithCapabilities(
        facility_id="test_001",
        facility_name="Test District Hospital",
        region="Test Region",
        district="Test District",
        ownership="Government",
        facility_type="District Hospital",
        capabilities=test_capabilities,
        raw_data="Test data"
    )
    
    scorer = TrustScorer()
    results = scorer.score_facility(test_facility)
    
    print("Trust Scoring Results:")
    print(f"Facility: {results['facility_name']}")
    print(f"Average Trust: {results['statistics']['average_trust']:.2f}")
    print("\nCapabilities:")
    for cap in results['capabilities']:
        print(f"  {cap['capability']}: {cap['trust_score']:.2f} (confidence: {cap['confidence']:.2f})")
