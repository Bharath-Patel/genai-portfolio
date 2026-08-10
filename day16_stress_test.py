from day15_rag import answer_question

test_questions = [
    # Straightforward per-document (baseline check)
    "How do I control who can access my S3 bucket?",
    "What triggers a Lambda function to run?",
    "How does Terraform know what infrastructure already exists?",

    # Outside document scope entirely - should say "I don't know"
    "What is the capital of France?",
    "How do I set up a Kubernetes ingress controller?",

    # Ambiguous / cross-document
    "How do I store and manage infrastructure state?",

    # Tricky phrasing - same intent, different wording than the docs
    "What's the cheapest way to keep rarely-used files in AWS?",
    "Why would my Lambda function time out?",

    # Personal notes - casual phrasing test
    "Why does streaming feel faster even if it isn't?",

    # Deliberately vague, could go multiple ways
    "What should I be careful about?",
]

log = []

for i,question in enumerate(test_questions):
    print(f"\n {'=' * 80}")
    print(f"Test {i+1} : {question}")
    answer, sources = answer_question(question)
    print(f"Answer : {answer}")
    print(f"Source{[s.payload['source'] + '(' f'{s.score:.3f}' + ')' for s in sources]}")

    log.append({
        'question' : question,
        'answer' : answer,
        'source' : [s.payload['source'] for s in sources],
        'top_score': sources[0].score if sources else None
    }
    )

    import json

    with open('day16_test_log.json',"w") as f:
        json.dump(log,f, indent=2)

    print(f"\n\nSaved {len(log)} test results to day16_test_log.json")