import os
import json
import requests
from typing import Dict, Optional, Any
from datetime import datetime


GENAI_API_URL = os.getenv("GENAI_API_URL", "http://localhost:8001")


class ManufacturingGenAIBridge:
    def __init__(self, api_url: str = GENAI_API_URL):
        self.api_url = api_url

    def is_genai_available(self) -> bool:
        try:
            r = requests.get(f"{self.api_url}/health", timeout=5)
            return r.status_code == 200
        except:
            return False

    def push_live_metrics(self, metrics: Dict[str, Any]) -> bool:
        try:
            r = requests.post(
                f"{self.api_url}/metrics/update",
                json={"metrics": metrics},
                timeout=10
            )
            return r.status_code == 200
        except Exception as e:
            print(f"⚠️  GenAI metrics push failed: {e}")
            return False

    def sync_mlflow_models(self, mlflow_tracking_uri: str = "http://localhost:5000"):
        try:
            import mlflow
            mlflow.set_tracking_uri(mlflow_tracking_uri)
            client = mlflow.tracking.MlflowClient()
            models = client.search_registered_models()
            summary_parts = [f"MLflow Model Registry (synced {datetime.now().strftime('%Y-%m-%d %H:%M')}):"]

            for model in models:
                latest = client.get_latest_versions(model.name)
                for version in latest:
                    run = client.get_run(version.run_id)
                    metrics = run.data.metrics
                    params = run.data.params
                    summary_parts.append(f"""
Model: {model.name} v{version.version}
  Stage: {version.current_stage}
  Accuracy: {metrics.get('accuracy', 'N/A')}
  F1 Score: {metrics.get('f1_score', 'N/A')}
  Algorithm: {params.get('model_type', 'N/A')}
  Trained: {datetime.fromtimestamp(run.info.start_time / 1000).strftime('%Y-%m-%d')}
""")
            summary_text = "\n".join(summary_parts)
            self._upload_text_to_rag(summary_text, "mlflow_model_registry.txt")
            print(f"✅ Synced {len(models)} MLflow models to GenAI knowledge base")

        except ImportError:
            print("⚠️  MLflow not installed. Run: pip install mlflow")
        except Exception as e:
            print(f"⚠️  MLflow sync failed: {e}")

    def get_alert_explanation(self, alert: Dict) -> Optional[str]:
        """
        Ask the GenAI assistant to explain an alert and suggest actions.
        Wire this into your alerting pipeline.

        Args:
            alert: {machine_id, alert_type, value, threshold, severity}
        Returns:
            AI-generated explanation and recommended action
        """
        message = (
            f"⚠️ Alert on {alert.get('machine_id', 'Unknown Machine')}: "
            f"{alert.get('alert_type', 'Unknown Alert')} — "
            f"Value: {alert.get('value', 'N/A')}, Threshold: {alert.get('threshold', 'N/A')}, "
            f"Severity: {alert.get('severity', 'UNKNOWN')}. "
            f"Explain what this means and what action should be taken."
        )
        try:
            r = requests.post(
                f"{self.api_url}/chat",
                json={"message": message, "session_id": "alert_system"},
                timeout=30
            )
            if r.status_code == 200:
                return r.json().get("response")
        except Exception as e:
            print(f"⚠️  Alert explanation failed: {e}")
        return None

    # ─── Document Management ──────────────────────────────────────────────────

    def index_sop_document(self, file_path: str) -> bool:
        """
        Index a Standard Operating Procedure (SOP) document into the RAG knowledge base.
        Supports: .txt, .pdf (if PyMuPDF installed)
        """
        from document_loaders import load_document
        try:
            doc = load_document(file_path)
            return self._upload_text_to_rag(doc["text"], doc["filename"])
        except Exception as e:
            print(f"⚠️  Failed to index {file_path}: {e}")
            return False

    def index_maintenance_logs(self, csv_path: str) -> bool:
        """Index historical maintenance logs for RAG."""
        from document_loaders import load_sensor_csv
        try:
            text = load_sensor_csv(csv_path)
            return self._upload_text_to_rag(text, os.path.basename(csv_path))
        except Exception as e:
            print(f"⚠️  Failed to index maintenance logs: {e}")
            return False

    # ─── Direct RAG Query ─────────────────────────────────────────────────────

    def ask(self, question: str, session_id: str = "bridge") -> Optional[str]:
        """
        Simple method to ask the GenAI a question programmatically.
        Useful for automated reporting or pipeline decision support.
        """
        try:
            r = requests.post(
                f"{self.api_url}/chat",
                json={"message": question, "session_id": session_id},
                timeout=30
            )
            if r.status_code == 200:
                return r.json().get("response")
        except Exception as e:
            print(f"⚠️  Query failed: {e}")
        return None

    # ─── Internal Helpers ─────────────────────────────────────────────────────

    def _upload_text_to_rag(self, text: str, filename: str) -> bool:
        """Upload plain text as a document to the RAG knowledge base."""
        try:
            r = requests.post(
                f"{self.api_url}/rag/upload",
                files={"file": (filename, text.encode("utf-8"), "text/plain")},
                timeout=60
            )
            return r.status_code == 200
        except Exception as e:
            print(f"⚠️  RAG upload failed: {e}")
            return False


