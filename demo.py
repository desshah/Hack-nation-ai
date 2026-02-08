"""
Demo Script - Demonstrates complete IDP pipeline with all features
"""
import os
from main import IDPAgent
from citation_generator import CitationGenerator
from visualizer import MedicalDesertVisualizer


def demo_complete_pipeline():
    """
    Demonstrate the complete IDP agent pipeline:
    1. Initialize agent
    2. Run queries
    3. Detect medical deserts
    4. Generate citations
    5. Create visualizations
    6. Export results
    """
    
    print("\n" + "=" * 80)
    print("🚀 GHANA MEDICAL DESERT IDP AGENT - COMPLETE DEMO")
    print("=" * 80)
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Step 1: Initialize Agent
    print("\n📦 Step 1: Initializing IDP Agent...")
    print("-" * 80)
    agent = IDPAgent(rebuild_index=False)
    citation_gen = CitationGenerator()
    visualizer = MedicalDesertVisualizer()
    
    # Step 2: Natural Language Query
    print("\n💬 Step 2: Natural Language Query Analysis")
    print("-" * 80)
    query = "Which regions in Ghana have the worst emergency care coverage?"
    print(f"Query: {query}")
    print("\nProcessing...")
    
    query_result = agent.query(query)
    
    print(f"\n✅ Answer:")
    print(query_result['answer'])
    
    if query_result.get('findings'):
        print(f"\n🔍 Key Findings:")
        for finding in query_result['findings'][:3]:
            print(f"  • {finding}")
    
    # Step 3: Find All Medical Deserts
    print("\n\n🏜️  Step 3: Medical Desert Detection")
    print("-" * 80)
    deserts = agent.find_all_medical_deserts(min_trust=0.7)
    
    print(f"\n📊 Summary:")
    print(f"  • Total Regions Analyzed: {deserts['total_regions']}")
    print(f"  • Medical Deserts Found: {deserts['desert_regions_count']}")
    
    if deserts['total_regions'] > 0:
        print(f"  • Coverage Rate: {((deserts['total_regions'] - deserts['desert_regions_count']) / deserts['total_regions'] * 100):.1f}%")
    else:
        print(f"  • Coverage Rate: N/A (no regions analyzed)")
    
    
    if deserts['desert_regions']:
        print(f"\n🚨 Critical Medical Deserts:")
        for desert in deserts['desert_regions'][:5]:
            print(f"  • {desert['region']} ({desert['severity'].upper()})")
            print(f"    Missing: {', '.join(desert['missing_capabilities'][:3])}...")
    
    # Step 4: Capability-Specific Analysis
    print("\n\n🏥 Step 4: Emergency Care Gap Analysis")
    print("-" * 80)
    emergency_gaps = agent.find_capability_deserts('emergency_care', min_trust=0.7)
    
    print(f"\n📈 Emergency Care Coverage:")
    print(f"  • Regions WITH Emergency Care: {len(emergency_gaps['regions_with_capability'])}")
    print(f"  • Regions WITHOUT Emergency Care: {len(emergency_gaps['regions_without_capability'])}")
    print(f"  • Coverage: {emergency_gaps['coverage_percentage']:.1f}%")
    
    if emergency_gaps['regions_without_capability']:
        print(f"\n⚠️  Regions Lacking Emergency Care:")
        for region in emergency_gaps['regions_without_capability'][:5]:
            print(f"  • {region}")
    
    # Step 5: Region Deep-Dive
    print("\n\n📍 Step 5: Region-Specific Analysis")
    print("-" * 80)
    
    # Analyze a specific region
    if deserts['desert_regions']:
        target_region = deserts['desert_regions'][0]['region']
        print(f"Analyzing: {target_region}")
        
        region_analysis = agent.analyze_region(target_region, min_trust=0.7)
        
        print(f"\n🔬 {target_region} Analysis:")
        print(f"  • Desert Status: {'YES' if region_analysis['is_desert'] else 'NO'} ({region_analysis['severity']})")
        print(f"  • Facilities: {region_analysis['facilities_count']}")
        print(f"  • Coverage: {region_analysis['coverage_percentage']:.1f}%")
        print(f"  • Capabilities Present: {len(region_analysis['critical_capabilities_present'])}/9")
        
        if region_analysis['critical_capabilities_missing']:
            print(f"\n  Missing Critical Capabilities:")
            for cap in region_analysis['critical_capabilities_missing']:
                print(f"    • {cap.replace('_', ' ').title()}")
    
    # Step 6: Generate Citations
    print("\n\n📝 Step 6: Generating Citations & Evidence")
    print("-" * 80)
    
    if 'facilities' in query_result:
        citations = citation_gen.generate_analysis_citations(
            query_result['facilities'],
            'medical_desert_analysis',
            query_result.get('findings', [])
        )
        
        # Export citations
        citation_gen.export_citations_markdown(citations, 'output/analysis_citations.md')
        citation_gen.export_citations_json(citations, 'output/analysis_citations.json')
        
        print(f"  ✅ Citations exported:")
        print(f"    • output/analysis_citations.md")
        print(f"    • output/analysis_citations.json")
    
    # Step 7: Create Visualizations
    print("\n\n📊 Step 7: Generating Visualizations")
    print("-" * 80)
    
    try:
        visualizer.create_summary_dashboard(deserts, output_dir='output')
        print("  ✅ Visualizations created:")
        print("    • output/medical_deserts_map.png")
        print("    • output/capability_coverage.png")
        print("    • output/region_comparison.png")
    except Exception as e:
        print(f"  ⚠️  Visualization error: {e}")
        print("    (Matplotlib may need display configuration)")
    
    # Step 8: Export Complete Report
    print("\n\n💾 Step 8: Exporting Complete Report")
    print("-" * 80)
    
    report = agent.generate_report(analysis_type='full')
    report_path = agent.export_results(report, 'ghana_medical_desert_full_report.json')
    
    print(f"  ✅ Complete report saved: {report_path}")
    
    # Final Summary
    print("\n\n" + "=" * 80)
    print("✅ DEMO COMPLETE - ALL COMPONENTS EXECUTED SUCCESSFULLY")
    print("=" * 80)
    
    print("\n📁 Generated Files:")
    print("  • output/ghana_medical_desert_full_report.json")
    print("  • output/analysis_citations.md")
    print("  • output/analysis_citations.json")
    print("  • output/medical_deserts_map.png")
    print("  • output/capability_coverage.png")
    print("  • output/region_comparison.png")
    
    print("\n🎯 Key Insights:")
    print(f"  • {deserts['desert_regions_count']} out of {deserts['total_regions']} regions are medical deserts")
    print(f"  • Emergency care coverage: {emergency_gaps['coverage_percentage']:.1f}%")
    if deserts.get('most_common_gaps'):
        top_gap = deserts['most_common_gaps'][0]
        print(f"  • Most common gap: {top_gap[0].replace('_', ' ')} (missing in {top_gap[1]} regions)")
    
    print("\n💡 Next Steps:")
    print("  1. Review detailed report: output/ghana_medical_desert_full_report.json")
    print("  2. Check citations for evidence: output/analysis_citations.md")
    print("  3. View visualizations in output/ directory")
    print("  4. Run web UI: python ui.py")
    print("  5. Use main.py for custom analyses")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    demo_complete_pipeline()
