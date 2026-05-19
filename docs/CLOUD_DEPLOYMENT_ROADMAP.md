# ☁️ Cloud Deployment Roadmap (GCP)

This roadmap outlines the steps to take the Smart Manufacturing Platform from local development to a production-grade cloud environment on Google Cloud Platform.

## Phase 1: Containerization (Docker)
1.  **Backend Dockerization**: Create a Dockerfile for the Flask app.
    *   Base image: `python:3.9-slim`.
    *   Environment: `requirements.txt`.
2.  **Frontend Dockerization**: Create a multi-stage Dockerfile for React.
    *   Build stage: `node:18`.
    *   Production stage: `nginx:alpine` to serve static files.
3.  **Local Validation**: Run both containers using `docker-compose` to ensure connectivity.

## Phase 2: Google Cloud Infrastructure
1.  **Artifact Registry**: Set up a private repository on GCP to store container images.
2.  **Cloud SQL**: Migrate local SQLite `.db` files to a Managed PostgreSQL instance.
    *   Configure Private IP and IAM authentication.
3.  **VPC Networking**: Set up a Virtual Private Cloud to secure communication between services.

## Phase 3: Deployment & Orchestration
1.  **Google Cloud Run (Recommended)**:
    *   Deploy the Flask API for easy scaling and "scale-to-zero" cost savings.
2.  **Google Cloud Storage / Firebase Hosting**:
    *   Host the compiled React frontend for high availability.
3.  **Cloud Load Balancing**:
    *   Use a Global Load Balancer with an SSL certificate to unified the frontend and backend under a single domain.

## Phase 4: Intelligence & Scaling
1.  **Vertex AI**:
    *   Migrate the `model.pkl` to a Vertex AI Endpoint for high-performance inference.
    *   Use Vertex AI Pipelines (Kubeflow) to automate model retraining.
2.  **Cloud Monitoring & Logging**:
    *   Set up Dashboards in Cloud Monitoring for real-time uptime and error tracking.

---
*For specific implementation scripts, contact the DevOps lead.*
