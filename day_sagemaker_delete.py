import boto3

sm_client=boto3.client("sagemaker")
sm_client.delete_endpoint(
    EndpointName='genai-embedding-endpoint'
)
sm_client.delete_endpoint_config(
    EndpointConfigName='genai-embedding-endpoint'
)
print("Endpoint and endpoint config deleted.")