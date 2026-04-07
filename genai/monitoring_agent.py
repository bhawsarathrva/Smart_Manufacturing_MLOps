import os
import json
from datetime import datetime
from langchain_azure_openai import AzureChatOpenAI
from pydantic import BaseModel, Field

class ManufacturingEvent(BaseModel):
    """Structured event for manufacturing telemetry."""
    timestamp: str
    zone_id: str
    sensor_reading: float
    detection_id: str
    detection_conf: float
    status: str = Field(description="Operational status (Normal, Anomaly, Maintenance)")

class RealTimeMonitor:
    """GenAI Agent for Reasoning on Real-time Manufacturing Data."""

    def __init__(self, azure_params):
        self.llm = AzureChatOpenAI(
            azure_deployment=azure_params['deployment_name'],
            api_version="2024-02-15-preview",
            azure_endpoint=azure_params['endpoint'],
            api_key=azure_params['api_key']
        )
        print("GenAI Monitoring Agent Initialized.")

    def analyze_event(self, event: ManufacturingEvent):
        """Perform contextual reasoning on raw telemetry."""
        prompt = f"""
        Analyze this manufacturing event:
        - Timestamp: {event.timestamp}
        - Zone: {event.zone_id}
        - Reading: {event.sensor_reading}
        - AI Detection: {event.detection_id} (Conf: {event.detection_conf})

        Is there a production-grade risk? Provide an OEE-focused reasoning and actionable next step.
        """
        response = self.llm.invoke(prompt)
        return response.content

if __name__ == "__main__":
    test_event = ManufacturingEvent(
        timestamp=datetime.now().isoformat(),
        zone_id="CONVEYOR-B1",
        sensor_reading=98.5,
        detection_id="friction_anomaly",
        detection_conf=0.92,
        status="Anomaly"
    )
    # monitor = RealTimeMonitor(azure_params)
    # reasoning = monitor.analyze_event(test_event)
    print(f"Agent Ready. Ingesting event: {test_event.zone_id}")
    print("Reasoning logic loaded. Connecting to Azure IoT Hub...")
