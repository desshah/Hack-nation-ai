# Ghana Medical Desert IDP Agent

**Intelligent Document Parsing (IDP) agent that identifies medical deserts and critical healthcare capability gaps in Ghana's healthcare system.**

## 🎯 Overview

This IDP agent goes far beyond simple search to:
- **Extract and verify** medical facility capabilities from messy, unstructured data
- **Identify infrastructure gaps** and medical deserts across Ghana's regions
- **Detect incomplete or suspicious claims** using multi-layer validation
- **Map where critical expertise is available** with trust-scored evidence
- **Reduce time for patients to receive lifesaving treatment by 100×**

Built for the **Virtue Foundation Ghana** healthcare infrastructure challenge.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    IDP Agent Pipeline                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Data Ingestion (987 facilities, 41+ fields)         │
│     └─> data_loader.py: Normalize & create contexts     │
│                                                          │
│  2. Embedding Generation (RAG Index)                    │
│     └─> embeddings.py: HuggingFace BGE-large-en-v1.5   │
│     └─> vector_store.py: LanceDB serverless storage    │
│                                                          │
│  3. Retrieval (Semantic Search)                         │
│     └─> retriever.py: Top-k similarity search          │
│                                                          │
│  4. Capability Extraction (Groq LLM)                    │
│     └─> extractor_agent.py: llama-3.3-70b structured   │
│     └─> capability_extractor.py: Orchestration         │
│                                                          │
│  5. Multi-Layer Validation                              │
│     └─> validator.py: Dependency & consistency checks   │
│     └─> trust_scorer.py: Evidence quality scoring      │
│                                                          │
│  6. Medical Desert Detection                            │
│     └─> medical_desert_detector.py: Region analysis    │
│                                                          │
│  7. Multi-Step Reasoning                                │
│     └─> planner_agent.py: Query decomposition          │
│                                                          │
│  8. Main Orchestrator                                   │
│     └─> main.py: End-to-end pipeline                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/desshah/Hack-nation-ai.git
cd Hack-nation-ai

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file:

```bash
cp .env.example .env
```

Add your Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run Analysis

```bash
python main.py
```

---

## 📊 Data Pipeline

### Input Data
- **Source**: `vf_ghana_enriched.csv`
- **Records**: 987 healthcare facilities
- **Columns**: 41+ fields including:
  - Name, region, district, ownership
  - Facility type, specialties, services
  - Diagnostic capabilities, equipment
  - Staff information, contact details

### Data Processing
```python
from data_loader import load_enriched_data

# Load and preprocess
facilities_df = load_enriched_data()

# Creates:
# - row_id: Unique identifier
# - facility_context: LLM-optimized searchable text
# - Normalized fields for consistency
```

### Output Schema
```python
class ExtractedCapability:
    capability: str              # Normalized capability name
    evidence: List[str]          # Supporting evidence from data
    confidence: float            # LLM confidence (0-1)
    availability: Literal        # available|limited|unavailable|unknown
    dependencies: List[str]      # Required prerequisite capabilities
    flags: List[str]             # Validation warnings
```

---

## 🔍 Usage Examples

### Example 1: Find All Medical Deserts

```python
from main import IDPAgent

agent = IDPAgent()

# Analyze all regions
deserts = agent.find_all_medical_deserts(min_trust=0.7)

print(f"Found {deserts['desert_regions_count']} medical deserts")
for desert in deserts['desert_regions']:
    print(f"  {desert['region']}: {desert['severity']}")
    print(f"    Missing: {desert['missing_capabilities']}")
```

### Example 2: Capability Gap Analysis

```python
# Find regions without emergency care
emergency_gaps = agent.find_capability_deserts('emergency_care')

print("Regions without emergency care:")
for region in emergency_gaps['regions_without_capability']:
    print(f"  - {region}")
```

### Example 3: Natural Language Query

```python
# Complex query with multi-step reasoning
result = agent.query(
    "Which districts in Upper East Region need urgent maternity care investment?"
)

print(result['answer'])
print("\nEvidence:")
for finding in result['findings']:
    print(f"  - {finding}")
```

