"""
Citation Generator - Provides evidence traceability for extracted capabilities
"""
from typing import List, Dict
from schemas import ExtractedCapability, FacilityWithCapabilities


class CitationGenerator:
    """
    Generates citations for extracted capabilities to support:
    1. Traceability back to source data
    2. Evidence verification
    3. Trust/confidence explanations
    4. Data quality auditing
    """
    
    def generate_capability_citation(self, capability: ExtractedCapability) -> Dict:
        """
        Generate citation for a single capability
        
        Returns:
            Citation with source, evidence, and metadata
        """
        citation = {
            'capability': capability.capability,
            'confidence': capability.confidence,
            'availability': capability.availability,
            'source': {
                'facility_id': capability.facility_id,
                'facility_name': capability.facility_name,
                'region': capability.region,
                'row_id': capability.source_row_id
            },
            'evidence': capability.evidence,
            'validation': {
                'dependencies_required': capability.dependencies,
                'flags': capability.flags
            },
            'citation_text': self._format_citation_text(capability)
        }
        
        return citation
    
    def generate_facility_citations(self, facility: FacilityWithCapabilities) -> Dict:
        """
        Generate all citations for a facility
        """
        citations = {
            'facility': {
                'id': facility.facility_id,
                'name': facility.facility_name,
                'region': facility.region,
                'district': facility.district,
                'type': facility.facility_type,
                'ownership': facility.ownership
            },
            'capabilities': [
                self.generate_capability_citation(cap)
                for cap in facility.capabilities
            ],
            'summary': {
                'total_capabilities': len(facility.capabilities),
                'high_confidence_count': len([
                    c for c in facility.capabilities if c.confidence >= 0.8
                ]),
                'flagged_count': len([
                    c for c in facility.capabilities if c.flags
                ])
            }
        }
        
        return citations
    
    def generate_analysis_citations(
        self,
        facilities: List[FacilityWithCapabilities],
        analysis_type: str,
        findings: List[str]
    ) -> Dict:
        """
        Generate citations for an entire analysis (e.g., medical desert detection)
        
        Args:
            facilities: Facilities included in analysis
            analysis_type: Type of analysis (e.g., 'medical_desert', 'capability_gap')
            findings: List of key findings
            
        Returns:
            Comprehensive citation report
        """
        citations = {
            'analysis_type': analysis_type,
            'findings': findings,
            'data_sources': {
                'facilities_analyzed': len(facilities),
                'regions_covered': len(set(f.region for f in facilities)),
                'facilities': [
                    {
                        'id': f.facility_id,
                        'name': f.facility_name,
                        'region': f.region,
                        'capabilities_extracted': len(f.capabilities)
                    }
                    for f in facilities
                ]
            },
            'methodology': {
                'extraction_model': 'llama-3.3-70b-versatile',
                'embedding_model': 'BAAI/bge-large-en-v1.5',
                'trust_threshold': 0.7,
                'validation_layers': [
                    'dependency_consistency',
                    'facility_type_appropriateness',
                    'evidence_quality'
                ]
            }
        }
        
        return citations
    
    def _format_citation_text(self, capability: ExtractedCapability) -> str:
        """
        Format citation as human-readable text
        
        Returns:
            Citation string in academic style
        """
        evidence_str = "; ".join(capability.evidence[:2])  # First 2 evidence items
        
        citation_text = (
            f"{capability.facility_name} ({capability.region}). "
            f"{capability.capability.replace('_', ' ').title()} "
            f"[Confidence: {capability.confidence:.2f}, "
            f"Availability: {capability.availability}]. "
            f"Evidence: \"{evidence_str}\". "
            f"Source: Virtue Foundation Ghana Healthcare Database, "
            f"Row ID: {capability.source_row_id}."
        )
        
        if capability.flags:
            citation_text += f" Validation flags: {', '.join(capability.flags)}."
        
        return citation_text
    
    def export_citations_markdown(
        self,
        citations: Dict,
        output_path: str
    ):
        """
        Export citations as Markdown document
        """
        with open(output_path, 'w') as f:
            f.write(f"# Citations: {citations.get('analysis_type', 'Analysis')}\n\n")
            
            # Findings
            if 'findings' in citations:
                f.write("## Key Findings\n\n")
                for finding in citations['findings']:
                    f.write(f"- {finding}\n")
                f.write("\n")
            
            # Data sources
            if 'data_sources' in citations:
                f.write("## Data Sources\n\n")
                sources = citations['data_sources']
                f.write(f"- **Facilities Analyzed**: {sources['facilities_analyzed']}\n")
                f.write(f"- **Regions Covered**: {sources['regions_covered']}\n\n")
            
            # Methodology
            if 'methodology' in citations:
                f.write("## Methodology\n\n")
                method = citations['methodology']
                f.write(f"- **Extraction Model**: {method.get('extraction_model', 'N/A')}\n")
                f.write(f"- **Embedding Model**: {method.get('embedding_model', 'N/A')}\n")
                f.write(f"- **Trust Threshold**: {method.get('trust_threshold', 'N/A')}\n")
                f.write("- **Validation Layers**:\n")
                for layer in method.get('validation_layers', []):
                    f.write(f"  - {layer}\n")
                f.write("\n")
            
            # Facilities
            if 'data_sources' in citations and 'facilities' in citations['data_sources']:
                f.write("## Facility References\n\n")
                for facility in citations['data_sources']['facilities']:
                    f.write(f"### {facility['name']} (ID: {facility['id']})\n")
                    f.write(f"- **Region**: {facility['region']}\n")
                    f.write(f"- **Capabilities Extracted**: {facility['capabilities_extracted']}\n\n")
            
            # Capability citations (if facility-level)
            if 'capabilities' in citations:
                f.write("## Capability Citations\n\n")
                for cap_citation in citations['capabilities']:
                    f.write(f"### {cap_citation['capability'].replace('_', ' ').title()}\n")
                    f.write(f"{cap_citation['citation_text']}\n\n")
        
        print(f"Citations exported to: {output_path}")
    
    def export_citations_json(
        self,
        citations: Dict,
        output_path: str
    ):
        """
        Export citations as JSON
        """
        import json
        
        with open(output_path, 'w') as f:
            json.dump(citations, f, indent=2)
        
        print(f"Citations exported to: {output_path}")


if __name__ == "__main__":
    # Test citation generation
    from schemas import ExtractedCapability, FacilityWithCapabilities
    
    test_capability = ExtractedCapability(
        capability="emergency_care",
        evidence=[
            "24-hour emergency department with 3 doctors",
            "Equipped with resuscitation equipment"
        ],
        confidence=0.9,
        availability="available",
        dependencies=["basic_consultation"],
        flags=[],
        facility_id="test_001",
        facility_name="Test Hospital",
        region="Greater Accra",
        source_row_id="test_001"
    )
    
    test_facility = FacilityWithCapabilities(
        facility_id="test_001",
        facility_name="Test District Hospital",
        region="Greater Accra",
        district="Accra Metro",
        ownership="Government",
        facility_type="District Hospital",
        capabilities=[test_capability],
        raw_data="Test data"
    )
    
    generator = CitationGenerator()
    
    # Generate facility citations
    citations = generator.generate_facility_citations(test_facility)
    
    print("Facility Citations:")
    print(f"Facility: {citations['facility']['name']}")
    print(f"Total Capabilities: {citations['summary']['total_capabilities']}")
    print(f"\nCapability Citation:")
    print(citations['capabilities'][0]['citation_text'])
    
    # Export as Markdown
    generator.export_citations_markdown(citations, "output/test_citations.md")
