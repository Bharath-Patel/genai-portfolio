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