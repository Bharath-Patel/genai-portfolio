from langchain.agents import create_agent 
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from dotenv import load_dotenv
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from day15_rag import answer_question

load_dotenv()
_kb_search_call_count = {"count": 0}

@tool
def calculator(expression: str) -> str:
    """Evaluates a basic math expression, e.g. '15% of 200' should be passed as '0.15 * 200'."""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

@tool
def knowledge_base_search(question: str) -> str:
    """Searches AWS S3, AWS Lambda, and Terraform state documentation, plus personal 
    DevOps/GenAI learning notes, to answer technical questions about these topics. 
    This tool should only be called ONCE per user question."""
    
    _kb_search_call_count["count"] += 1
    
    if _kb_search_call_count["count"] > 1:
        return "You already searched the knowledge base for this question. Use the previous result to answer - do not search again."
    
    print(f">>> Tool called with: {question}")
    answer, sources = answer_question(question)
    print(f">>> Tool returned: {answer[:50]}...")
    return answer

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

agent = create_agent(
    llm,
    tools=[calculator, knowledge_base_search],
    system_prompt=(
        "You are a helpful assistant with access to a calculator and a technical knowledge base. "
        "Call each tool at most once per question. Once a tool gives you an answer, respond to "
        "the user immediately rather than calling the same or similar tool again."
    )
)

def run_and_print(question: str):
    print(f"\n{'='*80}")
    print(f"Question: {question}")
    _kb_search_call_count["count"] = 0  # reset before each new question
    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": question}]},
            config={"recursion_limit": 10}
        )
        for msg in result["messages"]:
            print(f"[{msg.type}] {msg.content}")
    except Exception as e:
        print(f"Agent hit an error or limit: {e}")
        return

if __name__ == "__main__":
    run_and_print("What is 15% of 200?")
    run_and_print("How do I control who can access my S3 bucket?")