# ─── Streamlit Widget (drop into existing dashboard page) ────────────────────

def embed_chat_widget_streamlit(api_url: str = GENAI_API_URL):
    """
    Drop this function call into any Streamlit page to embed a mini chatbot.
    Example: Add to your existing dashboard sidebar or a dedicated "AI Assistant" page.

    Usage in your existing dashboard:
        from genai_integration import embed_chat_widget_streamlit
        embed_chat_widget_streamlit()
    """
    import streamlit as st
    import uuid

    if "mini_chat_session" not in st.session_state:
        st.session_state.mini_chat_session = str(uuid.uuid4())
    if "mini_chat_history" not in st.session_state:
        st.session_state.mini_chat_history = []

    with st.expander("🤖 Ask MAIA - AI Assistant", expanded=False):
        # Chat history
        for msg in st.session_state.mini_chat_history[-6:]:
            role_icon = "🧑" if msg["role"] == "user" else "🤖"
            st.markdown(f"**{role_icon}** {msg['content']}")

        # Input
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_input(
                "Ask about alerts, KPIs, maintenance...",
                key="mini_chat_input",
                label_visibility="collapsed"
            )
        with col2:
            send = st.button("Send", key="mini_chat_send")

        if send and user_input:
            # Add to history
            st.session_state.mini_chat_history.append({"role": "user", "content": user_input})

            # Query API
            try:
                r = requests.post(
                    f"{api_url}/chat",
                    json={"message": user_input, "session_id": st.session_state.mini_chat_session},
                    timeout=30
                )
                if r.status_code == 200:
                    response = r.json().get("response", "No response")
                else:
                    response = "⚠️ API error"
            except:
                response = "⚠️ Cannot connect to GenAI API. Ensure api_server.py is running."

            st.session_state.mini_chat_history.append({"role": "assistant", "content": response})
            st.rerun()


# ─── CLI Demo ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    bridge = ManufacturingGenAIBridge()

    print(f"GenAI API available: {bridge.is_genai_available()}")

    # Push sample metrics
    bridge.push_live_metrics({
        "production_rate": 156,
        "oee": 82.3,
        "defect_rate": 1.8,
        "energy_kwh": 1823,
        "active_alarms": 2,
        "machine_status": "Running",
        "last_anomaly": "CNC-03 vibration spike at 6.8 mm/s",
        "model_accuracy": 94.2
    })

    # Ask a question
    answer = bridge.ask("What are the current active alerts and what should I do?")
    if answer:
        print("\n=== GenAI Response ===")
        print(answer)

    # Get alert explanation
    explanation = bridge.get_alert_explanation({
        "machine_id": "CNC-03",
        "alert_type": "Vibration Spike",
        "value": 6.8,
        "threshold": 7.1,
        "severity": "WARNING"
    })
    if explanation:
        print("\n=== Alert Explanation ===")
        print(explanation)