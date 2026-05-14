from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fuzzy_system import evaluate_employee
import uvicorn
import os
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmployeeInput(BaseModel):
    attendance: float
    productivity: float
    cooperation: float
    suggestions: float
    evaluation_mode: str = "corporate_v2"
    profile: str = "general"
    proactivity: Optional[float] = None

@app.post("/evaluate")
def evaluate(data: EmployeeInput):
    score, label, explanation = evaluate_employee(
        data.attendance,
        data.productivity,
        data.cooperation,
        data.suggestions,
        explain=True,
        evaluation_mode=data.evaluation_mode,
        profile=data.profile,
        proactivity_val=data.proactivity
    )
    return {"score": score, "label": label, "explanation": explanation}

@app.get("/")
def serve_index():
    return FileResponse("index.html")


if __name__ == "__main__":
    port = int(os.getenv("API_PORT", "8001"))
    uvicorn.run(app, host="127.0.0.1", port=port)
