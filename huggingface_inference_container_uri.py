from sagemaker.core import image_uris

uri = image_uris.retrieve(
    framework="huggingface", #this is what gets us the inference-capable container (has serve built in), unlike pytorch-training before.
    region="us-east-1",
    version="4.51.3",  
    base_framework_version="pytorch2.6.0",
    py_version="py312",
    image_scope="inference",
    instance_type="ml.t2.medium"
)
print(uri)