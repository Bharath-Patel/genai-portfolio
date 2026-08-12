import spaces
import gradio as gr
from day15_rag import answer_question

@@spaces.GPU #marking which function actually needs GPU access, using a decorator. Since embedding & reranking models technically could use GPU.
def rag_interface(question):
    answer, sources = answer_question(question)

    if sources:
        source_list = "\n".join(
            f"- {r.payload['source']} (similarity: {r.score:.3f})"
            for r in sources
        )
    else:
        source_list = "No sources retrieved"

    return answer, source_list

demo = gr.Interface( #Gradio's core building block: given a function, input type(s), and output type(s), it auto-generates a full webpage with a textbox, a submit button, and areas to display your two outputs
    fn=rag_interface,
    inputs=gr.Textbox(
        label="Ask a question about AWS S3, Lambda, or Terraform state",
        placeholder="e.g. How do I control who can access my S3 bucket?"
    ),
    outputs=[
        gr.Textbox(label="Answer"),
        gr.Textbox(label="Sources used")
    ],
    title="GenAI DevOps Knowledge Assistant",
    description="A RAG system I built that answers questions grounded in AWS/Terraform documentation and my own learning notes. Uses semantic search (Qdrant) + cross-encoder reranking + guardrails against hallucination."
)

if __name__ == "__main__":
    demo.launch()