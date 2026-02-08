"""
Interactive Streamlit Demo for Ghana Medical Desert IDP Agent
Beautiful UI for exploring healthcare facility capabilities and medical deserts
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import sys
from typing import Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from main import IDPAgent
from config import OUTPUT_DIR

# Page configuration
st.set_page_config(
    page_title="Ghana Medical Desert IDP Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .query-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .finding-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .desert-card {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
    }
    .critical-card {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        font-size: 1.1rem;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'query_results' not in st.session_state:
    st.session_state.query_results = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

@st.cache_resource
def load_agent():
    """Load the IDP Agent (cached)"""
    with st.spinner("🚀 Initializing Ghana Medical Desert IDP Agent..."):
        agent = IDPAgent()
        return agent

def create_metric_card(value, label, color="blue"):
    """Create a styled metric card"""
    return f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """

def main():
    # Header
    st.markdown('<div class="main-header">🏥 Ghana Medical Desert IDP Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Intelligent Detection & Planning for Healthcare Access Gaps</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Flag_of_Ghana.svg/320px-Flag_of_Ghana.svg.png", width=100)
        st.title("⚙️ Configuration")
        
        # Analysis settings
        st.subheader("Analysis Settings")
        min_trust = st.slider("Minimum Trust Score", 0.0, 1.0, 0.7, 0.05)
        top_k = st.slider("Results to Retrieve", 10, 200, 100, 10)
        
        st.divider()
        
        # Quick stats
        st.subheader("📊 Quick Stats")
        if st.session_state.agent:
            st.metric("Total Facilities", len(st.session_state.agent.facilities_df))
            st.metric("Regions", st.session_state.agent.facilities_df['address_stateOrRegion'].nunique())
            st.metric("VF Compliance", "100%", delta="✅")
        
        st.divider()
        
        # Sample queries
        st.subheader("💡 Sample Queries")
        
        st.markdown("**🚨 Emergency & Critical Care:**")
        emergency_queries = [
            "Which regions have the worst emergency care?",
            "Find facilities with ambulance services",
            "Hospitals with ICU capabilities",
            "Emergency care coverage in Greater Accra"
        ]
        for q in emergency_queries:
            if st.button(q, key=f"sample_{q}", use_container_width=True):
                st.session_state.query_input = q
        
        st.markdown("**👶 Maternal & Child Health:**")
        maternal_queries = [
            "Find hospitals with maternity services",
            "Areas lacking child immunization",
            "Facilities with neonatal care",
            "C-section delivery capabilities"
        ]
        for q in maternal_queries:
            if st.button(q, key=f"sample_{q}", use_container_width=True):
                st.session_state.query_input = q
        
        st.markdown("**🔬 Diagnostic Services:**")
        diagnostic_queries = [
            "Regions with good laboratory services",
            "Facilities with X-ray equipment",
            "Blood bank availability",
            "CT scan and MRI facilities"
        ]
        for q in diagnostic_queries:
            if st.button(q, key=f"sample_{q}", use_container_width=True):
                st.session_state.query_input = q
        
        st.markdown("**🏥 General Healthcare:**")
        general_queries = [
            "Medical deserts in Ghana",
            "Private hospitals in Ashanti region",
            "Pharmacies in rural areas",
            "Dental clinics availability"
        ]
        for q in general_queries:
            if st.button(q, key=f"sample_{q}", use_container_width=True):
                st.session_state.query_input = q
        
        st.markdown("**🎯 Specific Conditions:**")
        specific_queries = [
            "Facilities treating malaria",
            "HIV/AIDS treatment centers",
            "Tuberculosis care availability",
            "Mental health services"
        ]
        for q in specific_queries:
            if st.button(q, key=f"sample_{q}", use_container_width=True):
                st.session_state.query_input = q
        
        st.markdown("**📊 Comparative Analysis:**")
        comparative_queries = [
            "Compare healthcare in urban vs rural areas",
            "Best equipped hospitals in Ghana",
            "Regions with poorest healthcare access",
            "Public vs private facility distribution"
        ]
        for q in comparative_queries:
            if st.button(q, key=f"sample_{q}", use_container_width=True):
                st.session_state.query_input = q
    
    # Initialize agent
    if st.session_state.agent is None:
        st.session_state.agent = load_agent()
        st.success("✅ Agent initialized successfully!")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Query Analysis", "🏜️ Medical Deserts", "📊 Regional Analysis", "📈 Visualizations"])
    
    # Tab 1: Query Analysis
    with tab1:
        st.header("Natural Language Query")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            query = st.text_input(
                "Ask a question about Ghana's healthcare facilities:",
                placeholder="e.g., Which regions have the worst emergency care coverage?",
                key="query_input"
            )
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            analyze_button = st.button("🔍 Analyze", type="primary")
        
        if analyze_button and query:
            with st.spinner("🧠 Processing your query..."):
                try:
                    # Run query
                    results = st.session_state.agent.query(query)
                    st.session_state.query_results = results
                    
                    # Display answer
                    st.markdown('<div class="query-box">', unsafe_allow_html=True)
                    st.markdown("### 💡 Answer")
                    st.write(results.get('answer', 'No answer generated.'))
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Key findings
                    if results.get('key_findings'):
                        st.markdown("### 🔑 Key Findings")
                        for finding in results['key_findings']:
                            st.markdown(f'<div class="finding-card">✓ {finding}</div>', unsafe_allow_html=True)
                    
                    # Relevant facilities
                    if results.get('facilities'):
                        st.markdown("### 🏥 Relevant Facilities")
                        facilities_df = pd.DataFrame([
                            {
                                'Name': f.name,
                                'Region': f.address_stateOrRegion or 'N/A',
                                'City': f.address_city or 'N/A',
                                'Type': f.facilityTypeId or f.organization_type or 'N/A',
                                'Capabilities': len(f.capabilities)
                            }
                            for f in results['facilities'][:10]
                        ])
                        st.dataframe(facilities_df, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"❌ Error processing query: {str(e)}")
        
        elif analyze_button:
            st.warning("⚠️ Please enter a query first!")
    
    # Tab 2: Medical Deserts
    with tab2:
        st.header("Medical Desert Detection")
        
        if st.button("🔍 Find All Medical Deserts", type="primary"):
            with st.spinner("🏜️ Analyzing medical deserts across Ghana..."):
                try:
                    deserts = st.session_state.agent.find_all_medical_deserts(min_trust=min_trust)
                    
                    # Metrics row
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(create_metric_card(deserts['total_regions'], "Total Regions"), unsafe_allow_html=True)
                    with col2:
                        st.markdown(create_metric_card(deserts['desert_regions_count'], "Medical Deserts"), unsafe_allow_html=True)
                    with col3:
                        coverage = ((deserts['total_regions'] - deserts['desert_regions_count']) / deserts['total_regions'] * 100) if deserts['total_regions'] > 0 else 0
                        st.markdown(create_metric_card(f"{coverage:.1f}%", "Coverage Rate"), unsafe_allow_html=True)
                    with col4:
                        facilities_analyzed = len(deserts.get('all_facilities', []))
                        st.markdown(create_metric_card(facilities_analyzed, "Facilities Analyzed"), unsafe_allow_html=True)
                    
                    st.divider()
                    
                    # Desert regions
                    if deserts.get('desert_regions'):
                        st.markdown("### 🚨 Critical Medical Deserts")
                        for desert in deserts['desert_regions'][:10]:
                            severity_emoji = "🔴" if desert['severity'] == 'critical' else "🟡" if desert['severity'] == 'high' else "🟢"
                            st.markdown(f"""
                            <div class="{'critical-card' if desert['severity'] == 'critical' else 'desert-card'}">
                                <strong>{severity_emoji} {desert['region']}</strong> - {desert['severity'].upper()}<br>
                                <small>Missing: {', '.join(desert.get('missing_capabilities', [])[:3])}...</small><br>
                                <small>Facilities: {desert.get('facilities_count', 0)} | Coverage: {desert.get('coverage_percentage', 0):.1f}%</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("✅ No medical deserts found with current criteria!")
                    
                    # Map visualization
                    if deserts.get('desert_regions'):
                        st.markdown("### 🗺️ Geographic Distribution")
                        desert_data = pd.DataFrame(deserts['desert_regions'])
                        fig = px.bar(
                            desert_data.head(10),
                            x='region',
                            y='coverage_percentage',
                            color='severity',
                            title='Medical Desert Coverage by Region',
                            labels={'coverage_percentage': 'Coverage %', 'region': 'Region'},
                            color_discrete_map={'critical': '#dc3545', 'high': '#ffc107', 'medium': '#17a2b8'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                except Exception as e:
                    st.error(f"❌ Error analyzing medical deserts: {str(e)}")
    
    # Tab 3: Regional Analysis
    with tab3:
        st.header("Regional Healthcare Coverage")
        
        # Critical capabilities analysis
        st.subheader("🎯 Critical Capabilities Coverage")
        
        critical_caps = [
            'emergency_care',
            'maternity_delivery',
            'child_immunization',
            'laboratory_services',
            'pharmacy'
        ]
        
        selected_capability = st.selectbox("Select Capability:", critical_caps)
        
        if st.button("📊 Analyze Coverage", type="primary"):
            with st.spinner(f"Analyzing {selected_capability} coverage..."):
                try:
                    gaps = st.session_state.agent.find_capability_deserts(selected_capability, min_trust=min_trust)
                    
                    # Metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(create_metric_card(len(gaps['regions_with_capability']), "Regions WITH"), unsafe_allow_html=True)
                    with col2:
                        st.markdown(create_metric_card(len(gaps['regions_without_capability']), "Regions WITHOUT"), unsafe_allow_html=True)
                    with col3:
                        st.markdown(create_metric_card(f"{gaps['coverage_percentage']:.1f}%", "Coverage"), unsafe_allow_html=True)
                    
                    st.divider()
                    
                    # Lists
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### ✅ Regions WITH Capability")
                        for region in gaps['regions_with_capability'][:10]:
                            st.markdown(f'<div class="finding-card">✓ {region}</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("### ❌ Regions WITHOUT Capability")
                        for region in gaps['regions_without_capability'][:10]:
                            st.markdown(f'<div class="desert-card">✗ {region}</div>', unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"❌ Error analyzing capability: {str(e)}")
        
        st.divider()
        
        # Facility data explorer
        st.subheader("🔎 Facility Data Explorer")
        
        df = st.session_state.agent.facilities_df
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            regions = ['All'] + sorted(df['address_stateOrRegion'].dropna().unique().tolist())
            selected_region = st.selectbox("Filter by Region:", regions)
        with col2:
            org_types = ['All'] + sorted(df['organization_type'].dropna().unique().tolist())
            selected_type = st.selectbox("Filter by Type:", org_types)
        
        # Apply filters
        filtered_df = df.copy()
        if selected_region != 'All':
            filtered_df = filtered_df[filtered_df['address_stateOrRegion'] == selected_region]
        if selected_type != 'All':
            filtered_df = filtered_df[filtered_df['organization_type'] == selected_type]
        
        # Display
        st.metric("Filtered Facilities", len(filtered_df))
        display_df = filtered_df[['name', 'address_stateOrRegion', 'address_city', 'organization_type', 'facilityTypeId']].head(50)
        st.dataframe(display_df, use_container_width=True)
    
    # Tab 4: Visualizations
    with tab4:
        st.header("Healthcare Analytics Dashboard")
        
        df = st.session_state.agent.facilities_df
        
        # Regional distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📍 Facilities by Region")
            region_counts = df['address_stateOrRegion'].value_counts().head(10)
            fig1 = px.bar(
                x=region_counts.values,
                y=region_counts.index,
                orientation='h',
                title='Top 10 Regions by Facility Count',
                labels={'x': 'Number of Facilities', 'y': 'Region'}
            )
            fig1.update_traces(marker_color='#667eea')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.subheader("🏥 Facility Types")
            type_counts = df['organization_type'].value_counts().head(10)
            fig2 = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title='Distribution by Facility Type'
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Operator type distribution
        st.subheader("🏛️ Public vs Private Facilities")
        operator_counts = df['operatorTypeId'].value_counts()
        fig3 = go.Figure(data=[
            go.Bar(name='Facilities', x=operator_counts.index, y=operator_counts.values, marker_color='#764ba2')
        ])
        fig3.update_layout(title='Facilities by Operator Type', xaxis_title='Operator Type', yaxis_title='Count')
        st.plotly_chart(fig3, use_container_width=True)
        
        # Capacity analysis
        st.subheader("🛏️ Facility Capacity")
        capacity_df = df[df['capacity'].notna()].copy()
        if not capacity_df.empty:
            fig4 = px.histogram(
                capacity_df,
                x='capacity',
                nbins=20,
                title='Distribution of Inpatient Bed Capacity',
                labels={'capacity': 'Bed Capacity'}
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No capacity data available")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p><strong>Ghana Medical Desert IDP Agent</strong> | 100% VF Compliant | Powered by Groq & LanceDB</p>
        <p>🔬 Built with: Python, Streamlit, Groq llama-3.3-70b, BAAI/bge-large-en-v1.5</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
