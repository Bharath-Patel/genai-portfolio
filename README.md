# GenAI Portfolio — Week 1: Foundations

Personal learning project documenting my transition from DevOps Engineer to GenAI/AI Engineer.

## What's in this repo so far (Week 1)

- `day1_compare.py` — compares responses from a cloud LLM (Groq API) vs a 
  local LLM (Ollama running on-device)
- `day2_async.py` — demonstrates concurrent API calls using Python's asyncio, 
  with measured proof that concurrent calls are faster than sequential ones
- `day3_api.py` / `day4_api.py` — a FastAPI web service exposing an LLM 
  through a `/chat` endpoint, with configurable system prompts and temperature
- `day5_stream.py` — streams LLM responses token-by-token instead of waiting 
  for the full response
- `Dockerfile` — containerizes the FastAPI app for portable deployment

## How to run this

1. Clone the repo
2. Create a `.env` file with `GROQ_API_KEY=your_key_here`
3. `python3 -m venv venv && source venv/bin/activate`
4. `pip install --no-cache-dir -r requirements.txt`
5. `uvicorn day5_stream:app --reload`
6. Test: `curl -N "localhost:8000/chat-stream?question=hello"`

Or with Docker:
1. `docker build -t genai-app .`
2. `docker run -p 8000:8000 --env-file .env genai-app`

## What I learned this week

- The difference between local inference (Ollama, runs on your own hardware) 
  and API-based inference (Groq, hosted elsewhere) — and why both matter 
  for different use cases (privacy, cost, latency)
- Why streaming matters for perceived responsiveness, even when total 
  generation time is unchanged
- Why `0.0.0.0` vs `127.0.0.1` matters once an app is containerized

## Week 2: Embeddings & Vector Search

- `day8_embeddings.py` — generates embeddings using `sentence-transformers` 
  (all-MiniLM-L6-v2, 384 dimensions), demonstrates semantic similarity 
  between sentences using cosine similarity
- `day9_qdrant.py` — sets up Qdrant (running in Docker), stores embeddings 
  as points with payloads, performs first semantic search
- `day11_chunking.py` — splits real documents into chunks using 
  RecursiveCharacterTextSplitter (chunk_size=500, overlap=50)
- `day12_embed_store.py` — full pipeline: reads all documents from `data/`, 
  chunks them, embeds each chunk, stores in Qdrant with source tracking, 
  with persistence via a Docker volume and a guard against redundant re-embedding
- `day14_retrieval_test.py` — tests retrieval across all 4 source documents 
  with varied questions to verify cross-document accuracy

### What I learned this week

- Embeddings convert text into fixed-size vectors that capture semantic 
  meaning, not just keywords — verified this with real similarity scores 
  before trusting the concept
- Qdrant stores vectors + payloads and performs fast similarity search; 
  collections require a fixed vector dimension and distance metric set 
  upfront
- Chunking is a real tradeoff: too small loses context, too large produces 
  blurry embeddings that blend multiple topics together
- High similarity score means "topically related," not "contains the 
  specific answer" — an important distinction discovered while debugging 
  retrieval on a tricky test case (see Week 3)

  ## Week 3: Full RAG Pipeline - Retrieval + Generation + Guardrails

- `day15_rag.py` — the core RAG pipeline: retrieves relevant chunks from 
  Qdrant, reranks them with a cross-encoder, and generates a grounded 
  answer using Groq (temperature=0 for deterministic output)
- `day16_stress_test.py` — stress-tested the pipeline with 10 varied 
  questions (in-scope, out-of-scope, cross-document, casually-phrased) 
  and logged results to `day16_test_log.json`
- `day18_rerank.py` — added a cross-encoder reranking stage 
  (ms-marco-MiniLM-L-6-v2): Qdrant retrieves a wide candidate set (top 10), 
  the cross-encoder re-scores each candidate against the question directly, 
  and only the top 3 are used for generation
- `day19_rag_api.py` — wraps the full pipeline in a FastAPI `/ask` endpoint, 
  returning the answer plus source documents and scores for traceability

### Evaluation & guardrail approach

This system uses two independent layers to prevent hallucination:

1. **Deterministic threshold guardrail** — before calling the LLM at all, 
   the top Qdrant similarity score is checked against a threshold (0.3, 
   chosen from real evidence: clearly irrelevant questions scored 
   0.04-0.24, clearly relevant ones scored 0.5-0.8). Below threshold, the 
   system refuses immediately without incurring an LLM call.

2. **LLM grounding judgment** — the system prompt instructs the model to 
   answer using ONLY the retrieved context, and to say "I don't know" if 
   the answer isn't present. This catches a subtler failure mode: chunks 
   that are topically related but don't actually contain the answer (e.g. 
   a question about Lambda timeouts retrieved genuinely Lambda-related 
   content that never mentioned timeouts — Qdrant scored it 0.61 
   similarity, but the LLM correctly refused since the specific fact 
   wasn't present).

Both layers were verified independently with real test cases, not assumed 
to work. One important lesson from debugging: an LLM call without 
`temperature=0` is non-deterministic — the same prompt and same retrieved 
context produced different answers (sometimes correctly grounded, 
sometimes mildly speculative) across repeated runs, until temperature 
was fixed at 0.

### What I learned this week

- RAG's core mechanism is simple: retrieved text gets inserted directly 
  into the prompt before the question is asked — the value is in what 
  gets retrieved and how the model is instructed to use it
- Similarity score and "actually answers the question" are different 
  things — proven directly by a case where high-scoring retrieved content 
  didn't contain the specific fact asked about
- Two-stage retrieval (fast approximate search, then precise reranking on 
  a shortlist) is standard because a reranker is too slow to run against 
  an entire document set but sharply improves precision on a narrowed 
  candidate list
- Reranker scores and embedding similarity scores are on different scales 
  and shouldn't be used interchangeably for hard thresholds without 
  separate calibration — learned this after a reranker-based threshold 
  caused correct answers to be incorrectly blocked
- Non-determinism in LLM calls (missing `temperature=0`) can look exactly 
  like a retrieval or logic bug — worth ruling out early when debugging 
  inconsistent behavior

  ### Reflection: How do I know this system works correctly?

When a question is asked, it's embedded and compared against stored chunk 
embeddings in Qdrant, which returns a wide set of topically similar 
candidates. Each candidate is then paired with the question and re-scored 
by a cross-encoder reranker, which reads both together rather than 
comparing pre-computed vectors — the top 3 reranked results become the 
final candidates.

Two independent guardrails prevent hallucination. First, a deterministic 
threshold checks Qdrant's top similarity score before the LLM is ever 
called — if nothing retrieved is similar enough, the system refuses 
immediately, with no LLM cost incurred. Second, even when retrieval 
passes that threshold, the LLM is instructed to answer using ONLY the 
retrieved context, not its own training knowledge, and to say it doesn't 
know if the context doesn't contain the answer — this catches cases where 
retrieval finds topically related content that doesn't actually contain 
the specific fact asked. I verified this distinction directly: a question 
about Lambda timeouts retrieved genuinely Lambda-related content at 0.61 
similarity, but since none of it mentioned timeouts specifically, the LLM 
correctly refused rather than fabricating an answer.