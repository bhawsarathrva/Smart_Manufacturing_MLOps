import os
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime

import openai
import faiss
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

EMBEDDING_MODEL = "text-embedding-3-small"
GENERATION_MODEL = "gpt-4o-mini"
VECTOR_STORE_PATH = "data/vector_store"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K = 5


MANUFACTURING_KNOWLEDGE = [
    {
        "source": "predictive_maintenance",
        "content": """
        Predictive Maintenance in Smart Manufacturing:
        Predictive maintenance uses sensor data and ML models to predict equipment failures before they occur.
        Key metrics monitored include: vibration levels (normal: <2.5 mm/s, warning: 2.5-7.1 mm/s, critical: >7.1 mm/s),
        temperature (normal: 20-60°C, warning: 60-80°C, critical: >80°C), bearing wear, oil quality, and acoustic emissions.
        Common ML models used: Random Forest, LSTM, Isolation Forest for anomaly detection.
        Alert thresholds are set based on historical failure data and manufacturer specifications.
        Mean Time Between Failures (MTBF) and Mean Time To Repair (MTTR) are key KPIs.
        """
    },
    {
        "source": "quality_control",
        "content": """
        Quality Control & Defect Detection:
        Computer vision models (CNN, YOLO) are deployed on production lines to detect defects in real-time.
        Defect categories include: surface scratches, dimensional deviations, color inconsistencies, structural cracks.
        Statistical Process Control (SPC) uses control charts (X-bar, R-chart) to monitor process stability.
        Six Sigma methodology targets <3.4 defects per million opportunities (DPMO).
        Acceptance Quality Limit (AQL) sampling is used for batch inspection.
        OEE (Overall Equipment Effectiveness) = Availability × Performance × Quality. Target OEE: >85%.
        """
    },
    {
        "source": "energy_optimization",
        "content": """
        Energy Optimization in Manufacturing:
        Smart energy management monitors power consumption per machine and production unit.
        Peak demand management shifts high-energy operations to off-peak hours to reduce costs.
        Energy KPIs: Energy Intensity (kWh/unit), Power Factor (target >0.95), Load Factor.
        Variable Speed Drives (VSDs) on motors can reduce energy consumption by 20-50%.
        Compressed air leaks account for 20-30% of energy waste; IoT sensors detect leaks automatically.
        HVAC optimization using occupancy sensors and weather data reduces building energy by 15-25%.
        """
    },
    {
        "source": "production_planning",
        "content": """
        Production Planning & Scheduling:
        MES (Manufacturing Execution System) tracks work orders, production status, and material flow.
        Lean manufacturing principles: eliminate waste (muda), reduce setup times (SMED), 5S methodology.
        Just-in-Time (JIT) production minimizes inventory costs but requires reliable supply chains.
        Production KPIs: Throughput, Cycle Time, Lead Time, Schedule Adherence, Capacity Utilization.
        Bottleneck analysis (Theory of Constraints) identifies and optimizes the slowest process step.
        Digital twin technology creates virtual models of production lines for simulation and optimization.
        """
    },
    {
        "source": "anomaly_detection",
        "content": """
        Anomaly Detection Models in Smart Manufacturing:
        Isolation Forest: Unsupervised algorithm effective for high-dimensional sensor data anomalies.
        Autoencoder Neural Networks: Learns normal patterns; high reconstruction error = anomaly.
        LSTM (Long Short-Term Memory): Captures temporal dependencies in time-series sensor data.
        Statistical methods: Z-score, IQR, CUSUM for simple threshold-based anomaly detection.
        Model performance metrics: Precision, Recall, F1-Score, AUC-ROC for anomaly detection tasks.
        Typical anomaly threshold: data points beyond 3 standard deviations from mean.
        Real-time streaming with Kafka/Flink enables sub-second anomaly detection latency.
        """
    },
    {
        "source": "mlops_pipeline",
        "content": """
        MLOps Pipeline for Smart Manufacturing:
        Data ingestion: IoT sensors → MQTT broker → Apache Kafka → data lake (S3/Azure Blob).
        Feature engineering: rolling statistics, FFT features, lag features, domain-specific ratios.
        Model training: MLflow tracks experiments, parameters, metrics, and artifacts.
        Model registry: MLflow Model Registry with staging/production/archived stages.
        CI/CD pipeline: GitHub Actions / Jenkins automates testing, validation, and deployment.
        Model monitoring: Evidently AI / Great Expectations for data drift and model performance.
        Retraining triggers: data drift detected, model performance drops below threshold (e.g., F1 < 0.85).
        Deployment: Docker containers, Kubernetes orchestration, FastAPI serving endpoints.
        """
    },
    {
        "source": "safety_compliance",
        "content": """
        Safety & Compliance in Smart Manufacturing:
        ISO 45001 covers occupational health and safety management systems.
        IEC 61508 is the standard for functional safety of electrical/electronic/programmable systems.
        Real-time safety monitoring includes: worker proximity detection, PPE compliance verification (CV models).
        Emergency stop (E-stop) systems must have response time <0.5 seconds per safety standards.
        Hazardous area classification (ATEX/NEC) determines equipment requirements for explosive atmospheres.
        Environmental compliance: emission monitoring (CO2, NOx, particulates), effluent tracking.
        Audit trails: all ML model decisions logged with timestamps for regulatory compliance.
        """
    },
    {
        "source": "dashboard_metrics",
        "content": """
        Dashboard Metrics & KPIs Overview:
        Production KPIs displayed: Units Produced, Scrap Rate, OEE, Throughput Rate, Downtime Hours.
        Quality metrics: Defect Rate (%), First Pass Yield (FPY), Customer Complaints, DPMO.
        Maintenance metrics: MTBF, MTTR, Planned vs Unplanned Maintenance ratio, Work Order Backlog.
        Energy metrics: Total Energy Consumption (kWh), Cost per Unit, Carbon Footprint (kg CO2).
        ML model metrics: Model Accuracy, Prediction Latency, Data Drift Score, Alert Count.
        Dashboard refresh rate: real-time (WebSocket) for critical alarms, 1-minute for operational KPIs.
        Historical trend analysis: 7-day, 30-day, 90-day rolling windows for performance comparison.
        """
    }
]


