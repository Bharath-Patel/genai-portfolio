import json
import boto3

runtime = boto3.client("sagemaker-runtime", region_name="us-east-1")

questions = [
    "How do I control who can access my S3 bucket?",
    "What triggers a Lambda function to run?",
    "How does Terraform manage state?",
    "What is S3 versioning used for?",
    "How do I set up IAM roles for Lambda?",
    "What is a Terraform backend?",
    "How does S3 Object Lock work?",
    "What is the difference between FastAPI and Uvicorn?",
]

for q in questions:
    response = runtime.invoke_endpoint(
        EndpointName="genai-monitor-endpoint",
        ContentType="application/json",
        Body=json.dumps({"inputs": q}),
    )
    result = json.loads(response["Body"].read())
    print(f"{q} -> vector of {len(result[0])} numbers")