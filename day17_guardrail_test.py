from day15_rag import answer_question

test_cases = [
    "What is the capital of France?",           
    "How do I set up a Kubernetes ingress controller?",  
    "Why would my Lambda function time out?",   
    "How do I control who can access my S3 bucket?"
]

for q in test_cases:
    answer, sources = answer_question(q)
    top_score = sources[0].score if sources else 0
    print(f"Question: {q}")
    print(f"Top score: {top_score:.3f}")
    print(f"Answer: {answer}\n")