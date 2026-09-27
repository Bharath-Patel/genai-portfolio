import boto3

# Initialize the SageMaker client
sagemaker_client = boto3.client('sagemaker', region_name='us-east-1')

# List of specific model names to delete
models_to_delete = [
    "pipelines-kwidzvlefz0e-Model-A07B12-H3WJyOWfFI",
    "pipelines-nm1zjfesz9q8-Model-A07B12-p5KDfWT20z",
    "pipelines-84a3p88fd8ww-Model-A07B12-3NJGjyye8w",
    "pipelines-13ps87elenr7-Model-A07B12-8WH2IddDhw",
    "pipelines-4qftishklg71-Model-A07B12-IqUIUS5exJ",
    "minilm-finetuned-inference-model",
    "pipelines-pg0aszkqrxpi-Model-A07B12-rPAnJgKmEd",
    "pipelines-0utzvb1w7tdi-Model-A07B12-f6Ebj2oiTO"
]

for model_name in models_to_delete:
    try:
        print(f"Deleting {model_name}...")
        sagemaker_client.delete_model(ModelName=model_name)
        print(f"Successfully deleted {model_name}")
    except Exception as e:
        print(f"Failed to delete {model_name}: {e}")