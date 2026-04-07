# 🏭 Production-Grade Smart Manufacturing GenAI Architecture

This plan upgrades your current Smart Manufacturing system into an advanced, production-ready AI platform using Azure Infrastructure, GenAI reasoning, and fine-tuned Small Language Models (SLMs).

---

## 🏗️ 1. System Architecture (Azure + GenAI)

```mermaid
graph TB
    subgraph "🏭 Manufacturing Unit (Edge)"
        CAM["📷 CCTV / Sensors"] --> |"RTSP / MQTT"| EDGE["Azure IoT Edge"]
        EDGE --> |"Pre-processing"| VLM["VLM Inference (SLM)"]
        VLM --> |"Status/Anomaly Events"| HUB["Azure IoT Hub"]
    end

    subgraph "☁️ Azure Cloud Infrastructure"
        HUB --> |"Real-time Stream"| ASA["Azure Stream Analytics"]
        ASA --> |"Hot Storage"| CDB["Azure Cosmos DB (Live Telemetry)"]
        
        HUB --> |"System Alerts"| AF["Azure Functions (Trigger)"]
        AF --> |"Reasoning Request"| GPT["GPT-4o / Fine-tuned SLM"]
        GPT --> |"Contextual Alert"| NOTIF["Staff Dash / Teams / SMS"]

        ASA --> |"Cold Storage"| ADLS["Azure Data Lake (Gen2)"]
    end

    subgraph "🧠 AI / MLOps Pipeline"
        ADLS --> |"Historical Data"| AML["Azure Machine Learning"]
        AML --> |"Fine-Tuning"| FT["SLM Training Loop (Unsloth/LoRA)"]
        FT --> |"New Weights"| MOD_REG["Azure Model Registry"]
        MOD_REG --> |"Deployment"| VLM
    end
```

---

## 🧩 2. Core Components & Logic

### A. The "Vision-Reasoning" Layer (VLM/SLM)
Instead of basic object detection, we use a **Vision-Language Model (VLM)** like **Phi-3-Vision** or **Qwen-2.5-VL** (Small Language Models).
- **Inference**: "Analyze the machine at [Zone A]. Is there any smoke or mechanical misalignment?"
- **Output**: "Anomaly detected. Conveyor belt B-402 shows excessive friction/heat signature. Maintenance required."

### B. Fine-Tuning SLM (Small Language Models)
Fine-turning an SLM for manufacturing-specific terminology (e.g., "OEE", "CNC spindle", "safety interlock breach").
- **Dataset**: Custom images of faulty vs. normal machinery.
- **Process**: QLoRA fine-tuning on Azure ML compute instances.

### C. Data & AI Pipeline (DVC + Azure ML)
Ensuring every model version is linked to the data version that trained it.
- **DVC**: Track data in Azure Blob Storage.
- **Azure ML SDK v2**: Orchestrate training jobs.

---

## 🚀 3. Proposed Codebase Structure

```text
CODE/
├── azure/                  # ☁️ Azure Cloud Infrastructure
│   ├── iot_hub_config.json # IoT Hub setup
│   ├── provision_infra.py   # Terraform/Pulumi scripts
│   └── functions/          # Azure Function Triggers
├── genai/                  # 🤖 GenAI & LLM Logic
│   ├── monitoring_agent.py # GPT-4o / Phi-3 Agent loop
│   ├── prompts/            # System prompts for reasoning
│   └── slm_inference.py    # VLM local inference engine
├── pipeline/               # ⚡ Production-Grade Pipelines
│   ├── azure_ml_training.py# Training jobs on Azure ML
│   ├── deployment.py       # CI/CD to Azure IoT Edge
│   └── data_pipeline.py    # ADLS Data ingestion logic
├── src/                    # 🏗️ Core ML / Vision
│   ├── slm_finetuner.py    # Script for fine-tuning Phi-3/Qwen
│   ├── data_ingestion.py   # Real-time data processing
│   └── report_generator.py # GenAI PDF/Analytics reporting
└── requirements_genai.txt  # Modern dependencies
```

---

## 🛠️ 4. Immediate Next Steps

1.  **Environment Setup**: Install Azure CLI and `azure-ai-ml` SDK.
2.  **Dataset Pre-processing**: Convert manufacturing telemetry/images to JSONL for SFT (Supervised Fine-Tuning).
3.  **Prototype Agent**: Create a Python script (`monitoring_agent.py`) using `langchain-azure-openai` to reason over sensor data.
4.  **Azure Resource Provisioning**: Create the IoT Hub and Cosmos DB instances.
