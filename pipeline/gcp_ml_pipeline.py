import google.cloud.aiplatform as aip

def submit_gcp_ml_job(workspace_config):
    """Schedules a systematic SLM training or processing job on GCP Vertex AI."""
    
    # 1. Initialize Vertex AI
    aip.init(
        project=workspace_config['project_id'],
        location=workspace_config['region'],
        staging_bucket=workspace_config['staging_bucket']
    )

    # 2. Define Custom Training Job
    # Requires a pre-built docker container pushed to GCR/Artifact Registry
    job = aip.CustomContainerTrainingJob(
        display_name="SLM-Manufacturing-Fine-Tuning",
        container_uri=f"gcr.io/{workspace_config['project_id']}/supermart-genai-env:latest",
        command=["python", "src/slm_finetuner.py", "--data", workspace_config.get('training_data_uri', 'gs://your-bucket/training-data/')],
    )

    # 3. Submit the job
    print("Submitting Systematic GCP Vertex AI Job...")
    returned_job = job.run(
        machine_type="a2-highgpu-1g", # A2 machine types have A100 GPUs
        accelerator_type="NVIDIA_TESLA_A100",
        accelerator_count=1,
        replica_count=1,
        sync=False # Don't block execution
    )
    
    print(f"Systematic GCP Vertex AI Job submitted. Resource Name: {returned_job.resource_name}")
    return returned_job

if __name__ == "__main__":
    test_config = {
        "project_id": "YOUR_PROJECT_ID",
        "region": "us-central1",
        "staging_bucket": "gs://YOUR_STAGING_BUCKET",
        "training_data_uri": "gs://YOUR_STAGING_BUCKET/training-data/"
    }
    # submit_gcp_ml_job(test_config)
    print("GCP Vertex AI Systematic Pipeline ready. Defined Job Configuration.")