class EmbeddingEngine:
    def __init__(self):
        self.model = EMBEDDING_MODEL

    def embed_text(self, text: str) -> List[float]:
        response = client.embeddings.create(input=text, model=self.model)
        return response.data[0].embedding

    def embed_query(self, query: str) -> List[float]:
        response = client.embeddings.create(input=query, model=self.model)
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = client.embeddings.create(input=texts, model=self.model)
        return [data.embedding for data in response.data]


class VectorStore:
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents: List[Dict] = []
        self.embedder = EmbeddingEngine()

    def add_documents(self, documents: List[Dict]):
        """Add documents with metadata to the vector store."""
        texts = [doc["content"] for doc in documents]
        embeddings = self.embedder.embed_batch(texts)

        vectors = np.array(embeddings, dtype=np.float32)
        self.index.add(vectors)
        self.documents.extend(documents)
        print(f"✅ Added {len(documents)} documents to vector store. Total: {len(self.documents)}")

    def search(self, query: str, top_k: int = TOP_K) -> List[Tuple[Dict, float]]:
        """Search for relevant documents given a query."""
        query_embedding = self.embedder.embed_query(query)
        query_vector = np.array([query_embedding], dtype=np.float32)

        distances, indices = self.index.search(query_vector, top_k)
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(dist)))
        return results

    def save(self, path: str = VECTOR_STORE_PATH):
        """Persist vector store to disk."""
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, f"{path}/index.faiss")
        with open(f"{path}/documents.pkl", "wb") as f:
            pickle.dump(self.documents, f)
        print(f"💾 Vector store saved to {path}")

    def load(self, path: str = VECTOR_STORE_PATH) -> bool:
        """Load vector store from disk."""
        index_path = f"{path}/index.faiss"
        docs_path = f"{path}/documents.pkl"
        if os.path.exists(index_path) and os.path.exists(docs_path):
            self.index = faiss.read_index(index_path)
            with open(docs_path, "rb") as f:
                self.documents = pickle.load(f)
            print(f"📂 Loaded vector store: {len(self.documents)} documents")
            return True
        return False


# ─── Document Processor ───────────────────────────────────────────────────────

