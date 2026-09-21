from sagemaker.serve.model_builder import ModelBuilder
from sagemaker.core.jumpstart.configs import JumpStartConfig
from sagemaker.train.configs import Compute
import json

compute = Compute(instance_type="ml.g5.xlarge")

jumpstart_config=JumpStartConfig(model_id = "huggingface-textembedding-all-MiniLM-L6-v2")

model_builder = ModelBuilder.from_jumpstart_config(
    jumpstart_config = jumpstart_config,
    compute =compute,
    role_arn = "arn:aws:iam::053285355767:role/sagemaker-execution-role"
)

print("Building model configuration...")
core_model = model_builder.build(model_name="genai-embedding-model")

print("Deploying endpoint - this will take several minutes...")
endpoint = model_builder.deploy(endpoint_name="genai-embedding-endpoint")
print(f"Endpoint deployed: {endpoint}")


print("Endpoint deployed. Running test inferences...")

print("Run day_sagemaker_delete.py when you're ready to tear it down.")