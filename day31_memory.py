import os
import time
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from dotenv import load_dotenv
from day15_rag import answer_question
from day39_cost_guardrail import CallBudget, LLMCallBudgetExceeded

load_dotenv()

_kb_search_call_count = {"count": 0}
request_budget = CallBudget(max_calls=2)

@tool
def knowledge_base_search(question: str) -> str:
    """Searches AWS S3, AWS Lambda, and Terraform state documentation, plus personal 
    DevOps/GenAI learning notes, to answer technical questions about these topics. 
    This tool should only be called ONCE per user question."""
    try:
        request_budget.record_call()
    except LLMCallBudgetExceeded as e:
        return f"Call budget exceeded for this request. You must answer using information already gathered. ({e})"

    _kb_search_call_count["count"] += 1
    if _kb_search_call_count["count"] > 1:
        return "You already searched the knowledge base for this question. Use the previous result to answer - do not search again."
    answer, sources = answer_question(question)
    return answer

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY")
)

agent = create_agent(
    llm,
    tools=[knowledge_base_search],
    system_prompt=(
        "You are a helpful assistant with access to a technical knowledge base. "
        "Call the knowledge base at most once per new question. Pay attention to "
        "the full conversation history to understand follow-up questions."
    )
)

conversation_history = []

def ask(question: str, max_retries: int = 3):
    global conversation_history
    _kb_search_call_count["count"] = 0
    request_budget.calls_made = 0

    attempt_history = conversation_history + [{"role": "user", "content": question}]

    for attempt in range(max_retries):
        try:
            result = agent.invoke(
                {"messages": attempt_history},
                config={"recursion_limit": 10}
            )
            conversation_history = result["messages"]
            final_message = conversation_history[-1]
            print(f"\nQ: {question}")
            print(f"A: {final_message.content}")
            return
        except Exception as e:
            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(1)

    print(f"\nQ: {question}")
    print("A: Sorry, I'm having trouble processing that right now. Please try again.")


if __name__ == "__main__":
    ask("How do I control who can access my S3 bucket?")
    ask("What about for Lambda instead?")