import os
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, END
from groq import Groq
from day15_rag import retrieve

load_dotenv()
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

MAX_REVISIONS = 2


class ReviewState(TypedDict):
    question: str
    context: str
    draft: str
    critique: str
    judge_decision: str
    judge_rationale: str
    revision_count: int
    final_answer: str


def propose_node(state: ReviewState) -> dict:
    feedback_note = f"\n\nPrevious critique to address: {state['critique']}" if state.get("critique") else ""
    prompt = f"""Answer the question using ONLY the context below.
Context:
{state['context']}

Question: {state['question']}{feedback_note}
"""
    response = groq.chat.completions.create(
        model="openai/gpt-oss-20b", temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    draft = response.choices[0].message.content
    print(f"\n--- DRAFT ---\n{draft}\n")
    return {"draft": draft}


def critic_node(state: ReviewState) -> dict:
    prompt = f"""You are a strict critic. Your ONLY job is to find problems - do not fix anything, do not decide anything.
Context:
{state['context']}

Draft answer:
{state['draft']}

List any claims in the draft that are NOT directly supported by the context.
If everything is fully supported, say exactly: "No issues found."
"""
    response = groq.chat.completions.create(
        model="openai/gpt-oss-20b", temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    critique = response.choices[0].message.content
    print(f"\n--- CRITIC OUTPUT ---\n{critique}\n")
    return {"critique": critique}


def judge_node(state: ReviewState) -> dict:
    prompt = f"""You are a judge. Based on the critic's findings, decide: ACCEPT, REVISE, or REJECT.
Critique:
{state['critique']}

Respond in exactly this format:
DECISION: <ACCEPT|REVISE|REJECT>
RATIONALE: <one sentence explaining why>
"""
    response = groq.chat.completions.create(
        model="openai/gpt-oss-20b", temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content
    decision = "REJECT"
    rationale = text
    for line in text.splitlines():
        if line.startswith("DECISION:"):
            decision = line.replace("DECISION:", "").strip()
        if line.startswith("RATIONALE:"):
            rationale = line.replace("RATIONALE:", "").strip()
    return {"judge_decision": decision, "judge_rationale": rationale}


def route_after_judge(state: ReviewState) -> str:
    if state["judge_decision"] == "ACCEPT":
        return "accept"
    elif state["judge_decision"] == "REVISE" and state["revision_count"] < MAX_REVISIONS:
        return "revise"
    else:
        return "reject"


def revise_node(state: ReviewState) -> dict:
    return {"revision_count": state["revision_count"] + 1}


def accept_node(state: ReviewState) -> dict:
    return {"final_answer": state["draft"]}


def reject_node(state: ReviewState) -> dict:
    return {"final_answer": f"I don't have a fully grounded answer for that. (Judge rationale: {state['judge_rationale']})"}


graph = StateGraph(ReviewState)
graph.add_node("propose", propose_node)
graph.add_node("critic", critic_node)
graph.add_node("judge", judge_node)
graph.add_node("revise", revise_node)
graph.add_node("accept", accept_node)
graph.add_node("reject", reject_node)

graph.set_entry_point("propose")
graph.add_edge("propose", "critic")
graph.add_edge("critic", "judge")
graph.add_conditional_edges("judge", route_after_judge, {
    "accept": "accept", "revise": "revise", "reject": "reject"
})
graph.add_edge("revise", "propose")
graph.add_edge("accept", END)
graph.add_edge("reject", END)

workflow = graph.compile()


if __name__ == "__main__":
    question = "How do I control who can access my S3 bucket?"
    chunks, top_score = retrieve(question)
    context = "\n\n".join(c.payload["text"] for c in chunks)

    result = workflow.invoke({
        "question": question, "context": context,
        "revision_count": 0, "critique": ""
    })

    print(f"\nJudge decision: {result['judge_decision']}")
    print(f"Judge rationale: {result['judge_rationale']}")
    print(f"Revisions used: {result['revision_count']}")
    print(f"\nFinal answer: {result['final_answer']}")