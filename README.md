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

## Week 4: Deployment, Documentation, Resume Prep

- Migrated the vector database from local Docker Qdrant to Qdrant Cloud 
  (free tier), making retrieval reachable from any hosting platform instead 
  of only localhost
- Updated `day12_embed_store.py` and `day15_rag.py` to connect via 
  `QDRANT_URL` and `QDRANT_API_KEY` instead of a local connection string
- Ran a full secrets audit (`git log --all --full-history -- .env`) to 
  confirm no API keys were ever committed to version control
- Built `app.py` — a Gradio interface wrapping the existing `answer_question()` 
  pipeline, giving the project a browser-based demo in addition to the 
  FastAPI JSON endpoint
- Deployed to Hugging Face Spaces (Gradio SDK, free ZeroGPU tier)
- Attempted a second deployment on Render (Docker-based, serving 
  `day19_rag_api.py` directly):
  - Diagnosed and hit a genuine free-tier resource limit: loading both the 
    embedding model and cross-encoder reranker exceeded Render's 512MB RAM 
    cap. Rather than force a fix on a hard infrastructure constraint, 
    prioritized the working HF Spaces deployment and documented the 
    tradeoff honestly instead

### What I learned this week

- Free-tier hosting platforms have real, differing constraints (GPU/package 
  version requirements, RAM limits, import-order rules) that don't show up 
  until you actually attempt deployment — this is a normal, expected part 
  of shipping software, not a sign something is wrong with the underlying 
  code
- Knowing when to stop optimizing around a hard constraint (Render's 
  memory limit) and use what's already working (HF Spaces) is itself a 
  real engineering decision, not a failure to solve the problem

  ## Month 1 Retro

**What worked well:**
Building project-first rather than tutorial-first meant every concept was 
learned in the context of a real problem. The most valuable learning moments 
came from debugging actual failures in my own system (e.g., diagnosing why 
a Lambda timeout question was retrieving topically-related but factually 
absent content) rather than following pre-built examples.

