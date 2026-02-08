"""
Main IDP Agent Orchestrator - Entry point for medical desert analysis
"""
import os
import json
from typing import List, Dict, Optional
from pathlib import Path

from data_loader import load_and_preprocess_data
from embeddings import EmbeddingGenerator
from vector_store import VectorStore
from retriever import Retriever
from capability_extractor import CapabilityExtractor
from planner_agent import PlannerAgent
from medical_desert_detector import MedicalDesertDetector
from trust_scorer import TrustScorer
from config import GROQ_API_KEY, OUTPUT_DIR, VECTOR_DB_PATH


class IDPAgent:
    """
    Main Intelligent Document Parsing Agent for Ghana Medical Desert Analysis
    
    Orchestrates the full pipeline:
    1. Data loading and preprocessing
    2. Embedding generation and vector storage
    3. Retrieval-augmented extraction
    4. Multi-step reasoning and planning
    5. Medical desert detection
    6. Result synthesis and export
    """
    
    def __init__(
        self,
        rebuild_index: bool = False,
        vector_db_path: str = VECTOR_DB_PATH,
        output_dir: str = OUTPUT_DIR
    ):
        """
        Initialize the IDP Agent
        
        Args:
            rebuild_index: Whether to rebuild the vector index from scratch
            vector_db_path: Path to vector database
            output_dir: Path for output files
        """
        self.vector_db_path = vector_db_path
        self.output_dir = output_dir
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        print("🚀 Initializing IDP Agent...")
        
        # Step 1: Load data
        print("📊 Loading facilities data...")
        self.facilities_df = load_and_preprocess_data()
        print(f"   Loaded {len(self.facilities_df)} facilities")
        
        # Step 2: Initialize embeddings and vector store
        if rebuild_index or not os.path.exists(vector_db_path):
            print("🔨 Building vector index...")
            self._build_vector_index()
        else:
            print("✅ Loading existing vector index...")
        
        # Step 3: Initialize retriever
        print("🔍 Initializing retriever...")
        self.retriever = Retriever(db_path=vector_db_path)
        
        # Step 4: Initialize extractor
        print("🧠 Initializing capability extractor...")
        self.extractor = CapabilityExtractor(self.retriever, self.facilities_df)
        
        # Step 5: Initialize planner agent
        print("🎯 Initializing planner agent...")
        self.planner = PlannerAgent(self.extractor, GROQ_API_KEY)
        
        # Step 6: Initialize analyzers
        self.trust_scorer = TrustScorer()
        self.desert_detector = MedicalDesertDetector(self.trust_scorer)
        
        print("✅ IDP Agent initialized successfully!\n")
    
    def _build_vector_index(self):
        """Build vector index from facility contexts"""
        # Generate embeddings
        print("   Generating embeddings...")
        embedding_generator = EmbeddingGenerator()
        
        texts = self.facilities_df['facility_context'].tolist()
        embeddings = embedding_generator.generate_embeddings(texts)
        
        # Create metadata
        metadatas = [
            {
                'facility_id': row['row_id'],
                'facility_name': row['name'],
                'region': row.get('address_stateOrRegion', ''),
                'city': row.get('address_city', ''),
                'facility_type': row.get('organization_type', row.get('facilityTypeId', '')),
                'row_id': row['row_id'],
                'source_url': row.get('url', ''),
                'text': row['facility_context']
            }
            for _, row in self.facilities_df.iterrows()
        ]
        
        # Prepare embeddings data structure
        embeddings_data = {
            'embeddings': embeddings,
            'metadata': metadatas
        }
        
        # Store in vector database
        print("   Storing in vector database...")
        vector_store = VectorStore(db_path=self.vector_db_path)
        vector_store.create_table(embeddings_data)
        
        print("   ✅ Vector index built successfully")
    
    def query(self, query: str, top_k: int = 10) -> Dict:
        """
        Answer a natural language query about medical capabilities
        
        Args:
            query: Natural language query
            top_k: Number of facilities to retrieve
            
        Returns:
            Complete analysis with answer and evidence
        """
        print(f"\n🔍 Query: {query}")
        print("=" * 80)
        
        # Use planner agent for complex queries
        results = self.planner.answer_query(query)
        
        return results
    
    def find_capability_deserts(
        self,
        capability: str,
        min_trust: float = 0.7
    ) -> Dict:
        """
        Find regions lacking a specific capability
        
        Args:
            capability: Capability to check (e.g., 'emergency_care')
            min_trust: Minimum trust score threshold
            
        Returns:
            Analysis of capability gaps by region
        """
        print(f"\n🔍 Finding regions without: {capability}")
        print("=" * 80)
        
        # Get all facilities
        all_facilities = self.extractor.extract_for_query(
            f"facilities with {capability.replace('_', ' ')}",
            top_k=100
        )
        
        # Analyze capability distribution
        analysis = self.desert_detector.identify_capability_deserts(
            all_facilities,
            capability,
            min_trust
        )
        
        return analysis
    
    def analyze_region(
        self,
        region: str,
        min_trust: float = 0.7
    ) -> Dict:
        """
        Analyze medical capability coverage in a specific region
        
        Args:
            region: Region name (e.g., 'Greater Accra')
            min_trust: Minimum trust score threshold
            
        Returns:
            Region analysis with capability gaps
        """
        print(f"\n📍 Analyzing region: {region}")
        print("=" * 80)
        
        # Get facilities in this region
        region_facilities = self.extractor.extract_for_query(
            f"facilities in {region}",
            top_k=50
        )
        
        # Analyze region
        analysis = self.desert_detector.analyze_region(
            region_facilities,
            region,
            min_trust
        )
        
        return analysis
    
    def find_all_medical_deserts(
        self,
        min_trust: float = 0.7
    ) -> Dict:
        """
        Identify all medical desert regions in Ghana
        
        Args:
            min_trust: Minimum trust score threshold
            
        Returns:
            Complete medical desert analysis
        """
        print("\n🏜️  Finding all medical deserts...")
        print("=" * 80)
        
        # Get all facilities
        all_facilities = self.extractor.extract_for_query(
            "all healthcare facilities",
            top_k=200
        )
        
        # Analyze all regions
        analysis = self.desert_detector.analyze_all_regions(
            all_facilities,
            min_trust
        )
        
        return analysis
    
    def export_results(self, results: Dict, filename: str):
        """Export results to JSON file"""
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_path}")
        
        return output_path
    
    def generate_report(self, analysis_type: str = "full") -> Dict:
        """
        Generate comprehensive analysis report
        
        Args:
            analysis_type: Type of report ('full', 'deserts', 'capabilities')
            
        Returns:
            Complete report with all analyses
        """
        print("\n📊 Generating comprehensive report...")
        print("=" * 80)
        
        report = {
            'analysis_type': analysis_type,
            'total_facilities': len(self.facilities_df),
            'regions_analyzed': self.facilities_df['address_stateOrRegion'].nunique()
        }
        
        if analysis_type in ['full', 'deserts']:
            # Medical desert analysis
            print("   Analyzing medical deserts...")
            desert_analysis = self.find_all_medical_deserts()
            report['medical_deserts'] = desert_analysis
        
        if analysis_type in ['full', 'capabilities']:
            # Critical capability analysis
            print("   Analyzing critical capabilities...")
            from ontology import CRITICAL_CAPABILITIES
            
            capability_analyses = {}
            for capability in CRITICAL_CAPABILITIES:
                analysis = self.find_capability_deserts(capability)
                capability_analyses[capability] = analysis
            
            report['capability_gaps'] = capability_analyses
        
        print("   ✅ Report generated successfully")
        
        return report


