from sagemaker.core import image_uris

try:
    training_image = image_uris.retrieve(
        framework="pytorch",
        region="us-east-1",
        version="2.9",
        py_version="py312",
        instance_type="ml.m5.xlarge",
        image_scope="training"
    )
    print(training_image)

except Exception as e:
    print(e)