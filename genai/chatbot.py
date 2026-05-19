import os
import json
from typing import List, Dict, Optional, Callable
from datetime import datetime
from enum import Enum

import openai
from rag_engine import RAGEngine

from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

client = openai.OpenAI(api_key=OPENAI_API_KEY)


class Intent(Enum):
    ANOMALY_QUERY = "anomaly_query"
    MAINTENANCE_QUERY = "maintenance_query"
    QUALITY_QUERY = "quality_query"
    ENERGY_QUERY = "energy_query"
    MODEL_PERFORMANCE = "model_performance"
    GENERAL_MANUFACTURING = "general_manufacturing"
    LIVE_METRICS = "live_metrics"
    ALERT_EXPLANATION = "alert_explanation"
    ACTION_RECOMMENDATION = "action_recommendation"
    GREETING = "greeting"
    UNKNOWN = "unknown"


INTENT_KEYWORDS = {
    Intent.ANOMALY_QUERY: ["anomaly", "anomalies", "outlier", "unusual", "spike", "deviation", "abnormal"],
    Intent.MAINTENANCE_QUERY: ["maintenance", "breakdown", "failure", "repair", "mtbf", "mttr", "bearing", "vibration"],
    Intent.QUALITY_QUERY: ["quality", "defect", "scrap", "oee", "yield", "fpy", "inspection", "reject"],
    Intent.ENERGY_QUERY: ["energy", "power", "electricity", "consumption", "kwh", "carbon", "efficiency"],
    Intent.MODEL_PERFORMANCE: ["model", "accuracy", "f1", "precision", "recall", "drift", "prediction", "mlflow"],
    Intent.LIVE_METRICS: ["current", "now", "live", "real-time", "latest", "today", "status"],
    Intent.ALERT_EXPLANATION: ["alert", "alarm", "warning", "critical", "threshold", "exceeded"],
    Intent.ACTION_RECOMMENDATION: ["should", "recommend", "suggest", "action", "next step", "fix", "improve"],
    Intent.GREETING: ["hello", "hi", "hey", "help", "start", "what can you"],
}


def classify_intent(message: str) -> Intent:
    """Simple keyword-based intent classifier."""
    msg_lower = message.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in msg_lower for kw in keywords):
            return intent
    return Intent.GENERAL_MANUFACTURING



MANUFACTURING_TOOLS = [
    {
        "name": "get_live_metrics",
        "description": "Fetch the latest real-time production metrics, sensor readings, and KPIs from the manufacturing system",
        "parameters": {
            "type": "object",
            "properties": {
                "metric_type": {
                    "type": "string",
                    "enum": ["all", "production", "quality", "energy", "maintenance", "models"],
                    "description": "Type of metrics to retrieve"
                }
            },
            "required": ["metric_type"]
        }
    },
    {
        "name": "get_anomaly_report",
        "description": "Get the latest anomaly detection report including recent anomalies, severity, and affected machines",
        "parameters": {
            "type": "object",
            "properties": {
                "hours": {
                    "type": "integer",
                    "description": "Number of past hours to look back for anomalies (default: 24)"
                }
            }
        }
    },
    {
        "name": "get_maintenance_schedule",
        "description": "Retrieve the predictive maintenance schedule and upcoming maintenance alerts",
        "parameters": {
            "type": "object",
            "properties": {
                "machine_id": {
                    "type": "string",
                    "description": "Specific machine ID or 'all' for all machines"
                }
            }
        }
    },
    {
        "name": "get_model_performance",
        "description": "Get ML model performance metrics including accuracy, drift scores, and recent predictions",
        "parameters": {
            "type": "object",
            "properties": {
                "model_name": {
                    "type": "string",
                    "description": "Name of the ML model or 'all' for all models"
                }
            }
        }
    }
]


# ─── Mock Tool Handlers (replace with real integrations) ──────────────────────

