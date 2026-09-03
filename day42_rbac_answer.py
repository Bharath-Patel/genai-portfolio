import os
from dotenv import load_dotenv
from groq import Groq
from day42_rbac_retrieve import retrieve_with_rbac

load_dotenv()
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

SIMILARITY_THRESHOLD = 0.3  # same threshold as Month 1's Day 17 guardrail


def answer_with_rbac(question: str, user_role: str):
    retrieved_chunks = retrieve_with_rbac(question, user_role=user_role, top_k=3)

    if not retrieved_chunks:
        return "No accessible documents matched this query.", []

    top_score = retrieved_chunks[0].score

    # SAME guardrail logic as Month 1 - the exact protection we're testing
    if top_score < SIMILARITY_THRESHOLD:
        return "I don't have information about that in my documents.", retrieved_chunks

    context = "\n\n".join(f"[Source: {r.payload['source']}]\n{r.payload['text']}" for r in retrieved_chunks)
    prompt = f"""Answer the question using ONLY the context below.
If the answer isn't in the context, say "I don't have information about that in my documents."

Context:
{context}

Question: {question}
"""

    response = groq.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a helpful assistant answering questions based strictly on provided context."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content, retrieved_chunks


if __name__ == "__main__":
    question = "What did I learn about async programming?"

    print("=== As 'engineer' ===")
    answer, sources = answer_with_rbac(question, user_role="engineer")
    print(f"Answer: {answer}")
    print(f"Top score was: {sources[0].score:.3f}" if sources else "No sources")

    print("\n=== As 'admin' ===")
    answer, sources = answer_with_rbac(question, user_role="admin")
    print(f"Answer: {answer}")
    print(f"Top score was: {sources[0].score:.3f}" if sources else "No sources")