# Smart Manufacturing AI & MLOps Platform
A production-grade, AI-driven manufacturing monitoring and predictive analytics platform. This project integrates a modern Data & ML pipeline with Microsoft Phi-3 GenAI reasoning for specialized manufacturing anomaly detection and a real-time React-based dashboard.

## 🚀 Overview
This platform transforms traditional manufacturing monitoring into an intelligent, proactive system. It leverages GCP cloud infrastructure, IoT sensor data ingestion, and advanced machine learning models (including Small Language Models like Phi-3) to provide actionable insights for factory floor operations.

## ✨ Key Features

- **Predictive Maintenance**: Machine-specific failure probability forecasting using scikit-learn models.
- **GenAI Reasoning**: Integrated "SmartFactory AI" assistant powered by Microsoft Phi-3 SLM for natural language data analysis.
- **Real-time Monitoring**: Live dashboard for tracking machine OEE, temperature, vibration, and power consumption.
- **MLOps Pipeline**: Fully versioned data and model pipeline using **DVC** (Data Version Control).
- **GitOps Hub**: Automated CI/CD using **Jenkins**, **ArgoCD**, and **Kubernetes** for seamless deployment.
- **GCP Architecture**: Designed for GCP Pub/Sub, Dataflow, and BigQuery.

## 🏗️ Project Structure

```text
├── Dashboard/              # React + Vite Frontend
│   ├── src/
│   │   ├── api/            # API Clients (Flask ML)
│   │   ├── components/     # UI & Dashboard Components
│   │   └── pages/          # Analytics, Machine Monitor, AI Assistant
├── pipeline/               # Data processing & Training logic
├── src/                    # Core Python Source Code
│   ├── data_processing.py  # DVC-managed data ingestion
│   ├── model_training.py   # Scikit-learn model training
│   └── slm_finetuner.py    # Phi-3 SLM fine-tuning scripts
├── genai/                  # GenAI monitoring and reasoning agents
├── artifacts/              # Versioned models and processed data (DVC)
├── dvc.yaml                # DVC pipeline configuration
├── application.py          # Flask API for model serving
├── Dockerfile              # Containerization for deployment
└── Jenkinsfile             # CI/CD pipeline definition
```

## 🛠️ Technology Stack

- **Frontend**: React, Vite, Tailwind CSS, Lucide Icons, Recharts, TanStack Query.
- **Backend/ML**: Python, Flask, Scikit-learn, Pandas, NumPy, Joblib.
- **GenAI**: Microsoft Phi-3 SLM, Vertex AI.
- **Infrastructure/DevOps**: GCP, Docker, Kubernetes, Jenkins, ArgoCD, DVC.

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.9+ 
- Node.js & npm
- Docker (for deployment)

### 2. Backend & ML Pipeline
Install Python dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements_genai.txt
```

Run the ML pipeline (via DVC):
```bash
dvc repro
```

Start the Flask prediction API:
```bash
python application.py
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

## 🚢 CI/CD & Deployment (GitOps)

The project utilizes a full GitOps workflow:
1. **Jenkins**: Orchestrates the build process and pushes Docker images.
2. **ArgoCD**: Monitors the GitHub repository and syncs Kubernetes manifests for continuous deployment.
3. **Kubernetes**: Hosts the containerized application on-prem or in the cloud.

Review `SETUP.txt` for detailed Jenkins and ArgoCD configuration steps.

## 📊 ML Pipeline Architecture

The DVC-managed pipeline consists of:
1. **Data Processing**: Cleans and scales raw sensor data from `DATA/data.csv`.
2. **Model Training**: Trains a classifier to predict maintenance risk (output: `artifacts/models/model.pkl`).
3. **Serving**: Flask API serves live inference to the React Dashboard.

---
Developed as part of the **Smart Manufacturing Intelligence** initiative.