class ToolHandler:
    """
    Handles tool calls from Gemini.
    Replace mock data with real database/API calls from your MLOps system.
    """

    def __init__(self, metrics_callback: Optional[Callable] = None):
        self.metrics_callback = metrics_callback

    def execute(self, tool_name: str, params: Dict) -> str:
        """Dispatch tool call to appropriate handler."""
        handlers = {
            "get_live_metrics": self.get_live_metrics,
            "get_anomaly_report": self.get_anomaly_report,
            "get_maintenance_schedule": self.get_maintenance_schedule,
            "get_model_performance": self.get_model_performance,
        }
        handler = handlers.get(tool_name)
        if handler:
            return json.dumps(handler(params))
        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    def get_live_metrics(self, params: Dict) -> Dict:
        """Fetch live metrics — integrate with your actual data source."""
        if self.metrics_callback:
            return self.metrics_callback(params.get("metric_type", "all"))

        # Mock data — replace with real DB/API calls
        return {
            "timestamp": datetime.now().isoformat(),
            "production": {
                "units_produced_today": 1247,
                "production_rate": 156,  # units/hour
                "oee": 82.3,  # %
                "throughput_target": 160,
            },
            "quality": {
                "defect_rate": 1.8,  # %
                "scrap_count": 22,
                "first_pass_yield": 98.2,  # %
            },
            "energy": {
                "current_consumption_kw": 284.5,
                "today_kwh": 1823,
                "cost_per_unit": 0.042,  # $/unit
            },
            "maintenance": {
                "active_alerts": 2,
                "machines_at_risk": ["CNC-03", "Press-07"],
                "next_scheduled": "2025-06-15 08:00",
            }
        }

    def get_anomaly_report(self, params: Dict) -> Dict:
        hours = params.get("hours", 24)
        return {
            "period_hours": hours,
            "total_anomalies": 3,
            "anomalies": [
                {
                    "machine_id": "CNC-03",
                    "type": "Vibration Spike",
                    "severity": "WARNING",
                    "value": 6.8,
                    "threshold": 7.1,
                    "timestamp": "2025-06-14 14:32:10",
                    "recommended_action": "Inspect bearing assembly within 48 hours"
                },
                {
                    "machine_id": "Conveyor-02",
                    "type": "Temperature Anomaly",
                    "severity": "INFO",
                    "value": 65.2,
                    "threshold": 80,
                    "timestamp": "2025-06-14 11:15:42",
                    "recommended_action": "Monitor for next 4 hours"
                },
                {
                    "machine_id": "Press-07",
                    "type": "Power Consumption Spike",
                    "severity": "WARNING",
                    "value": 45.3,
                    "threshold": 42,
                    "timestamp": "2025-06-14 09:05:17",
                    "recommended_action": "Check hydraulic system pressure"
                }
            ]
        }

    def get_maintenance_schedule(self, params: Dict) -> Dict:
        machine_id = params.get("machine_id", "all")
        return {
            "machine_filter": machine_id,
            "upcoming_maintenance": [
                {
                    "machine_id": "CNC-03",
                    "type": "Predictive - Bearing Replacement",
                    "priority": "HIGH",
                    "predicted_failure_date": "2025-06-20",
                    "confidence": 87.3,
                    "estimated_downtime_hours": 4
                },
                {
                    "machine_id": "Press-07",
                    "type": "Predictive - Hydraulic Check",
                    "priority": "MEDIUM",
                    "predicted_failure_date": "2025-06-25",
                    "confidence": 71.8,
                    "estimated_downtime_hours": 2
                },
                {
                    "machine_id": "Robot-01",
                    "type": "Scheduled - Lubrication",
                    "priority": "LOW",
                    "scheduled_date": "2025-06-16",
                    "confidence": None,
                    "estimated_downtime_hours": 1
                }
            ]
        }

    def get_model_performance(self, params: Dict) -> Dict:
        model_name = params.get("model_name", "all")
        return {
            "model_filter": model_name,
            "models": [
                {
                    "name": "anomaly_detector_v3",
                    "type": "Isolation Forest",
                    "accuracy": 94.2,
                    "f1_score": 0.913,
                    "data_drift_score": 0.08,
                    "status": "HEALTHY",
                    "last_retrained": "2025-06-01",
                    "predictions_today": 14520
                },
                {
                    "name": "defect_classifier_v2",
                    "type": "CNN (ResNet50)",
                    "accuracy": 97.6,
                    "f1_score": 0.971,
                    "data_drift_score": 0.03,
                    "status": "HEALTHY",
                    "last_retrained": "2025-05-28",
                    "predictions_today": 8234
                },
                {
                    "name": "predictive_maintenance_lstm",
                    "type": "LSTM",
                    "accuracy": 89.1,
                    "f1_score": 0.878,
                    "data_drift_score": 0.19,
                    "status": "MONITOR",
                    "last_retrained": "2025-05-15",
                    "predictions_today": 2100
                }
            ]
        }


# ─── Chat Session ──────────────────────────────────────────────────────────────

class ConversationSession:
    """Manages a single user conversation session."""

    def __init__(self, session_id: str, max_history: int = 20):
        self.session_id = session_id
        self.max_history = max_history
        self.history: List[Dict] = []
        self.created_at = datetime.now()
        self.message_count = 0

    def add_message(self, role: str, content: str):
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.message_count += 1
        # Keep history bounded
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def get_formatted_history(self) -> str:
        if not self.history:
            return ""
        lines = []
        for msg in self.history[-6:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content'][:200]}")
        return "\n".join(lines)

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "message_count": self.message_count,
            "created_at": self.created_at.isoformat(),
            "history": self.history
        }


# ─── Main Chatbot ──────────────────────────────────────────────────────────────