class DocumentProcessor:
    """Processes and chunks documents for the RAG pipeline."""

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", " "]
        )

    def process_knowledge_base(self, knowledge: List[Dict]) -> List[Dict]:
        """Process static knowledge base into chunks."""
        chunks = []
        for item in knowledge:
            text_chunks = self.splitter.split_text(item["content"])
            for i, chunk in enumerate(text_chunks):
                chunks.append({
                    "content": chunk.strip(),
                    "source": item["source"],
                    "chunk_id": f"{item['source']}_{i}",
                    "timestamp": datetime.now().isoformat()
                })
        return chunks

    def process_live_metrics(self, metrics: Dict) -> List[Dict]:
        """Convert live sensor/model metrics into searchable documents."""
        docs = []
        # Format metrics as natural language for retrieval
        content = f"""
        Current Live Manufacturing Metrics (as of {datetime.now().strftime('%Y-%m-%d %H:%M')}):
        Production Rate: {metrics.get('production_rate', 'N/A')} units/hour
        OEE: {metrics.get('oee', 'N/A')}%
        Defect Rate: {metrics.get('defect_rate', 'N/A')}%
        Energy Consumption: {metrics.get('energy_kwh', 'N/A')} kWh
        Active Alarms: {metrics.get('active_alarms', 0)}
        Machine Status: {metrics.get('machine_status', 'Unknown')}
        Last Anomaly Detected: {metrics.get('last_anomaly', 'None')}
        Model Accuracy: {metrics.get('model_accuracy', 'N/A')}%
        """
        docs.append({
            "content": content.strip(),
            "source": "live_metrics",
            "chunk_id": f"live_metrics_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat()
        })
        return docs

    def process_uploaded_document(self, text: str, filename: str) -> List[Dict]:
        """Process user-uploaded documents (manuals, reports, SOPs)."""
        chunks = self.splitter.split_text(text)
        return [
            {
                "content": chunk.strip(),
                "source": f"upload:{filename}",
                "chunk_id": f"{filename}_{i}",
                "timestamp": datetime.now().isoformat()
            }
            for i, chunk in enumerate(chunks)
        ]


# ─── RAG Engine ───────────────────────────────────────────────────────────────

class RAGEngine:
    """
    Retrieval-Augmented Generation engine for Smart Manufacturing Q&A.
    Combines FAISS vector search with OpenAI generation.
    """

    def __init__(self):
        self.vector_store = VectorStore()
        self.processor = DocumentProcessor()
        self.llm = client
        self._initialized = False

    def initialize(self, live_metrics: Optional[Dict] = None):
        """Initialize the RAG engine with knowledge base."""
        if not self.vector_store.load():
            print("🔧 Building vector store from knowledge base...")
            chunks = self.processor.process_knowledge_base(MANUFACTURING_KNOWLEDGE)
            self.vector_store.add_documents(chunks)
            self.vector_store.save()

        if live_metrics:
            self.update_live_metrics(live_metrics)

        self._initialized = True
        print("🚀 RAG Engine initialized successfully!")

    def update_live_metrics(self, metrics: Dict):
        """Inject fresh live metrics into the vector store."""
        live_docs = self.processor.process_live_metrics(metrics)
        self.vector_store.add_documents(live_docs)

    def add_document(self, text: str, filename: str):
        """Add a new document (SOP, manual, report) to the knowledge base."""
        chunks = self.processor.process_uploaded_document(text, filename)
        self.vector_store.add_documents(chunks)
        self.vector_store.save()
        return len(chunks)

    def query(self, question: str, chat_history: List[Dict] = None) -> Dict:
        """
        Run a RAG query: retrieve context → build prompt → generate answer.
        Returns: {answer, sources, retrieved_chunks, confidence}
        """
        if not self._initialized:
            self.initialize()

        # 1. Retrieve relevant context
        results = self.vector_store.search(question, top_k=TOP_K)

        # 2. Build context string
        context_parts = []
        sources = set()
        for doc, dist in results:
            context_parts.append(f"[Source: {doc['source']}]\n{doc['content']}")
            sources.add(doc["source"])

        context = "\n\n---\n\n".join(context_parts)

        # 3. Build prompt with conversation history
        history_str = ""
        if chat_history:
            recent = chat_history[-4:]  # last 4 exchanges
            for msg in recent:
                role = "User" if msg["role"] == "user" else "Assistant"
                history_str += f"{role}: {msg['content']}\n"

        prompt = f"""You are an intelligent assistant for a Smart Manufacturing MLOps system.
You have deep expertise in manufacturing operations, predictive maintenance, quality control,
energy optimization, and ML model monitoring.

Use the following retrieved context to answer the question accurately.
If the context doesn't fully answer the question, use your manufacturing domain knowledge.
Always be concise, actionable, and data-driven.

=== RETRIEVED CONTEXT ===
{context}

=== CONVERSATION HISTORY ===
{history_str}

=== QUESTION ===
{question}

=== ANSWER ===
Provide a clear, structured answer. Include specific numbers/thresholds when relevant.
If suggesting actions, prioritize by urgency."""

        # 4. Generate answer
        response = self.llm.chat.completions.create(
            model=GENERATION_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content

        # 5. Compute confidence based on retrieval distances
        avg_distance = np.mean([d for _, d in results]) if results else 999
        confidence = max(0, min(100, int(100 - avg_distance * 10)))

        return {
            "answer": answer,
            "sources": list(sources),
            "retrieved_chunks": len(results),
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }