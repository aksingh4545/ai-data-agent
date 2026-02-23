# AI Data Agent

A FastAPI service that answers natural-language questions about a heart disease dataset by:
1. Asking an LLM (Ollama + Mistral) to generate pandas code.
2. Running the generated code against a preloaded DataFrame (`df`).
3. Returning the computed result plus a natural-language explanation.

## Features

- `GET /health` health-check endpoint.
- `POST /ask` endpoint for dataset Q&A.
- Dataset loaded at startup from `data/Heart_Disease_Prediction.csv`.
- Basic safety filter to block clearly unsafe generated code.
- Docker Compose setup with API + Ollama service.

## Project Structure

- `app.py` — FastAPI application and inference logic.
- `data/Heart_Disease_Prediction.csv` — source dataset.
- `requirements.txt` — Python dependencies.
- `Dockerfile` — API image build.
- `docker-compose.yml` — local multi-service orchestration.

## Requirements

- Python 3.11+ (for local run)
- [Ollama](https://ollama.com/) with the `mistral` model available
- Docker + Docker Compose (optional, recommended)

## Run Locally (without Docker)

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start Ollama (if not already running) and ensure `mistral` is pulled:

```bash
ollama pull mistral
ollama serve
```

3. Start the API:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

4. Verify health:

```bash
curl http://localhost:8000/health
```

## Run with Docker Compose

```bash
docker compose up --build
```

Then test:

```bash
curl http://localhost:8000/health
```

> Note: the API expects Ollama to be reachable at `OLLAMA_BASE_URL`. In Compose this is set to `http://ollama:11434`.

## API Usage

### Health Check

```http
GET /health
```

Response:

```json
{"status": "healthy"}
```

### Ask a Question

```http
POST /ask
Content-Type: application/json
```

Request body:

```json
{
  "question": "What is the average age in the dataset?"
}
```

Example curl:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the average age in the dataset?"}'
```

Example response shape:

```json
{
  "generated_code": "df['Age'].mean()",
  "result": "54.4",
  "explanation": "The average age in this dataset is 54.4 years..."
}
```

## Security Notes

The service includes a simple keyword-based filter before evaluating generated code. This is **not** a complete sandbox and should not be treated as production-grade code execution security.

## Environment Variable

- `OLLAMA_BASE_URL` (default: `http://localhost:11434`)