### Example 4: Region Deep-Dive

```python
# Analyze specific region
analysis = agent.analyze_region('Northern Region', min_trust=0.7)

print(f"Region: {analysis['region']}")
print(f"Desert Status: {analysis['is_desert']} ({analysis['severity']})")
print(f"Coverage: {analysis['coverage_percentage']:.1f}%")
print(f"Facilities: {analysis['facilities_count']}")
print(f"\nMissing Capabilities:")
for cap in analysis['critical_capabilities_missing']:
    print(f"  - {cap}")
```

---

## 🧠 Core Components

### 1. Retriever (`retriever.py`)
- Semantic search over facility contexts
- Top-k similarity retrieval
- LanceDB vector database

### 2. Extraction Agent (`extractor_agent.py`)
- Groq llama-3.3-70b-versatile
- JSON-mode structured output
- Few-shot prompting with examples
- Extracts capabilities with evidence and confidence

### 3. Validator (`validator.py`)
- Dependency consistency checks
- Facility type appropriateness validation
- Evidence quality assessment
- Contradiction detection

### 4. Trust Scorer (`trust_scorer.py`)
Weighted trust score calculation:
- **Confidence** (30%): LLM extraction confidence
- **Evidence Quality** (25%): Specificity indicators (numbers, names, details)
- **Dependency Consistency** (20%): Required capabilities present
- **Availability** (15%): Service status
- **Flags Penalty** (10%): Validation warnings

### 5. Medical Desert Detector (`medical_desert_detector.py`)
Classification criteria:
- **Critical**: Missing 6+ critical capabilities
- **Severe**: Missing 4-5 critical capabilities
- **Moderate**: Missing 2-3 critical capabilities
- **Minimal**: Missing 0-1 critical capabilities

Critical capabilities tracked:
1. Emergency care
2. Basic surgery
3. Maternity/delivery
4. Laboratory services
5. ICU/critical care
6. Diagnostic imaging (X-ray)
7. Ambulance services
8. Blood transfusion
9. Specialist care

### 6. Planner Agent (`planner_agent.py`)
Multi-step reasoning:
1. Query understanding and decomposition
2. Retrieval planning
3. Extraction coordination
4. Validation and trust scoring
5. Region/district aggregation
6. Answer synthesis with citations

---

## 📈 Validation & Trust Metrics

### Validation Layers

**Layer 1: Dependency Validation**
- Surgery → requires anesthesia
- ICU → requires emergency_care
- Specialist care → requires basic_consultation

**Layer 2: Facility Type Constraints**
- CHPS compounds unlikely to have ICU, surgery
- District hospitals unlikely to have organ transplant
- Teaching hospitals expected to have advanced capabilities

**Layer 3: Evidence Quality**
- **High quality**: Specific numbers, named staff, 24/7 availability
- **Low quality**: Hedging language (may, possibly), vague terms

### Trust Score Components

```python
trust_score = (
    0.30 * confidence_score +
    0.25 * evidence_quality_score +
    0.20 * dependency_consistency_score +
    0.15 * availability_score -
    0.10 * flags_penalty
)
```

**Trust Categories:**
- **High Trust** (≥0.8): Strong evidence, consistent dependencies
- **Medium Trust** (0.5-0.8): Reasonable evidence, minor concerns
- **Low Trust** (<0.5): Weak evidence, validation issues

---

## 🎯 Medical Ontology

Defined in `ontology.py`:

- **60+ medical capabilities** mapped to standard terms
- **100+ synonym mappings** (e.g., "A&E" → "emergency_care")
- **Capability dependencies** (e.g., surgery requires anesthesia)
- **9 critical capabilities** for desert detection

---

## 📁 Project Structure

