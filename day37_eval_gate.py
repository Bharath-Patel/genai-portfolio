import sys
from day15_rag import retrieve, answer_question
from datasets import Dataset
from dotenv import load_dotenv
from ragas.metrics import faithfulness, context_precision
from ragas import evaluate
from langchain_groq import ChatGroq
from ragas.llms import LangchainLLMWrapper
import os

load_dotenv()

FAITHFULNESS_THRESHOLD = 0.6
CONTEXT_PRECISION = 0.8

eval_llm = LangchainLLMWrapper(ChatGroq(
    model = "openai/gpt-oss-120b",
    temperature = 0,
    api_key = os.getenv("GROQ_API_KEY")
))

test_questions = [
    "How do I control who can access my S3 bucket?",
    "What triggers a Lambda function to run?",
    "How does Terraform know what infrastructure already exists?",
]

reference_answers = [
    "You can control S3 bucket access using bucket policies, IAM user policies, access control lists (ACLs), and S3 Access Points. Bucket policies and IAM policies are recommended over ACLs.",
    "Lambda functions are triggered by connecting them to an event source such as API Gateway, Amazon S3, Amazon SQS, EventBridge, or other AWS services.",
    "Terraform performs a refresh before any operation to update its state file with the real infrastructure, comparing configured resources against actual remote objects.",
]

def run_eval():
    questions,answers, contexts = [],[],[]
    for q in test_questions:
        retrieved_chunks, top_score = retrieve(q)
        answer, sources = answer_question(q)
        questions.append(q)
        answers.append(answer)
        contexts.append([ r.payload["text"] for r in retrieved_chunks])      

    eval_dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "reference": reference_answers
    })

    result = evaluate(
        eval_dataset,
        metrics=[faithfulness,context_precision],
        llm=eval_llm
    )
    return result

if __name__ == "__main__":
    result = run_eval()
    df = result.to_pandas()
    failed = False
    avg_faithfulness = df["faithfulness"].mean()
    avg_context_precision = df["context_precision"].mean()

    print(f"Average faithfulness is {avg_faithfulness:.3f}, (threshold is {FAITHFULNESS_THRESHOLD})")
    print(f"Average context_precision is {avg_context_precision:.3f}, (threshold is {CONTEXT_PRECISION})")


    if avg_faithfulness < FAITHFULNESS_THRESHOLD:
        print(f"FAILED: faithfulness {avg_faithfulness:.3f} below threshold {FAITHFULNESS_THRESHOLD}")
        failed = True
    if avg_context_precision < CONTEXT_PRECISION:
        print(f"FAILED: context precision {avg_context_precision:.3f} below threshold {CONTEXT_PRECISION_THRESHOLD}")
        failed = True
    
    if failed:
        sys.exit(1)
    else:
        print("PASSED: all metrics meet threshold")
        sys.exit(0)

