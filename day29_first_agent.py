from langchain.agents import create_agent #create_agent is langgraphs prebuilt implementation which has plan->act->observe->repeat loop
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()

@tool #tool decorator wraps a plain function so that LLm can find and call it
def calculator(expression: str) -> str:
    """Evaluates a basic math expression, e.g. '15% of 200' should be passed as '0.15 * 200'.""" #docstring matters — the agent reads it to decide when this tool is relevant, so it's not just documentation, it's actually functional instruction to the model.
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

llm = ChatGroq(
    model = "llama-3.1-8b-instant",
    temperature = 0,
    api_key = os.getenv("GROQ_API_KEY")
)

agent = create_agent(llm, tools=[calculator], system_prompt="You are a helpful assistant.")

if __name__ == "__main__":
    question = "What is 15% of 200?"
    result = agent.invoke({"messages": [{"role" : "user","content": question}]})
    print("Full message history:")
    for msg in result["messages"]:
        print(f"[{msg.type}] {msg.content}")


# What agent.invoke(...) actually triggers
# Input: you're handing agent a starting message list — just your one human question, {"role": "user", "content": "What is 15% of 200?"}
# Plan: the agent (powered by your llm) reads that message and decides: "do I have enough to answer directly, or do I need to call a tool first?" — this decision happens because create_agent wired your llm together with the list of available tools and their docstrings
# Act (if a tool is chosen): if the model decides a tool call is needed, LangGraph actually executes your Python calculator function, with whatever arguments the model decided to pass
# Observe: the tool's return value gets added back into the message history as a [tool] message (exactly what you saw: [tool] 30.0)
# Repeat or finish: the agent looks at this new information and decides again — "do I need another tool call, or can I now answer the user?" In your case, it decided it had enough, and produced the final [ai] message
# Output: agent.invoke(...) returns the entire accumulated message history — not just the final answer, but the full trace of everything that happened along the way, which is exactly what you're looping through and printing