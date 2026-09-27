import json
import boto3

runtime = boto3.client("sagemaker-runtime", region_name="us-east-1")

test_sentences = [
    "How do I control who can access my S3 bucket?",
    "What triggers a Lambda function to run?",
    "How does Terraform manage state?",
]

for sentence in test_sentences:
    response = runtime.invoke_endpoint(
        EndpointName="minilm-finetuned-endpoint-v2",
        ContentType="application/json",
        Body=json.dumps({"inputs": sentence}),
    )
    result = json.loads(response["Body"].read())
    print(f"\nInput: {sentence}")
    print(f"Output: {result}")