```
Hack-nation-ai/
├── data/
│   ├── Virtue Foundation Ghana v0.3 - Sheet1.csv  # Raw data
│   └── vf_ghana_enriched_final.csv                # Processed data
├── prompts_and_pydantic_models/                   # Original schemas
├── output/                                         # Results and reports
├── vector_db/                                      # LanceDB storage
│
├── schemas.py                     # Pydantic data models
├── ontology.py                    # Medical capability taxonomy
├── config.py                      # Configuration & API keys
├── data_loader.py                 # Data ingestion & preprocessing
├── embeddings.py                  # HuggingFace embedding generation
├── vector_store.py                # LanceDB vector database
├── retriever.py                   # Semantic search retriever
├── extractor_agent.py             # Groq LLM capability extraction
├── capability_extractor.py        # Extraction orchestration
├── validator.py                   # Multi-layer validation
├── trust_scorer.py                # Evidence-based trust scoring
├── medical_desert_detector.py     # Region gap analysis
├── planner_agent.py               # Multi-step reasoning
├── main.py                        # Main orchestrator
│
├── requirements.txt               # Dependencies
├── .env.example                   # Environment template
├── .gitignore                     # Git exclusions
└── README.md                      # This file
```

---

## 🚧 Known Issues

### Embedding Generation Dependencies
**Issue**: `sentence-transformers` import fails due to protobuf/TensorFlow conflicts

**Temporary Workaround**: Vector index building is disabled in `main.py` by default

**Solution Options**:
- Option A: Use OpenAI embeddings API
- Option B: Use direct `transformers` without `sentence-transformers` wrapper
- Option C: Create isolated environment with compatible versions

---

## 🔧 Configuration

### Environment Variables
```bash
# Required
GROQ_API_KEY=your_groq_api_key

# Optional (defaults provided)
DATA_DIR=./data
OUTPUT_DIR=./output
VECTOR_DB_PATH=./vector_db
```

### Model Configuration
Defined in `config.py`:

```python
MODEL_CONFIG = {
    'primary': 'llama-3.3-70b-versatile',      # Main reasoning
    'fast': 'llama-3.1-8b-instant',             # Quick triage
    'extraction': 'mixtral-8x7b-32768',         # Structured output
    'embedding': 'BAAI/bge-large-en-v1.5',      # Embeddings
    'embedding_fallback': 'all-MiniLM-L6-v2'    # Faster alternative
}
```

---

## 🎯 Use Cases

### 1. Policy Planning
- Identify regions needing urgent healthcare investment
- Prioritize infrastructure development
- Allocate mobile medical units

### 2. Emergency Response
- Find nearest facilities with critical capabilities
- Route patients to appropriate care levels
- Coordinate ambulance services

### 3. Data Quality Audits
- Flag suspicious capability claims
- Identify facilities needing verification
- Track data completeness over time

### 4. Research & Analysis
- Analyze healthcare access patterns
- Study capability distribution trends
- Generate evidence-based policy recommendations

---

## 🤝 Contributing

Contributions welcome! Focus areas:
1. Fix embedding generation dependencies
2. Add visualization layer (maps, charts)
3. Implement UI/web interface
4. Add more validation rules
5. Expand medical ontology

---

## 📄 License

MIT License

---

## 👥 Authors

Built for **Hack Nation AI** challenge - Virtue Foundation Ghana healthcare infrastructure analysis

---

## 🙏 Acknowledgments

- **Virtue Foundation Ghana** for providing the healthcare facilities dataset
- **Groq** for fast LLM inference
- **HuggingFace** for embedding models
- **LanceDB** for serverless vector storage

---

**⚡ Reducing time to lifesaving treatment by 100× through intelligent healthcare infrastructure analysis**


- A separate schema document defines expected fields and meanings.

---

## What This Project Does

At a high level, the project:

1. Loads raw healthcare facility data
2. Adds **lightweight helper columns** for:
   - list‑like fields (e.g. specialties, procedures)
   - region and country grouping
   - facility type categorization
   - contact and web normalization
3. Preserves all original text for:
   - evidence
   - auditing
   - future LLM‑based extraction
4. Prepares the dataset for:
   - analysis
   - visualization
   - planning logic

---

## What This Project Does NOT Do (Yet)

- ❌ No heavy data cleaning or normalization
- ❌ No data imputation or guessing
- ❌ No automated medical classification
- ❌ No production‑grade validation
- ❌ No final UI or dashboard

These are intentionally left out at the MVP stage.

---

## Repository Structure