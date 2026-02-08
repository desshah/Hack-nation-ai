"""
Planner Agent - Orchestrates multi-step reasoning for complex queries
"""
from typing import List, Dict, Optional
from groq import Groq
from schemas import FacilityWithCapabilities
from capability_extractor import CapabilityExtractor
from validator import CapabilityValidator
from trust_scorer import TrustScorer
from medical_desert_detector import MedicalDesertDetector
from ontology import CRITICAL_CAPABILITIES, normalize_capability
import json

class PlannerAgent:
    """
    Orchestrates complex medical desert analysis queries through multi-step reasoning:
    1. Query understanding and decomposition
    2. Retrieval planning
    3. Extraction coordination
    4. Validation and trust scoring
    5. Region/district aggregation
    6. Medical desert detection
    7. Answer synthesis with citations
    """
    
    SYSTEM_PROMPT = """You are a medical infrastructure analysis expert helping identify healthcare gaps in Ghana.

Your role is to:
1. Understand complex queries about medical capabilities and access
2. Break down queries into retrieval and analysis steps
3. Identify which capabilities and regions to analyze
4. Determine appropriate trust thresholds
5. Synthesize findings into actionable insights

Available analysis capabilities:
- extract_for_query: Find facilities matching capability queries
- analyze_region: Analyze capability coverage in a specific region
- analyze_all_regions: Identify all medical desert regions
- identify_capability_deserts: Find regions lacking specific capabilities
- validate_facility: Check consistency of facility claims
- calculate_trust_scores: Assess reliability of capability claims

Output your plan as JSON with:
{
  "query_type": "region_analysis|capability_search|desert_detection|facility_validation",
  "steps": [
    {
      "action": "extract_for_query|analyze_region|etc",
      "parameters": {"param": "value"},
      "reasoning": "why this step"
    }
  ],
  "expected_insights": ["what we'll learn"]
}"""
    
    def __init__(
        self,
        extractor: CapabilityExtractor,
        api_key: str,
        model: str = "llama-3.3-70b-versatile"
    ):
        self.extractor = extractor
        self.validator = CapabilityValidator()
        self.trust_scorer = TrustScorer()
        self.desert_detector = MedicalDesertDetector(self.trust_scorer)
        self.client = Groq(api_key=api_key)
        self.model = model
    
    def create_plan(self, query: str) -> Dict:
        """
        Create execution plan for a complex query
        
        Args:
            query: Natural language query about medical capabilities
            
        Returns:
            Execution plan as dictionary
        """
        # Use LLM to create plan
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"Create an analysis plan for: {query}"}
            ],
            temperature=0.3,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        plan = json.loads(response.choices[0].message.content)
        return plan
    
    def execute_plan(self, plan: Dict, query: str) -> Dict:
        """
        Execute the planned analysis steps
        
        Returns:
            Analysis results with findings and evidence
        """
        results = {
            'query': query,
            'plan': plan,
            'step_results': [],
            'findings': [],
            'evidence': []
        }
        
        # Execute each step
        for step in plan['steps']:
            action = step['action']
            params = step['parameters']
            
            step_result = None
            
            if action == 'extract_for_query':
                # Extract facilities matching capability query
                facilities = self.extractor.extract_for_query(
                    params.get('query', query),
                    top_k=params.get('top_k', 10)
                )
                step_result = {
                    'action': action,
                    'facilities_found': len(facilities),
                    'facilities': [
                        {
                            'name': f.facility_name,
                            'region': f.region,
                            'district': f.district,
                            'capabilities_count': len(f.capabilities)
                        }
                        for f in facilities
                    ]
                }
                results['facilities'] = facilities
            
            elif action == 'analyze_region':
                # Analyze specific region
                region = params.get('region')
                facilities = results.get('facilities', [])
                
                analysis = self.desert_detector.analyze_region(
                    facilities,
                    region,
                    min_trust=params.get('min_trust', 0.7)
                )
                step_result = analysis
            
            elif action == 'analyze_all_regions':
                # Analyze all regions for deserts
                facilities = results.get('facilities', [])
                
                analysis = self.desert_detector.analyze_all_regions(
                    facilities,
                    min_trust=params.get('min_trust', 0.7)
                )
                step_result = analysis
            
            elif action == 'identify_capability_deserts':
                # Find regions lacking specific capability
                capability = params.get('capability')
                facilities = results.get('facilities', [])
                
                analysis = self.desert_detector.identify_capability_deserts(
                    facilities,
                    capability,
                    min_trust=params.get('min_trust', 0.7)
                )
                step_result = analysis
            
            elif action == 'validate_facilities':
                # Validate facility claims
                facilities = results.get('facilities', [])
                
                validation = self.validator.validate_batch(facilities)
                step_result = validation
            
            elif action == 'calculate_trust_scores':
                # Score facility reliability
                facilities = results.get('facilities', [])
                
                scores = self.trust_scorer.score_batch(facilities)
                step_result = scores
            
            results['step_results'].append({
                'step': step,
                'result': step_result
            })
        
        # Synthesize findings
        results['findings'] = self._synthesize_findings(results)
        
        return results
    
    def answer_query(self, query: str) -> Dict:
        """
        Full pipeline: plan -> execute -> synthesize
        
        Returns:
            Complete analysis with natural language answer
        """
        # Create plan
        plan = self.create_plan(query)
        
        # Execute plan
        results = self.execute_plan(plan, query)
        
        # Generate natural language answer
        answer = self._generate_answer(query, results)
        results['answer'] = answer
        
        return results
    
    def _synthesize_findings(self, results: Dict) -> List[str]:
        """Extract key findings from step results"""
        findings = []
        
        for step_result in results['step_results']:
            result = step_result['result']
            
            if isinstance(result, dict):
                # Desert analysis findings
                if 'is_desert' in result and result['is_desert']:
                    findings.append(
                        f"Medical desert detected in {result.get('region', 'unknown')}: "
                        f"{len(result.get('critical_capabilities_missing', []))} critical capabilities missing"
                    )
                
                # Capability coverage findings
                if 'coverage_percentage' in result:
                    coverage = result['coverage_percentage']
                    if coverage < 50:
                        findings.append(
                            f"Low capability coverage: {coverage:.1f}% in {result.get('region', 'analyzed area')}"
                        )
                
                # Validation findings
                if 'facilities_with_warnings' in result:
                    warnings = result['facilities_with_warnings']
                    if warnings > 0:
                        findings.append(
                            f"Data quality concern: {warnings} facilities have validation warnings"
                        )
        
        return findings
    
    def _generate_answer(self, query: str, results: Dict) -> str:
        """Generate natural language answer using LLM"""
        # Prepare context from results
        context = {
            'findings': results['findings'],
            'step_results': [
                {
                    'action': step['step']['action'],
                    'summary': self._summarize_step_result(step['result'])
                }
                for step in results['step_results']
            ]
        }
        
        prompt = f"""Based on the analysis results, answer this query concisely:

Query: {query}

Findings:
{json.dumps(context, indent=2)}

Provide a clear, evidence-based answer that:
1. Directly addresses the query
2. Highlights key insights and gaps
3. Mentions specific regions/facilities where relevant
4. Notes any data quality concerns
5. Suggests implications for healthcare access"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a healthcare analyst providing concise, evidence-based insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def _summarize_step_result(self, result) -> str:
        """Create brief summary of step result"""
        if isinstance(result, dict):
            if 'facilities_found' in result:
                return f"Found {result['facilities_found']} facilities"
            elif 'is_desert' in result:
                return f"Desert: {result['is_desert']}, Severity: {result.get('severity', 'unknown')}"
            elif 'total_regions' in result:
                return f"Analyzed {result['total_regions']} regions, {result.get('desert_regions_count', 0)} deserts found"
            elif 'total_facilities' in result:
                return f"Validated {result['total_facilities']} facilities"
        
        return "Analysis complete"


if __name__ == "__main__":
    # Test planner agent
    from data_loader import load_and_preprocess_data
    from retriever import Retriever
    from config import GROQ_API_KEY
    
    print("Loading facilities data...")
    facilities_df = load_and_preprocess_data()
    
    print("Initializing retriever...")
    retriever = Retriever(db_path="vector_db")
    
    print("Creating capability extractor...")
    extractor = CapabilityExtractor(retriever, facilities_df)
    
    print("Creating planner agent...")
    planner = PlannerAgent(extractor, GROQ_API_KEY)
    
    # Test query
    test_query = "Which regions in Ghana lack emergency care capabilities?"
    
    print(f"\nQuery: {test_query}")
    print("Creating plan...")
    
    plan = planner.create_plan(test_query)
    print(f"\nPlan: {json.dumps(plan, indent=2)}")
    
    print("\nExecuting plan...")
    results = planner.answer_query(test_query)
    
    print(f"\nAnswer: {results['answer']}")
    print(f"\nKey Findings:")
    for finding in results['findings']:
        print(f"  - {finding}")
