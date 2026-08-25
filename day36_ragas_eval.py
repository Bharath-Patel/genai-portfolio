from day15_rag import retrieve, answer_question, build_prompt
from ragas import evaluate
from ragas.metrics import faithfulness, context_precision
from datasets import Dataset
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from ragas.llms import LangchainLLMWrapper #Ragas needs an LLM to actually perform its judgments

load_dotenv()

eval_llm=LangchainLLMWrapper(ChatGroq(
    model ="openai/gpt-oss-120b",
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

questions = []
answers = []
contexts = []
for i, q in enumerate(test_questions):
    retrieved_chunks, top_score = retrieve(q)
    answer, sources = answer_question(q)

    questions.append(q)
    answers.append(answer)
    contexts.append([r.payload["text"] for r in retrieved_chunks])

eval_dataset = Dataset.from_dict({ #Dataset.from_dict(...): Converts a standard Python dictionary into a Hugging Face Dataset object,commonly used for evaluating AI models(like RAG systems)
    "question": questions,
    "answer": answers,
    "contexts": contexts,
    "reference": reference_answers
})

result = evaluate(
    eval_dataset,
    metrics = [faithfulness,context_precision],
    llm = eval_llm
)

print(result)
print(result.to_pandas())
