import json
import argparse
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient, command, Input
from azure.ai.ml.entities import Environment, BuildContext

def submit_azure_ml_job(workspace_config):
    """Schedules a systematic SLM training or processing job on Azure ML compute."""
    
    # 1. Connect to Azure Workspace
    ml_client = MLClient(
        DefaultAzureCredential(),
        workspace_config['subscription_id'],
        workspace_config['resource_group'],
        workspace_config['workspace_name']
    )

    # 2. Define Training Environment
    env = Environment(
        name="supermart-genai-env",
        build=BuildContext(path="./CODE")
    )

    # 3. Define Training Command
    job = command(
        code="./CODE",
        command="python src/slm_finetuner.py --data ${{inputs.training_data}}",
        inputs={
            "training_data": Input(type="uri_folder", path="azureml://datastores/workspaceblobstore/paths/training-data/")
        },
        environment=env,
        compute="gpu-cluster-a100", # Example compute cluster name
        display_name="SLM-Manufacturing-Fine-Tuning",
        description="Systematic fine-tuning of Phi-3-Vision for anomaly detection."
    )

    # 4. Submit the job
    returned_job = ml_client.jobs.create_or_update(job)
    print(f"Systematic Azure ML Job submitted. Status: {returned_job.services}")
    return returned_job

if __name__ == "__main__":
    test_config = {
        "subscription_id": "YOUR_SUB_ID",
        "resource_group": "YOUR_RG",
        "workspace_name": "YOUR_WORKSPACE"
    }
    # submit_azure_ml_job(test_config)
    print("Azure ML Systematic Pipeline ready. Defined Job Configuration.")
