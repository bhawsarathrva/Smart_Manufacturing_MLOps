# Smart Manufacturing Dashboard

This is the real-time AI-powered monitoring dashboard for the Smart Manufacturing Platform. It visualizes machine status, predictive analytics, and provides direct interaction with the project's custom ML pipeline.

## 🔗 ML Model Pipeline Connectivity

The dashboard connects to the local Machine Learning model serving layer via a built-in API proxy.

### 1. Data Flow Architecture
The connectivity works through three main layers:
1. **Frontend (React)**: Captures sensor inputs (Temp, Vibration, etc.) in the `PredictiveAnalytics` page.
2. **API Client (`mlClient.js`)**: Sends a JSON POST request to the `/api/ml/predict` endpoint.
3. **Vite Proxy**: Re-routes these requests from your dashboard's development server to the Flask backend running on `http://localhost:5000`.
4. **Backend (`application.py`)**: Runs the scikit-learn random forest model (`model.pkl`) to generate maintenance risk predictions and returns them as JSON.

### 2. Integration Points
- **Predictive Analytics Page**: Features a live "Machine Learning Pipeline Inference" card for real-time model testing.
- **AI Manufacturing Assistant**: Uses LLM reasoning (Phi-3) alongside real-world factory status data.

## 🛠️ Required Dependencies

To run the dashboard and its ML features, you must install the following dependency chains:

### Frontend Dependencies (Node.js)
In the `/CODE/Dashboard` directory, run:
```bash
npm install
```
Key packages include:
- `lucide-react`: For iconography.
- `recharts`: For data visualization.
- `tanstack/react-query`: For server state management.
- `framer-motion`: For premium UI animations.

### Backend ML Dependencies (Python)
The dashboard requires the prediction backend to be active. In the `/CODE` root directory, install:
```bash
pip install flask numpy pandas scikit-learn joblib
```

## 🚀 Getting Started

### 1. Start the ML Pipeline Server
Ensure your model artifacts are present and start the backend:
```bash
cd ..
python application.py
```

### 2. Start the Dashboard
In a separate terminal, launch the dev server:
```bash
cd Dashboard
npm run dev
```

### 3. Environment Configuration
Create a `.env` or `.env.local` file with your Base44 credentials if you're using integrated entities:
```env
VITE_BASE44_APP_ID=your_id
VITE_BASE44_APP_BASE_URL=your_url
```

## 📂 Key Files for Connectivity
- `src/api/mlClient.js`: Contains the logic for asynchronous calls to the Flask ML model.
- `vite.config.js`: Defines the proxy configuration that bridges frontend and backend communications.
- `src/pages/PredictiveAnalytics.jsx`: The primary UI for interacting with internal ML models.
