# Smart Manufacturing AI & MLOps Platform
A production-grade, AI-driven manufacturing monitoring and predictive analytics platform. This project integrates a modern Data & ML pipeline with an OpenAI-powered GenAI reasoning assistant for specialized manufacturing anomaly detection, RAG capabilities, and a real-time React-based dashboard.

## 🚀 Overview
This platform transforms traditional manufacturing monitoring into an intelligent, proactive system. It leverages GCP cloud infrastructure, IoT sensor data ingestion, and advanced machine learning models (along with OpenAI's LLMs) to provide actionable insights for factory floor operations.

## ✨ Key Features
- **Predictive Maintenance**: Machine-specific failure probability forecasting using scikit-learn models.
- **GenAI Reasoning (RAG)**: Integrated "MAIA" (Manufacturing AI Assistant) powered by OpenAI (`gpt-4o-mini`) for natural language data analysis, alert explanation, and document-grounded answers.
- **Real-time Monitoring**: Live dashboard for tracking machine OEE, temperature, vibration, and power consumption.
- **MLOps Pipeline**: Fully versioned data and model pipeline using **DVC** (Data Version Control) and **MLflow**.
- **GitOps Hub**: Automated CI/CD using **Jenkins**, **ArgoCD**, and **Kubernetes** for seamless deployment.
- **GCP Architecture**: Designed for GCP Pub/Sub, Dataflow, and BigQuery.

## 🏗️ Project Structure
```text
├── Dashboard/              # React + Vite Frontend
│   ├── src/
│   │   ├── api/            # API Clients (Flask ML & GenAI API)
│   │   ├── components/     # UI & Dashboard Components
│   │   └── pages/          # Analytics, Machine Monitor, AI Assistant
├── pipeline/               # Data processing & Training logic
├── src/                    # Core Python Source Code
│   ├── data_processing.py  # DVC-managed data ingestion
│   ├── model_training.py   # Scikit-learn model training
│   └── slm_finetuner.py    # Phi-3 SLM fine-tuning scripts
├── genai/                  # GenAI monitoring and reasoning agents
│   ├── rag_engine.py          → Core RAG: FAISS + OpenAI embeddings
│   ├── chatbot.py             → Chatbot: intent routing, tool calling, session mgmt
│   ├── api_server.py          → FastAPI server exposing REST endpoints
│   ├── chat_ui.py             → Full-page Streamlit chat UI
│   ├── genai.py               → Bridge to existing MLOps pipeline
│   └── doc_loader.py          → Loaders for PDF, CSV, JSON, TXT documents
├── artifacts/              # Versioned models and processed data (DVC)
├── dvc.yaml                # DVC pipeline configuration
├── application.py          # Flask API for model serving
├── pyproject.toml          # Primary Python dependencies (managed by uv)
├── requirements.txt        # Extra dependency configs
├── Dockerfile              # Containerization for deployment
└── Jenkinsfile             # CI/CD pipeline definition
```

## 🛠️ Technology Stack
- **Frontend**: React, Vite, Tailwind CSS, Lucide Icons, Recharts, TanStack Query, Streamlit.
- **Backend/ML**: Python, FastAPI, Flask, Scikit-learn, Pandas, MLflow.
- **GenAI**: OpenAI (`gpt-4o-mini`, `text-embedding-3-small`), Langchain, FAISS.
- **Infrastructure/DevOps**: GCP, Docker, Kubernetes, Jenkins, ArgoCD, DVC.

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.12+ 
- Node.js & npm
- **uv** (High-performance Python package manager)
- Docker (for deployment)

### 2. Backend, GenAI & ML Pipeline
Sync your environment using **uv**:
```bash
uv sync
```
*Note: This automatically installs all packages mapped in `pyproject.toml` and `requirements.txt`.*

Configure your environment variables:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

Run the ML pipeline (via DVC):
```bash
uv run dvc repro
```

Start the Flask prediction API:
```bash
uv run python application.py
```

Start the GenAI REST API Server:
```bash
uv run python genai/api_server.py
# Starts on http://localhost:8001
```

Launch the standalone Chat UI:
```bash
uv run streamlit run genai/chat_ui.py
# Opens at http://localhost:8502
```

### 3. Dashboard (Frontend)
Navigate to the directory and install dependencies:
```bash
cd Dashboard
npm install
```

Start the development server:
```bash
npm run dev
```

## 🤖 GenAI Module Integration

### Data Flow
```
User Question
    │
    ▼
Intent Classifier ──► GREETING / LIVE DATA → Direct OpenAI + Tool Call
    │
    ▼ (domain knowledge)
FAISS Vector Search
    │
    ▼
Top-K Relevant Chunks (from knowledge base + uploaded docs + live metrics)
    │
    ▼
OpenAI gpt-4o-mini (generation with context)
    │
    ▼
Structured Response → Chat UI / REST API
```

### Option A: Push Live Metrics (Recommended)
```python
# In your MLOps pipeline / data refresh loop
from genai.genai import ManufacturingGenAIBridge

bridge = ManufacturingGenAIBridge()

# Push metrics every minute (or on update)
bridge.push_live_metrics({
    "production_rate": your_metrics["rate"],
    "oee": your_metrics["oee"],
    "defect_rate": your_metrics["defect_rate"],
    "energy_kwh": your_metrics["energy"],
    "active_alarms": len(your_alerts),
    "machine_status": "Running",
    "last_anomaly": your_last_anomaly,
    "model_accuracy": your_model_acc
})
```

### Option B: Sync MLflow Experiment Results
```python
bridge = ManufacturingGenAIBridge()
bridge.sync_mlflow_models("http://localhost:5000")
```

### Option C: Adding Custom Knowledge
Upload an SOP or Maintenance Manual:
```bash
# Via API
curl -X POST http://localhost:8001/rag/upload \
  -F "file=@maintenance_sop.txt"
```
Or via Python:
```python
bridge = ManufacturingGenAIBridge()
bridge.index_sop_document("docs/maintenance_sop.pdf")
bridge.index_maintenance_logs("data/sensor_logs.csv")
```

## 📡 API Endpoints (GenAI)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/health` | API health check |
| `POST` | `/chat` | Main chat endpoint |
| `GET`  | `/chat/session/{id}` | Get conversation history |
| `DELETE` | `/chat/session/{id}` | Clear session |
| `POST` | `/rag/query` | Direct RAG query |
| `POST` | `/rag/upload` | Upload document to knowledge base |
| `POST` | `/metrics/update` | Push live metrics to RAG |
| `GET`  | `/chat/suggestions` | Get suggested questions |

## 🚢 CI/CD & Deployment (GitOps)
The project utilizes a full GitOps workflow:
1. **Jenkins**: Orchestrates the build process and pushes Docker images.
2. **ArgoCD**: Monitors the GitHub repository and syncs Kubernetes manifests for continuous deployment.
3. **Kubernetes**: Hosts the containerized application on-prem or in the cloud.

Review `SETUP.txt` for detailed Jenkins and ArgoCD configuration steps.

## 🚀 Cloud Deployment
For taking this platform to production on **Google Cloud Platform (GCP)**, please refer to our detailed roadmap:
👉 [**Cloud Deployment Roadmap (GCP)**](./docs/CLOUD_DEPLOYMENT_ROADMAP.md)

---
Developed as part of the **Smart Manufacturing Intelligence** initiative.
