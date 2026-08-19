from day33_self_correction import workflow

test_topics = [
    "How do I control who can access my S3 bucket?",       # known-good, tested Day 33
    "What triggers a Lambda function to run?",               # known-good, different doc
    "How does Terraform know what infrastructure exists?",   # known-good, different doc
    "What is the best programming language for AI in 2026?", # deliberately out of scope
]

for topic in test_topics:
    print(f"\n{'='*80}")
    print(f"Topic : {topic}")
    result = workflow.invoke({"topic" : topic})
    print(f" Attempts: {result['revision_count']}")
    print(f"Final post : {result['final_post']}")
    print(f"FInal feedback: {result.get('feedback','N/A')}")
