from fastapi import FastAPI
from pydantic import BaseModel
from langchain_ollama import OllamaLLM
import pandas as pd
import os

app = FastAPI()

# ----------------------------
# Ollama Configuration
# ----------------------------
ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

llm = OllamaLLM(
    model="mistral",
    base_url=ollama_url,
    options={"num_gpu": 0}
)

# ----------------------------
# Load Dataset
# ----------------------------
df = pd.read_csv("data/Heart_Disease_Prediction.csv")

# ----------------------------
# Request Model
# ----------------------------
class QueryRequest(BaseModel):
    question: str

# ----------------------------
# Health Endpoint
# ----------------------------
@app.get("/health")
def health():
    return {"status": "healthy"}

# ----------------------------
# Ask Endpoint
# ----------------------------
@app.post("/ask")
def ask_question(request: QueryRequest):
    query = request.question

    code_prompt = f"""
You are a professional data analyst.

The dataset is loaded as a pandas DataFrame named df.

Columns:
{list(df.columns)}

User question:
{query}

Return ONLY a single line of valid pandas code using df.
Do NOT include explanations.
Do NOT include comments.
Do NOT include markdown.
Return only executable Python code.
"""

    raw_output = llm.invoke(code_prompt)

    # ----------------------------
    # Clean Model Output
    # ----------------------------
    lines = raw_output.strip().split("\n")
    lines = [line.strip() for line in lines if line.strip()]

    if not lines:
        return {"error": "Model did not return valid code."}

    generated_code = lines[-1]  # Take last non-empty line

    # ----------------------------
    # Basic Security Filter
    # ----------------------------
    blocked_keywords = [
        "import", "os", "sys", "open", "exec",
        "eval", "__", "subprocess", "shutil"
    ]

    for keyword in blocked_keywords:
        if keyword in generated_code.lower():
            return {
                "generated_code": generated_code,
                "error": "Unsafe code detected."
            }

    try:
        # Execute in restricted environment
        result = eval(
            generated_code,
            {"__builtins__": {}},
            {"df": df}
        )

        explanation_prompt = f"""
User question: {query}

Computed result:
{result}

Explain this result clearly and professionally.
"""

        explanation = llm.invoke(explanation_prompt)

        return {
            "generated_code": generated_code,
            "result": str(result),
            "explanation": explanation
        }

    except Exception as e:
        return {
            "generated_code": generated_code,
            "error": str(e)
        }
