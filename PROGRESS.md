# IDP Agent Project - Progress Tracker

## ✅ Completed Steps

### 1. Define Output Schema (Pydantic) + Ontology ✅
**Files Created:**
- `schemas.py` - Pydantic models for:
  - `ExtractedCapability` - Individual capability with evidence, confidence, availability
  - `FacilityProfile` - Aggregated facility profile with trust scores
  - `RegionCapabilityGap` - Medical desert identification
  - `ActionPlan` - Planner agent output
  
- `ontology.py` - Medical capability ontology:
  - 60+ canonical capabilities (ICU, X-ray, maternity, surgery, etc.)
  - 100+ synonym mappings
  - Dependency rules (e.g., surgery requires anesthesia + OR)
  - 9 critical capabilities defining medical deserts
  - Availability pattern keywords

**Status:** ✅ COMPLETE

---

### 2. Data Ingestion + Normalization ✅
**Files Created:**
- `config.py` - Configuration with API keys, model settings, paths
- `data_loader.py` - Data loading and preprocessing utilities

**Data Processing:**
- ✅ Loaded 987 facilities from Ghana dataset
- ✅ Added `row_id` for tracking (0-986)
- ✅ Created `facility_context` field combining name, location, specialties, details
- ✅ LLM text normalization (remove control chars, fix encoding, normalize whitespace)
- ✅ Metadata extraction functions
- ✅ Saved enriched dataset to `vf_ghana_enriched_final.csv`

**Dataset Summary:**
- Total facilities: 987
- Regions: 53
- Facility types: hospital (457), clinic (237), dentist (17), pharmacy (5), doctor (1)

**Status:** ✅ COMPLETE

---

## 🚧 Next Steps (To Be Implemented)

### 3. Create Embeddings for RAG Index (Hugging Face)
- Use `BAAI/bge-large-en-v1.5` for high-quality embeddings
- Embed `facility_context` field for each facility
- Store in LanceDB or FAISS with metadata

### 4. Build Retriever
- Top-k retrieval from vector DB
- Return relevant facilities based on query

### 5. Extraction Agent (Groq LLM → Structured JSON)
- Use `llama-3.3-70b-versatile` for capability extraction
- Parse facility_context → ExtractedCapability objects
- Output: capability, evidence, confidence, availability, dependencies

### 6. Fast Triage Pass (Optional)
- Use `llama-3.1-8b-instant` for quick relevance filtering

### 7. Normalization + Canonical Mapping
- Map extracted terms to ontology (e.g., "radiography" → "xray")
- Use rule-based matching + optional LLM for fuzzy cases

### 8. Validation / Contradiction Detection
- Check capability dependencies
- Flag suspicious claims
- Use `llama-3.3-70b-versatile` for judgment

### 9. Trust Score Computation
- Formula: confidence + completeness + (1-contradictions) + availability
- Deterministic scoring

### 10. Row-Level Citations
- Store `row_id` + `chunk_id` + evidence text offsets
- Enable traceability

### 11. Region Aggregation
- Roll up capabilities by region
- Classify: trusted / untrusted / unknown

### 12. Medical Desert Detection
- Identify regions missing critical services
- Calculate severity scores

### 13. Planner Agent
- Natural language input → action plan
- Use `llama-3.3-70b-versatile` for reasoning

### 14. Optional Reranker
- Use `BAAI/bge-reranker` to improve retrieval

### 15. UI + Map
- Streamlit interface
- Folium map visualization
- Search, filter, citations, planner

---

## 📁 Project Structure

```
Hack-nation-ai/
├── config.py                          # ✅ Configuration & API keys
├── schemas.py                         # ✅ Pydantic models
├── ontology.py                        # ✅ Medical capability ontology
├── data_loader.py                     # ✅ Data ingestion & preprocessing
├── Virtue Foundation Ghana v0.3...csv # Raw data
├── vf_ghana_enriched_final.csv       # ✅ Preprocessed data
├── data_cleaning.ipynb               # Original cleaning notebook
│
├── embeddings.py                      # 🚧 TODO: Embedding generation
├── vector_store.py                    # 🚧 TODO: Vector DB management
├── retriever.py                       # 🚧 TODO: RAG retrieval
├── extractor_agent.py                 # 🚧 TODO: Capability extraction
├── validator.py                       # 🚧 TODO: Contradiction detection
├── trust_scorer.py                    # 🚧 TODO: Trust score computation
├── aggregator.py                      # 🚧 TODO: Region aggregation
├── medical_desert_detector.py         # 🚧 TODO: Desert identification
├── planner_agent.py                   # 🚧 TODO: Planning agent
├── app.py                             # 🚧 TODO: Streamlit UI
│
├── output/                            # Generated outputs
│   ├── vector_db/                     # Vector database
│   ├── extracted_capabilities.json    # Extraction results
│   ├── facility_profiles.json         # Facility profiles
│   ├── region_gaps.json               # Medical desert analysis
│   └── citations.json                 # Citation tracking
│
└── .cache/                            # Model cache
```

---

## 🎯 Tech Stack

| Component | Technology |
|-----------|-----------|
| **LLM** | Groq (llama-3.3-70b-versatile) |
| **Embeddings** | HuggingFace (BAAI/bge-large-en-v1.5) |
| **Vector Store** | LanceDB (local, no setup) |
| **Agent Framework** | LangGraph (planned) |
| **Schemas** | Pydantic |
| **UI** | Streamlit (planned) |
| **Map** | Folium (planned) |
| **Data** | Pandas |

---

## 📊 Dataset Overview

**Source:** Virtue Foundation Ghana v0.3
**Facilities:** 987
**Regions:** 53 across Ghana
**Fields:** 43 columns including:
- Basic info: name, type, location
- Medical data: specialties, procedures, equipment, capabilities
- Contact: phone, email, website
- Enriched: row_id, facility_context, _blob_clean

---

## 🔑 API Configuration

**Groq API Key:** Configured in `config.py`
- Primary Model: `llama-3.3-70b-versatile` (reasoning)
- Fast Model: `llama-3.1-8b-instant` (triage)
- Extraction Model: `mixtral-8x7b-32768` (structured output)

**Temperature Settings:**
- Extraction: 0.1 (consistent)
- Reasoning: 0.3 (creative planning)

---

*Last Updated: Steps 1-2 completed. Ready to implement Step 3 (Embeddings).*
