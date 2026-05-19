import os
from flask import Flask, render_template, request, send_from_directory
import joblib
import numpy as np

app = Flask(__name__, static_folder='Dashboard/dist', static_url_path='/', template_folder='Dashboard/dist')

MODEL_PATH = "artifacts/models/model.pkl"
SCALER_PATH = "artifacts/processed/scaler.pkl"

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

FEATURES = [
                'Operation_Mode', 'Temperature_C', 'Vibration_Hz',
                'Power_Consumption_kW', 'Network_Latency_ms', 'Packet_Loss_%',
                'Quality_Control_Defect_Rate_%', 'Production_Speed_units_per_hr',
                'Predictive_Maintenance_Score', 'Error_Rate_%','Year', 'Month', 'Day', 'Hour'
            ]

LABELS = {
    0:"High",
    1:"Low",
    2:"Medium"
}


@app.route("/", defaults={'path': ''})
@app.route("/<path:path>")
def serve_dashboard(path):
    # Match specific existing files in the static folder (like assets)
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    # Catch-all serving React's index.html for frontend routing
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict_api():
    try:
        data = request.get_json()
        input_data = [float(data.get(feature, 0)) for feature in FEATURES]
        input_array = np.array(input_data).reshape(1, -1)
        scaled_array = scaler.transform(input_array)
        pred = model.predict(scaled_array)[0]
        prediction = LABELS.get(pred, "Unknown")
        return {"prediction": prediction, "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "error"}, 400

@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    # In a real app, this would query your ProductionBatch.db
    # For now, we simulate live drift to show the dashboard is "alive"
    import random
    return {
        "avg_oee": random.randint(82, 94),
        "active_machines": random.randint(8, 12),
        "total_machines": 12,
        "units_produced": random.randint(15200, 15800),
        "critical_alerts": random.randint(0, 3),
        "yield_rate": round(random.uniform(94.5, 98.2), 1),
        "uptime": 99.4,
        "status": "success"
    }

if __name__=="__main__":
    app.run(debug=True , host="0.0.0.0" , port=5000)