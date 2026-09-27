---
tags:
- sentence-transformers
- sentence-similarity
- feature-extraction
- generated_from_trainer
- dataset_size:58
- loss:MultipleNegativesRankingLoss
base_model: sentence-transformers/all-MiniLM-L6-v2
widget:
- source_sentence: Why does Terraform require state and cannot function without it?
  sentences:
  - The primary purpose of Terraform state is to store bindings between objects in
    a remote system and resource instances declared in your configuration. When Terraform
    creates a remote object in response to a change of configuration, it records the
    identity of that remote object against a particular resource instance, and potentially
    updates or deletes that object in response to future configuration changes.
  - Amazon Simple Storage Service (Amazon S3) is an object storage service that offers
    industry-leading scalability, data availability, security, and performance. Customers
    of all sizes and industries can use Amazon S3 to store and protect any amount
    of data for a range of use cases, such as data lakes, websites, mobile applications,
    backup and restore, archive, enterprise applications, IoT devices, and big data
    analytics. Amazon S3 provides management features so that you can optimize, organize,
  - For more information on why Terraform requires state and why Terraform cannot
    function without state, please see the page state purpose.
- source_sentence: What compute primitives does AWS Lambda provide?
  sentences:
  - 'Storage logging and monitoring

    Amazon S3 provides logging and monitoring tools that you can use to monitor and
    control how your Amazon S3 resources are being used. For more information, see
    Monitoring tools.


    Automated monitoring tools

    Amazon CloudWatch metrics for Amazon S3 – Track the operational health of your
    S3 resources and configure billing alerts when estimated charges reach a user-defined
    threshold.'
  - 'While FastAPI is the framework you use to build the endpoints and logic, Uvicorn
    is the actual engine (the web server) that hosts your application and listens
    for incoming web requests.      Day 4     Task: Learn prompt basics: system prompt, few-shot, temperature — apply to your
    endpoint.      1)Every conversation with a LLM has  at least 2 voices , system prompt and user
    prompt     system message -> set by the developer , sort of a job description of what the
    LLM is and should do. Ex: you are an expert in'
  - 'AWS Lambda is a serverless compute service that lets you run code without provisioning
    or managing servers. Lambda automatically manages the underlying infrastructure
    – including server maintenance, capacity provisioning, scaling, and patching –
    so you can focus on your application logic.


    Lambda provides two compute primitives, each designed for different workload patterns:'
- source_sentence: What information does the table of supported Lambda runtimes provide?
  sentences:
  - Amazon S3 provides strong read-after-write consistency for PUT and DELETE requests
    of objects in your Amazon S3 bucket in all AWS Regions. This behavior applies
    to both writes of new objects as well as PUT requests that overwrite existing
    objects and DELETE requests. In addition, read operations on Amazon S3 Select,
    Amazon S3 access control lists (ACLs), Amazon S3 Object Tags, and object metadata
    (for example, the HEAD object) are strongly consistent. For more information,
    see Amazon S3 data
  - 'The terraform output command has a -json option, for obtaining either the full
    set of root module output values or a specific named output value from the latest
    state snapshot.

    The terraform show command has a -json option for inspecting the latest state
    snapshot in full, and also for inspecting saved plan files which include a copy
    of the prior state at the time the plan was made.'
  - 'Supported runtimes


    The following table lists the supported Lambda runtimes and projected deprecation
    dates. After a runtime is deprecated, you''re still able to create and update
    functions for a limited period. For more information, see Runtime use after deprecation.
    The table provides the currently forecasted dates for runtime deprecation, based
    on our Runtime deprecation policy. These dates are provided for planning purposes
    and are subject to change.'
- source_sentence: How does the choice of runtime affect performance in AWS Lambda?
  sentences:
  - S3 Inventory with Inventory reports – Audit and report on objects and their corresponding
    metadata and configure other Amazon S3 features to take action in Inventory reports.
    For example, you can report on the replication and encryption status of your objects.
    For a list of all the metadata available for each object in Inventory reports,
    see Amazon S3 Inventory list.
  - 'Lambda runtimes


    Lambda supports multiple languages through the use of runtimes. A runtime provides
    a language-specific environment that relays invocation events, context information,
    and responses between Lambda and the function. You can use runtimes that Lambda
    provides, or build your own.'
  - Lambda is agnostic to your choice of runtime. For simple functions, interpreted
    languages like Python and Node.js offer the fastest performance. For functions
    with more complex computation, compiled languages like Java are often slower to
    initialize but run quickly in the Lambda handler. Choice of runtime is also influenced
    by developer preference and language familiarity.