class ManufacturingChatbot:
    """
    Core chatbot for Smart Manufacturing MLOps.
    Features:
    - Gemini 1.5 Flash generation
    - RAG for domain knowledge retrieval
    - Function calling for live data
    - Multi-turn conversation memory
    - Intent-based routing
    """

    SYSTEM_PROMPT = """You are MAIA (Manufacturing AI Assistant), an expert AI for a Smart Manufacturing MLOps platform.

Your capabilities:
• Answer questions about manufacturing operations, anomalies, maintenance, quality, and energy
• Interpret ML model predictions and explain anomaly alerts
• Provide actionable recommendations based on sensor data and KPIs
• Help operators understand dashboard metrics
• Guide troubleshooting of production issues

Personality: Professional, concise, and data-driven. Use metrics when available.
Format: Use bullet points and structured responses for clarity. Highlight critical items with ⚠️.
Always: Ground your answers in data. If uncertain, say so clearly."""

    def __init__(self, metrics_callback: Optional[Callable] = None):
        self.rag_engine = RAGEngine()
        self.tool_handler = ToolHandler(metrics_callback)
        self.sessions: Dict[str, ConversationSession] = {}
        self.llm = client
        self._initialized = False

    def initialize(self, live_metrics: Optional[Dict] = None):
        """Initialize RAG engine with knowledge base."""
        self.rag_engine.initialize(live_metrics)
        self._initialized = True

    def get_or_create_session(self, session_id: str) -> ConversationSession:
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationSession(session_id)
        return self.sessions[session_id]

    def chat(self, message: str, session_id: str = "default") -> Dict:
        """
        Main chat method. Routes to RAG or direct generation based on intent.
        Returns: {response, intent, sources, session_id, timestamp}
        """
        if not self._initialized:
            self.initialize()

        session = self.get_or_create_session(session_id)
        intent = classify_intent(message)

        # Add user message to history
        session.add_message("user", message)

        # Route based on intent
        if intent == Intent.GREETING:
            response_text = self._handle_greeting()
            sources = []
        elif intent in [Intent.LIVE_METRICS, Intent.ANOMALY_QUERY, Intent.MAINTENANCE_QUERY, Intent.MODEL_PERFORMANCE]:
            # Use tool calling for live data
            response_text, sources = self._handle_with_tools(message, intent, session)
        else:
            # Use RAG for knowledge-based queries
            rag_result = self.rag_engine.query(message, session.history[:-1])
            response_text = rag_result["answer"]
            sources = rag_result["sources"]

        # Add response to history
        session.add_message("assistant", response_text)

        return {
            "response": response_text,
            "intent": intent.value,
            "sources": sources,
            "session_id": session_id,
            "message_count": session.message_count,
            "timestamp": datetime.now().isoformat()
        }

    def _handle_greeting(self) -> str:
        return """👋 Hello! I'm **MAIA**, your Manufacturing AI Assistant.

I can help you with:
- 🔍 **Anomaly Detection** — Explain alerts and anomalies
- 🔧 **Predictive Maintenance** — Machine health and maintenance schedules  
- ✅ **Quality Control** — Defect rates, OEE, and quality KPIs
- ⚡ **Energy Optimization** — Consumption analysis and recommendations
- 🤖 **ML Model Monitoring** — Model performance, drift, and retraining
- 📊 **Live Metrics** — Real-time production status

What would you like to know?"""

    def _handle_with_tools(self, message: str, intent: Intent, session: ConversationSession) -> tuple:
        """Handle queries that require live data via tool calling."""
        # Map intent to tool
        tool_map = {
            Intent.LIVE_METRICS: ("get_live_metrics", {"metric_type": "all"}),
            Intent.ANOMALY_QUERY: ("get_anomaly_report", {"hours": 24}),
            Intent.MAINTENANCE_QUERY: ("get_maintenance_schedule", {"machine_id": "all"}),
            Intent.MODEL_PERFORMANCE: ("get_model_performance", {"model_name": "all"}),
        }

        tool_name, default_params = tool_map.get(intent, ("get_live_metrics", {"metric_type": "all"}))

        # Execute tool
        tool_result = self.tool_handler.execute(tool_name, default_params)
        tool_data = json.loads(tool_result)

        # Build prompt with tool data + conversation context
        prompt = f"""
{session.get_formatted_history()}

User: {message}

Tool Data ({tool_name}):
{json.dumps(tool_data, indent=2)}

Based on the above data, provide a helpful, concise answer to the user's question.
Highlight any critical issues with ⚠️. Format numbers clearly."""

        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content, [tool_name]

    def add_document_to_knowledge_base(self, text: str, filename: str) -> str:
        """Allow users to upload documents (SOPs, manuals) to enhance RAG."""
        chunks_added = self.rag_engine.add_document(text, filename)
        return f"✅ Added '{filename}' to knowledge base ({chunks_added} chunks indexed)."

    def get_session_summary(self, session_id: str) -> Dict:
        """Get summary of a conversation session."""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        return session.to_dict()

    def clear_session(self, session_id: str):
        """Clear conversation history for a session."""
        if session_id in self.sessions:
            self.sessions[session_id] = ConversationSession(session_id)