**What was harder than expected:**
Deployment and infrastructure friction (dependency conflicts on ZeroGPU, 
memory limits on Render's free tier, secrets management) consumed a disproportionate amount of Week 4 relative to the core 
RAG logic built in Weeks 1-3. This wasn't wasted time — it's real, 
transferable DevOps-adjacent skill-building — but it means deployment work 
should be budgeted more generously going forward.

**A pattern worth watching:**
Some debugging sessions (a non-deterministic LLM bug traced to a missing 
`temperature=0`, a reranker-based threshold causing false-refusal 
regressions) required multiple rounds of hypothesis-testing before finding 
root cause. Valuable experience, but a signal to build small, deterministic 
tests earlier when adding new pipeline stages, rather than only 
stress-testing after full integration.

**Going into Month 2:**
Agents introduce multi-step decision loops, a meaningfully different 
complexity class from a single retrieve-then-generate pass. Plan is to 
test each new capability (tool use, memory, multi-step chains) in 
isolation before combining them, rather than building the full agent 
end-to-end and debugging everything at once.

## Week 5-6: Agents, Multi-Step Workflows, Self-Correction

- `day29_first_agent.py` — first LangGraph/LangChain agent using a single 
  tool (calculator), built with `create_agent` (migrated from the 
  deprecated `create_react_agent`). Learned the plan-act-observe-repeat 
  loop that underlies all agent frameworks.
- `day30_multi_tool_agent.py` — multi-tool agent combining a calculator 
  with the Month 1 RAG pipeline wrapped as a tool, proving retrieval logic 
  built in Month 1 could be composed into a new system without rebuilding it.
- `day31_memory.py` — multi-turn conversation memory by accumulating and 
  re-passing the full message history on each turn, with retry logic for 
  a documented Groq tool-calling reliability issue.
- `day32_workflow.py` — first explicit `StateGraph` workflow (research → 
  draft), demonstrating fixed multi-step sequences vs. an agent's free 
  tool selection.
- `day33_self_correction.py` — added a conditional edge (research → draft 
  → check → retry-or-end), where an LLM evaluates its own prior output and 
  the graph branches based on that judgment, capped at 3 revisions to 
  prevent infinite loops.
- `day34_workflow_stress_test.py` — stress-tested the self-correction 
  workflow across topics with and without matching source documents.

### Real issues found and fixed this week

1. **Tokenizer deadlock on concurrent tool calls** — when an agent issued 
   two near-simultaneous tool calls, both independently initializing 
   Hugging Face's tokenizer library caused a genuine hang, not just 
   slowness. Fixed by setting `TOKENIZERS_PARALLELISM=false`.

2. **Redundant tool-calling loop** — `llama-3.1-8b-instant` would 
   sometimes call the same tool multiple times with slightly reworded 
   queries even after getting a valid answer, despite explicit prompt 
   instructions not to. Prompt-only fixes were insufficient; resolved 
   with a hard, code-level call counter as a deterministic backstop — the 
   same "don't fully trust model judgment alone" principle from the 
   Month 1 RAG guardrails, now applied to tool-calling behavior.

3. **Groq tool-calling reliability (`tool_use_failed`)** — intermittent, 
   documented Groq API errors where the model produced malformed 
   function-call syntax instead of a proper structured tool call 
   (confirmed as a known issue via multiple independent GitHub reports 
   from other projects). Mitigated with retry logic; also found that 
   retrying at `temperature=0` is pointless for this specific failure mode, 
   since a deterministic model will reproduce the same malformed output 
   every time — retries only help when some variation is possible.

4. **State corruption on failed turns** — a failed `agent.invoke()` call 
   was still permanently appending the user's question to conversation 
   history before the failure occurred, corrupting the next turn's context 
   even though no real answer was ever given. Fixed by only committing to 
   the shared history after a confirmed successful response.

5. **Model deprecation mid-project** — Groq deprecated both 
   `llama-3.1-8b-instant` and `llama-3.3-70b-versatile` during this 
   project, breaking every file referencing them with a `model_not_found` 
   error. Migrated to `openai/gpt-oss-20b` and `openai/gpt-oss-120b` 
   respectively — a real example of a dependency changing outside my 
   control mid-build, not a code bug.

6. **Downstream blind spot from an upstream guardrail bypass** — a 
   shortcut in `check_node` (skip evaluation when research found nothing, 
   to avoid wasting retries) had an unintended side effect: `draft_node` 
   still attempted to generate a post from empty research, producing 
   literal unfilled placeholder text (`[insert tech topic]`), which then 
   sailed through the bypassed check as "PASS" without ever being read. 
   Fixed at the actual source (`draft_node` now returns an honest refusal 
   when research fails) rather than patching the symptom in the check.

### What I learned this week

- Composing Month 1's RAG pipeline as a tool inside an agent worked with 
  no changes to the underlying code — a real payoff of building modular, 
  independently-tested components rather than one monolithic script
- LLM-as-judge (using a model to evaluate another model's output) is a 
  real, useful pattern but inherits the same reliability weaknesses as any 
  other LLM call — it is not inherently more trustworthy just because its 
  job is to check something
- Bugs in multi-stage pipelines often hide at the boundary between stages 
  — a fix or shortcut in one node can create a blind spot in a completely 
  different node, which is why stress-testing the full pipeline end-to-end 
  matters more than testing each node in isolation
- Model providers can deprecate models with limited notice; hardcoding a 
  specific model string throughout a codebase is a real maintenance 
  liability worth being aware of, even in a personal project

  ## Week 7-8: Formal Evaluation, Drift Detection, Guardrails, and CI/CD

- `day36_ragas_eval.py` — first formal Ragas evaluation of the Month 1 RAG 
  pipeline (faithfulness, context precision), establishing a numeric 
  baseline (faithfulness ~0.79-0.90, context precision ~0.94-1.0) instead 
  of relying on manual read-throughs.
- `day37_eval_gate.py` — turned evaluation into an automated pass/fail 
  gate using proper exit codes (0 = pass, 1 = fail), the same mechanism 
  any CI system uses to know whether a step succeeded.
- `day38_drift_detection.py` — baseline-comparison drift detection: saves 
  a reference run and flags future runs that degrade beyond a tolerance, 
  distinct from a fixed threshold check.
- `day39_cost_guardrail.py` — a reusable `CallBudget` class capping total 
  LLM/tool calls per request, added as a general pattern; honestly 
  assessed as currently redundant with the existing per-tool call limit 
  in a single-tool system, but designed for future multi-tool scenarios.
- `.github/workflows/eval-gate.yml` — GitHub Actions workflow running the 
  eval gate automatically on push, with a `paths:` filter limiting runs 
  to changes that actually affect the pipeline.

### Real issues found and fixed this week

1. **A loop-indentation bug that ran evaluation once per partial batch 
   instead of once on the complete dataset** — evaluation and dataset 
   construction were nested inside the data-collection loop instead of 
   after it, causing a crash on the very first (incomplete) iteration. 
   Same category of bug as Day 12's `continue` logic inversion — 
   structural placement, not faulty logic.

3. **A NaN silently passing a quality gate** — when `context_precision` 
   failed to compute (returned NaN due to timeouts), the threshold check 
   `avg_context_precision < THRESHOLD` evaluated to `False`, since any 
   comparison involving NaN in Python returns False. The gate reported 
   "PASSED" on a metric that had completely failed to compute. Fixed with 
   an explicit `math.isnan()` check. This is a genuinely dangerous class 
   of bug for any automated quality gate — a missing result silently 
   looking identical to a good result.

5. **Grep missing a package due to hyphen/underscore mismatch** — 
   searched for `langgraph-agents` (hyphen) while the actual line in 
   `requirements.txt` used `langgraph_agents` (underscore). Pip treats 
   these as equivalent; plain text search tools do not — a subtle, easy 
   trap when hunting for a package by name in a text file.

6. **Evaluation timeouts from excessive concurrency** — Ragas's default 
   concurrent request count overwhelmed Groq's API/network conditions in 
   CI, causing multiple evaluation calls to time out and produce NaN 
   results. Fixed via `RunConfig(timeout=300, max_workers=2)`, trading 
   evaluation speed for reliability — the same reliability-over-speed 
   tradeoff as Day 31's tool-calling retry logic.

### What I learned this week

- Formal evaluation metrics don't replace manual testing, they formalize 
  and scale it — faithfulness and context precision are numeric versions 
  of exactly the "does this actually match the source" and "was this the 
  right thing to retrieve" questions I was already asking by hand in 
  Month 1
- Installing heavyweight tooling (Ragas) alongside a core application 
  stack (LangChain/LangGraph) in one shared environment is a real, 
  recurring source of dependency conflicts — separating "what the 
  application needs" from "what evaluation tooling needs" into different 
  environments or CI steps is a legitimate architectural decision, not 
  a workaround
- Concurrency settings that work fine locally can behave very differently 
  in CI due to network conditions, rate limits, or resource constraints — 
  worth treating concurrency/timeout tuning as an environment-specific 
  concern, not a one-time setting

  ## Week 9: Flagship Project - Role-Based Access Control + Audit Logging

Built a "Policy & Compliance Assistant" - composing the entire Month 1-2 
pipeline (retrieval, reranking, guardrails, generation) with two new 
capabilities specifically targeting the enterprise/regulated-industry 
angle identified in the Charlotte market research: access control and 
audit logging.

- `day42_rbac_setup.py` — created a separate Qdrant collection with each 
  chunk tagged by an `allowed_roles` payload field (engineer: 55 chunks, 
  admin-only: 24 chunks), keeping the original Month 1 collection untouched
- `day42_rbac_retrieve.py` — implemented access control using Qdrant's 
  native payload filtering (`FieldCondition` + `MatchAny`), enforced at 
  the query level so restricted documents are never even considered as 
  retrieval candidates, not filtered out after the fact
- `day42_rbac_answer.py` — combined RBAC-filtered retrieval with the 
  existing similarity threshold guardrail and generation
- `day43_audit_log.py` — a persistent SQLite audit log, refined from an 
  initial binary `access_granted` field to a three-state `status` field 
  (`access_denied`, `access_granted_no_answer`, `access_granted_answered`) 
  after finding the binary version misleadingly logged "granted" even 
  when the LLM itself declined to answer
- `day44_rbac_api.py` — exposed the full pipeline via FastAPI: `/ask` for 
  actual use, `/audit/logs` and `/audit/summary` for compliance review
- `day44_summarize.py` — aggregates audit log entries by status using a 
  counting-dictionary pattern

### Key finding: two-layer guardrails matter even more with access control

Testing an engineer-role query about content that only exists in the 
admin-only document revealed a real, important failure mode specific to 
RBAC systems: retrieval is forced to return the "best available" result 
from *permitted* documents, even when nothing permitted is actually 
relevant. In this case, an engineer's async-programming question scored 
0.303 against irrelevant Lambda content - just above the 0.3 hard 
threshold, but the LLM's own honesty check correctly caught that the 
content didn't actually address the question and refused rather than 
fabricating an answer. Without this second layer, an access-controlled 
system could confidently generate wrong answers built on content that 
was only retrieved because it was the least-bad option among what a role 
could see - a subtler and more dangerous failure mode than a normal RAG 
system without access restrictions.

### Real issues found and fixed

1. **Missing `create_payload_index`** - Qdrant requires an explicit index 
   on any payload field before it can be used in a filter, distinct from 
   the vector similarity index (HNSW) used for retrieval itself. 
   Attempting to filter on an unindexed field returns a clear 400 error 
   naming the exact field and required index type.
2. **Binary access-tracking field masking a real event** - the original 
   `access_granted` boolean logged `True` for a case where the LLM 
   declined to answer, making a refusal indistinguishable from a genuine 
   answer in the audit trail. Replaced with a three-state status field 
   before this reached anything resembling production use.

### What I learned this week

- Filtering for access control must happen at the retrieval/query level, 
  not as a post-processing step - filtering after the fact both risks 
  momentarily exposing restricted content and can crowd out legitimate 
  results that would have ranked lower only because higher-ranked 
  restricted content was competing for the same top-K slots
- A field designed for later audit/review needs to capture every 
  distinct outcome a reviewer would actually care about distinguishing - 
  a boolean is often not expressive enough once you think through what 
  questions the log needs to answer