import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv()

bedrock = boto3.client('bedrock-runtime',
                    region_name= os.getenv("AWS_REGION"),
                    aws_access_key_id= os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"))

def call_bedrock(question: str):
    response = bedrock.converse(
        modelId = "amazon.nova-micro-v1:0",
        messages = [{
            'role': 'user',
            'content': [{'text': question}]
       }],
       inferenceConfig = {"temperature" : 0}
    )

    return response["output"]["message"]["content"][0]["text"]

if __name__ == "__main__":
    answer = call_bedrock("What is the capital of India?")
    print(answer)