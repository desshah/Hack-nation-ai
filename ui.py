"""
Simple Web UI for Medical Desert Analysis
Run with: python ui.py
Then open browser to http://localhost:5000
"""
from flask import Flask, render_template, request, jsonify
import json
from main import IDPAgent
from citation_generator import CitationGenerator
import os

app = Flask(__name__)

# Initialize IDP agent (singleton pattern)
agent = None
citation_gen = CitationGenerator()

def get_agent():
    """Lazy load agent on first request"""
    global agent
    if agent is None:
        print("Initializing IDP Agent...")
        agent = IDPAgent(rebuild_index=False)
    return agent


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/api/query', methods=['POST'])
def query():
    """Handle natural language query"""
    try:
        data = request.json
        query_text = data.get('query', '')
        
        if not query_text:
            return jsonify({'error': 'Query is required'}), 400
        
        # Get agent
        idp_agent = get_agent()
        
        # Execute query
        result = idp_agent.query(query_text)
        
        # Generate citations
        if 'facilities' in result:
            citations = citation_gen.generate_analysis_citations(
                result['facilities'],
                'query_analysis',
                result.get('findings', [])
            )
            result['citations'] = citations
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/deserts', methods=['GET'])
def find_deserts():
    """Find all medical deserts"""
    try:
        min_trust = float(request.args.get('min_trust', 0.7))
        
        idp_agent = get_agent()
        result = idp_agent.find_all_medical_deserts(min_trust=min_trust)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/region/<region_name>', methods=['GET'])
def analyze_region(region_name):
    """Analyze specific region"""
    try:
        min_trust = float(request.args.get('min_trust', 0.7))
        
        idp_agent = get_agent()
        result = idp_agent.analyze_region(region_name, min_trust=min_trust)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/capability/<capability>', methods=['GET'])
def capability_gaps(capability):
    """Find regions lacking specific capability"""
    try:
        min_trust = float(request.args.get('min_trust', 0.7))
        
        idp_agent = get_agent()
        result = idp_agent.find_capability_deserts(capability, min_trust=min_trust)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/regions', methods=['GET'])
def get_regions():
    """Get list of all regions"""
    try:
        idp_agent = get_agent()
        regions = sorted(idp_agent.facilities_df['region'].unique().tolist())
        
        return jsonify({'regions': regions})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/capabilities', methods=['GET'])
def get_capabilities():
    """Get list of critical capabilities"""
    from ontology import CRITICAL_CAPABILITIES
    
    return jsonify({'capabilities': CRITICAL_CAPABILITIES})


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("\n" + "=" * 80)
    print("🚀 Starting Medical Desert Analysis Web UI")
    print("=" * 80)
    print("\n📍 Open your browser to: http://localhost:5000")
    print("\n⚠️  Note: First request will be slow as the agent initializes\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')
