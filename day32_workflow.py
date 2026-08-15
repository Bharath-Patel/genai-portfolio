import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from typing import TypedDict
from day15_rag import answer_question

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY")
)

# Step A: define the shared State - what data flows through every step
class WorkflowState(TypedDict): #attributes of class WorkflowState , are dictionaries which accpets only string as TypedDict is inherited here. 
    topic: str
    research_findings: str
    final_post: str

# Step B: define each node as a plain function - takes state, returns updates
def research_node(state: WorkflowState) -> dict: #node(function) must accept the current state as it's input parameter and must return a dictionary that it wants to update or add to the state.
    print(">>> Running research_node")
    answer, sources = answer_question(state["topic"])
    print(f">>> Research findings: {answer}")
    return {"research_findings": answer}

def draft_node(state: WorkflowState) -> dict:
    print(">>> Running draft_node")
    prompt = f"""Based on this research, write a short, engaging LinkedIn post (3-4 sentences, casual professional tone):

Research: {state['research_findings']}
"""
    response = llm.invoke(prompt)
    return {"final_post": response.content}

# Step C: wire the graph together
graph = StateGraph(WorkflowState) #Instantiates our graph controller,By passing the WorkflowState to StateGraph(creates graph) class, we are metioning the dictionary structure that graph will manage and pass btwn nodes. As LangGraph uses graph-based architecture.
graph.add_node("research", research_node) #registers our functions into graph's internal dictionary of workers
graph.add_node("draft", draft_node)

graph.set_entry_point("research") #tells the graph where to being execution
graph.add_edge("research", "draft") #tells graph the flow, direction after research node is done.
graph.add_edge("draft", END)

workflow = graph.compile() #this validates the graph for broken links or mission pieces and bakes it into an executable application.

# Step D: run it
if __name__ == "__main__":
    result = workflow.invoke({"topic": "How do I control who can access my S3 bucket?"}) #we invoke the compiled graph by passing starting state.
    print("\n=== Final Post ===")
    print(result["final_post"])