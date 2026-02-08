# 🏥 <span style="color:#2E86C1;">HealPath AI</span>

### <span style="color:#27AE60;">AI-powered detection of healthcare access gaps in Ghana</span>

<br/>

![Hackathon](https://img.shields.io/badge/Event-4th%20Hackathon%20Track-blueviolet)
![SAP](https://img.shields.io/badge/SAP-Corporate%20Challenge-0FAAFF?logo=sap&logoColor=white)
![Status](https://img.shields.io/badge/Status-Hackathon%20Build-success)
![License](https://img.shields.io/badge/License-MIT-yellow)

</div>


HealPath AI is an Intelligent Document Parsing (IDP) agent that analyzes healthcare facility data to identify medical deserts, missing medical capabilities, and regional healthcare gaps across Ghana.

---

## 🎯 Problem

Healthcare access in Ghana is uneven and difficult to analyze quickly. Decision-makers struggle to answer questions like:

- Which regions lack emergency or maternity care?
- Where are the most critical healthcare gaps?
- Which facilities can actually handle urgent cases?

---

## 💡 Solution

HealPath AI uses **LLMs + semantic search** to transform messy healthcare data into **actionable insights**:

- Automatically detect medical deserts  
- Validate facility capability claims with evidence  
- Answer complex healthcare questions in natural language  

All results are **evidence-backed** and **Virtue Foundation compliant**.

---

## ✨ Key Features

- Natural language healthcare queries
- Medical desert detection by region  
- Semantic search across 987 facilities  
- Interactive Streamlit dashboard  
- Trust scoring and validation  
- Coverage across all 53 regions of Ghana  

---

## 🏗️ How It Works

1. Load and normalize healthcare facility data  
2. Generate vector embeddings and store in LanceDB  
3. Retrieve relevant facilities using semantic search  
4. Extract and validate medical capabilities using LLMs  
5. Aggregate gaps by region to identify medical deserts  

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/desshah/Hack-nation-ai.git
cd Hack-nation-ai
pip install -r requirements.txt
```

### 2. Configure API Key
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Build Vector Index (first run only)
```bash
python embeddings.py
```

### 4. Run the App
```bash
streamlit run streamlit_demo.py
```

Open: **http://localhost:8501**

---

## 🧪 Example Queries

- “Which regions lack emergency care?”
- “Show medical deserts in Ghana”
- “Where is maternity care most limited?”
- “Which districts need urgent healthcare investment?”

---

## 📊 Data

- **987 healthcare facilities**
- **41+ data fields per facility**
- Services, equipment, staffing, ownership, and location
- Source: **Virtue Foundation Ghana**

---

## 🧠 Tech Stack

- **LLM**: Groq (Llama 3.x)
- **Embeddings**: BGE / MiniLM
- **Vector Database**: LanceDB
- **Backend**: Python
- **UI**: Streamlit

---

## 🎯 Use Cases

- 🏛️ Healthcare policy & planning  
- 🚑 Emergency response routing  
- 🤰 Maternal health programs  
- 📈 Infrastructure investment decisions  

---

## 🏆 Hackathon Value

- Real-world, high-impact problem  
- End-to-end working system  
- Scalable beyond Ghana  
- Demonstrates applied AI, not just models  

---

## 📄 License

MIT License

