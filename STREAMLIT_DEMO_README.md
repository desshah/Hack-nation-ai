# 🏥 Ghana Medical Desert IDP Agent - Interactive Streamlit Demo

## 🚀 Quick Start

### Run the Interactive UI
```bash
streamlit run streamlit_demo.py
```

Or with full path:
```bash
/opt/anaconda3/bin/python -m streamlit run streamlit_demo.py --server.port 8501
```

### Access the App
- **Local URL**: http://localhost:8501
- **Network URL**: http://192.168.1.215:8501 (accessible from other devices on your network)

## ✨ Features

### 🔍 Tab 1: Query Analysis
- **Natural Language Queries**: Ask questions in plain English
- **Sample Queries**: Click predefined queries to get started quickly
- **AI-Powered Answers**: Get comprehensive answers powered by Groq llama-3.3-70b
- **Key Findings**: Automatically extracted insights
- **Facility Results**: View matching facilities in a clean table

**Sample Queries:**
- "Which regions have the worst emergency care?"
- "Find hospitals with maternity services"
- "Areas lacking child immunization"
- "Regions with good laboratory services"
- "Medical deserts in Ghana"

### 🏜️ Tab 2: Medical Desert Detection
- **One-Click Analysis**: Find all medical deserts across Ghana
- **Beautiful Metrics**: 4 key metrics displayed in gradient cards
  - Total Regions
  - Medical Deserts Found
  - Coverage Rate
  - Facilities Analyzed
- **Desert Cards**: Color-coded by severity (🔴 Critical, 🟡 High, 🟢 Medium)
- **Interactive Charts**: Bar charts showing regional coverage

### 📊 Tab 3: Regional Analysis
- **Critical Capabilities**: Analyze coverage of 5 critical healthcare capabilities
  - Emergency Care
  - Maternity Delivery
  - Child Immunization
  - Laboratory Services
  - Pharmacy
- **Side-by-Side Comparison**: See regions WITH and WITHOUT each capability
- **Facility Explorer**: Browse and filter all 987 facilities
  - Filter by Region
  - Filter by Facility Type
  - Display up to 50 results

### 📈 Tab 4: Visualizations
- **Interactive Plotly Charts**:
  - Top 10 Regions by Facility Count (horizontal bar chart)
  - Facility Types Distribution (pie chart)
  - Public vs Private Facilities (bar chart)
  - Inpatient Bed Capacity Distribution (histogram)

## 🎨 UI Design Features

### Modern Design
- **Gradient Cards**: Beautiful purple gradient metric cards
- **Color-Coded Alerts**: Green for success, yellow for warnings, red for critical
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Professional Styling**: Custom CSS for a polished look

### Navigation
- **4 Main Tabs**: Easy navigation between different analyses
- **Sidebar**: Configuration and quick stats
- **Sample Queries**: One-click query suggestions

### Interactive Elements
- **Sliders**: Adjust trust score and result count
- **Buttons**: Trigger analyses with styled primary buttons
- **Data Tables**: Browse facilities with pandas dataframes
- **Charts**: Interactive Plotly visualizations with zoom/pan

## 🔧 Configuration Options

### Sidebar Settings
- **Minimum Trust Score**: 0.0 to 1.0 (default: 0.7)
- **Results to Retrieve**: 10 to 200 (default: 100)

### Quick Stats
- Total Facilities: 987
- Regions: 53
- VF Compliance: 100% ✅

## 📊 Data Sources

- **Dataset**: Ghana Healthcare Facilities from Virtue Foundation
- **Total Facilities**: 987
- **Data Fields**: 43 columns including:
  - VF Organization fields (name, phone, email, websites, etc.)
  - VF Address fields (line1, line2, city, region, country, etc.)
  - VF Facility fields (facilityTypeId, operatorTypeId, capacity, etc.)
  - VF Free-form fields (procedure, equipment, capability, specialties)

## 🚀 Technology Stack

- **UI Framework**: Streamlit 1.31+
- **Visualization**: Plotly Express
- **Backend**: Python 3.12
- **LLM**: Groq llama-3.3-70b-versatile
- **Embeddings**: BAAI/bge-large-en-v1.5 (1024 dimensions)
- **Vector DB**: LanceDB
- **Data Processing**: Pandas, NumPy

## 📸 Screenshot Highlights

### Main Dashboard
- Clean header with Ghana flag
- 4-tab navigation
- Sidebar with quick stats and settings

### Query Analysis
- Natural language input
- AI-generated answers
- Key findings cards
- Facility results table

### Medical Deserts
- 4 metric cards with gradients
- Color-coded desert cards by severity
- Interactive bar charts

### Regional Analysis
- Capability coverage comparison
- Facility data explorer with filters
- Side-by-side region lists

### Visualizations
- Multiple interactive Plotly charts
- Regional distribution
- Facility type breakdown
- Capacity analysis

## 🎯 Use Cases

1. **Healthcare Planning**: Identify gaps in healthcare coverage
2. **Resource Allocation**: Find regions needing more facilities
3. **Policy Making**: Data-driven decisions for healthcare policy
4. **Research**: Analyze healthcare access patterns
5. **Emergency Response**: Locate critical capability gaps

## 🔥 Key Benefits

✅ **100% VF Compliant**: Follows official Virtue Foundation specifications
✅ **Interactive**: Real-time analysis and visualization
✅ **Beautiful UI**: Modern, professional design
✅ **Fast**: Cached agent initialization for quick responses
✅ **Comprehensive**: Multiple analysis modes in one interface
✅ **Evidence-Based**: All results backed by facility data
✅ **User-Friendly**: No coding required, just click and explore

## 📝 Notes

- First load may take 30-60 seconds to initialize the agent
- Agent is cached for subsequent interactions
- All analyses run on local data (no external API calls except LLM)
- Visualizations are fully interactive (zoom, pan, hover for details)

## 🐛 Troubleshooting

### App Won't Start
```bash
# Install dependencies
pip install streamlit plotly pandas

# Run with full path
/opt/anaconda3/bin/python -m streamlit run streamlit_demo.py
```

### Port Already in Use
```bash
# Use different port
streamlit run streamlit_demo.py --server.port 8502
```

### Slow Performance
- First load is slower due to model initialization
- Subsequent interactions are fast due to caching
- Consider lowering "Results to Retrieve" slider

## 🎓 Learn More

- [Streamlit Documentation](https://docs.streamlit.io)
- [Plotly Documentation](https://plotly.com/python/)
- [Virtue Foundation](https://virtuefoundation.org)

---

**Built with ❤️ for Ghana Healthcare Access** | 100% VF Compliant | Powered by AI
