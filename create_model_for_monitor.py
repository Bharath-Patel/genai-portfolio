from sagemaker.serve.model_builder import ModelBuilder
from sagemaker.core.jumpstart.configs import JumpStartConfig
from sagemaker.train.configs import Compute

compute = Compute(instance_type="ml.g5.xlarge")

jumpstart_config = JumpStartConfig(model_id="huggingface-textembedding-all-MiniLM-L6-v2")

model_builder = ModelBuilder.from_jumpstart_config(
    jumpstart_config=jumpstart_config,
    compute=compute,
    role_arn="arn:aws:iam::053285355767:role/sagemaker-execution-role",
)

print("Building model configuration...")
core_model = model_builder.build(model_name="genai-embedding-model")
print("Model built. Check the console for its exact Model name before continuing.")