- source_sentence: What feature of Amazon S3 allows you to keep multiple versions
    of an object in the same bucket and restore objects that are accidentally deleted
    or overwritten?
  sentences:
  - 'AWS CloudTrail – Record actions taken by a user, a role, or an AWS service in
    Amazon S3. CloudTrail logs provide you with detailed API tracking for S3 bucket-level
    and object-level operations.


    Manual monitoring tools

    Server access logging – Get detailed records for the requests that are made to
    a bucket. You can use server access logs for many use cases, such as conducting
    security and access audits, learning about your customer base, and understanding
    your Amazon S3 bill.'
  - S3 provides features that you can configure to support your specific use case.
    For example, you can use S3 Versioning to keep multiple versions of an object
    in the same bucket, which allows you to restore objects that are accidentally
    deleted or overwritten.
  - 'Amazon S3 Storage Lens – Understand, analyze, and optimize your storage. S3 Storage
    Lens provides 60+ usage and activity metrics and interactive dashboards to aggregate
    data for your entire organization, specific accounts, AWS Regions, buckets, or
    prefixes.


    Storage Class Analysis – Analyze storage access patterns to decide when it''s
    time to move data to a more cost-effective storage class.'
pipeline_tag: sentence-similarity
library_name: sentence-transformers
---

# SentenceTransformer based on sentence-transformers/all-MiniLM-L6-v2