def main():
    """Main entry point for running the IDP agent"""
    
    # Initialize agent
    agent = IDPAgent(rebuild_index=False)
    
    # Example queries
    print("\n" + "=" * 80)
    print("EXAMPLE ANALYSES")
    print("=" * 80)
    
    # Query 1: General medical desert detection
    print("\n1️⃣  Finding all medical deserts...")
    deserts = agent.find_all_medical_deserts()
    print(f"\n   Found {deserts['desert_regions_count']} medical desert regions:")
    for desert in deserts['desert_regions'][:5]:
        print(f"   - {desert['region']} ({desert['severity']})")
    
    # Query 2: Specific capability gap
    print("\n2️⃣  Finding emergency care gaps...")
    emergency_gaps = agent.find_capability_deserts('emergency_care')
    print(f"\n   Regions without emergency care:")
    for region in emergency_gaps['regions_without_capability'][:5]:
        print(f"   - {region}")
    
    # Query 3: Natural language query
    print("\n3️⃣  Natural language query...")
    query_result = agent.query("Which regions need urgent maternity care investment?")
    print(f"\n   Answer: {query_result['answer']}")
    
    # Generate full report
    print("\n4️⃣  Generating comprehensive report...")
    report = agent.generate_report(analysis_type='full')
    
    # Export results
    agent.export_results(report, 'ghana_medical_desert_analysis.json')
    
    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