This is a [sentence-transformers](https://www.SBERT.net) model finetuned from [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2). It maps sentences & paragraphs to a 384-dimensional dense vector space and can be used for retrieval.

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
- **Base model:** [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) <!-- at revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41 -->
- **Maximum Sequence Length:** 256 tokens
- **Output Dimensionality:** 384 dimensions
- **Similarity Function:** Cosine Similarity
- **Supported Modality:** Text
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Sentence Transformers on Hugging Face](https://huggingface.co/models?library=sentence-transformers)

### Full Model Architecture

```
SentenceTransformer(
  (0): Transformer({'transformer_task': 'feature-extraction', 'modality_config': {'text': {'method': 'forward', 'method_output_name': 'last_hidden_state'}}, 'module_output_name': 'token_embeddings', 'architecture': 'BertModel'})
  (1): Pooling({'embedding_dimension': 384, 'pooling_mode': 'mean', 'include_prompt': True})
  (2): Normalize({})
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```
Then you can load this model and run inference.
```python
from sentence_transformers import SentenceTransformer

# Download from the 🤗 Hub
model = SentenceTransformer("sentence_transformers_model_id")
# Run inference
sentences = [
    'What feature of Amazon S3 allows you to keep multiple versions of an object in the same bucket and restore objects that are accidentally deleted or overwritten?',
    'S3 provides features that you can configure to support your specific use case. For example, you can use S3 Versioning to keep multiple versions of an object in the same bucket, which allows you to restore objects that are accidentally deleted or overwritten.',
    "Amazon S3 Storage Lens – Understand, analyze, and optimize your storage. S3 Storage Lens provides 60+ usage and activity metrics and interactive dashboards to aggregate data for your entire organization, specific accounts, AWS Regions, buckets, or prefixes.\n\nStorage Class Analysis – Analyze storage access patterns to decide when it's time to move data to a more cost-effective storage class.",
]
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 384]

# Get the similarity scores for the embeddings
similarities = model.similarity(embeddings, embeddings)
print(similarities)
# tensor([[1.0000, 0.8593, 0.3513],
#         [0.8593, 1.0000, 0.4497],
#         [0.3513, 0.4497, 1.0000]])
```
<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 58 training samples
* Columns: <code>sentence_0</code> and <code>sentence_1</code>
* Approximate statistics based on the first 58 samples:
  |          | sentence_0                                                                         | sentence_1                                                                          |
  |:---------|:-----------------------------------------------------------------------------------|:------------------------------------------------------------------------------------|
  | type     | string                                                                             | string                                                                              |
  | modality | text                                                                               | text                                                                                |
  | details  | <ul><li>min: 11 tokens</li><li>mean: 21.81 tokens</li><li>max: 44 tokens</li></ul> | <ul><li>min: 14 tokens</li><li>mean: 77.19 tokens</li><li>max: 127 tokens</li></ul> |
* Samples:
  | sentence_0                                                                                                         | sentence_1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
  |:-------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
  | <code>What are Lambda MicroVMs and what are their key features for providing isolated compute environments?</code> | <code>Lambda MicroVMs – Isolated compute environments with near-instant startup and state retention for up to 8 hours. Designed for workloads needing a dedicated compute environment for each individual user or job. Lambda manages isolation, capacity, and networking. Your application uses Lambda MicroVMs APIs and HTTPS endpoints to connect each user/job to their compute environment.<br><br>Lambda Functions and Lambda MicroVMs share a common serverless foundation:</code> |
  | <code>What options can I use to manage access permissions for S3 buckets and objects?</code>                       | <code>Buckets and the objects in them are private and can be accessed only if you explicitly grant access permissions. You can use bucket policies, AWS Identity and Access Management (IAM) policies, access control lists (ACLs), and S3 Access Points to manage access.</code>                                                                                                                                                                                                         |
  | <code>What are Lambda runtimes and how do they work?</code>                                                        | <code>Lambda runtimes<br><br>Lambda supports multiple languages through the use of runtimes. A runtime provides a language-specific environment that relays invocation events, context information, and responses between Lambda and the function. You can use runtimes that Lambda provides, or build your own.</code>                                                                                                                                                                   |
* Loss: [<code>MultipleNegativesRankingLoss</code>](https://sbert.net/docs/package_reference/sentence_transformer/losses.html#multiplenegativesrankingloss) with these parameters:
  ```json
  {
      "scale": 20.0,
      "similarity_fct": "cos_sim",
      "gather_across_devices": false,
      "directions": [
          "query_to_doc"
      ],
      "partition_mode": "joint",
      "hardness_mode": null,
      "hardness_strength": 0.0
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16
- `multi_dataset_batch_sampler`: round_robin

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `per_device_train_batch_size`: 16
- `num_train_epochs`: 3
- `max_steps`: -1
- `learning_rate`: 5e-05
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: None
- `warmup_steps`: 0
- `optim`: adamw_torch_fused
- `optim_args`: None
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `optim_target_modules`: None
- `gradient_accumulation_steps`: 1
- `average_tokens_across_devices`: True
- `max_grad_norm`: 1
- `label_smoothing_factor`: 0.0
- `bf16`: False
- `fp16`: False
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `use_cache`: False
- `neftune_noise_alpha`: None
- `torch_empty_cache_steps`: None
- `auto_find_batch_size`: False
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `include_num_input_tokens_seen`: no
- `log_level`: passive
- `log_level_replica`: warning
- `disable_tqdm`: False
- `project`: huggingface
- `trackio_space_id`: None
- `trackio_bucket_id`: None
- `trackio_static_space_id`: None
- `per_device_eval_batch_size`: 16
- `prediction_loss_only`: True
- `eval_on_start`: False
- `eval_do_concat_batches`: True
- `eval_use_gather_object`: False
- `eval_accumulation_steps`: None
- `include_for_metrics`: []
- `batch_eval_metrics`: False
- `save_only_model`: False
- `save_on_each_node`: False
- `enable_jit_checkpoint`: False
- `push_to_hub`: False
- `hub_private_repo`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_always_push`: False
- `hub_revision`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `restore_callback_states_from_checkpoint`: False
- `full_determinism`: False
- `seed`: 42
- `data_seed`: None
- `use_cpu`: False
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `parallelism_config`: None
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `dataloader_prefetch_factor`: None
- `remove_unused_columns`: True
- `label_names`: None
- `train_sampling_strategy`: random
- `length_column_name`: length
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `ddp_static_graph`: None
- `ddp_backend`: None
- `ddp_timeout`: 1800
- `fsdp`: None
- `fsdp_config`: None
- `deepspeed`: None
- `debug`: []
- `skip_memory_metrics`: True
- `do_predict`: False
- `resume_from_checkpoint`: None
- `warmup_ratio`: None
- `local_rank`: -1
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: round_robin
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Time
- **Training**: 3.8 seconds

### Framework Versions
- Python: 3.11.1
- Sentence Transformers: 5.6.0
- Transformers: 5.13.1
- PyTorch: 2.13.0
- Accelerate: 1.15.0
- Datasets: 5.0.1
- Tokenizers: 0.22.2

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

#### MultipleNegativesRankingLoss
```bibtex
@misc{oord2019representationlearningcontrastivepredictive,
      title={Representation Learning with Contrastive Predictive Coding},
      author={Aaron van den Oord and Yazhe Li and Oriol Vinyals},
      year={2019},
      eprint={1807.03748},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/1807.03748},
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->