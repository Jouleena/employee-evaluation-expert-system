from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fuzzy_system import evaluate_employee

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

@app.post("/evaluate")
def evaluate(data: EmployeeInput):
    score, label, explanation = evaluate_employee(
        data.attendance,
        data.productivity,
        data.cooperation,
        data.suggestions,
        explain=True
    )
    return {"score": score, "label": label, "explanation": explanation}

@app.get("/")
def serve_index():
    return FileResponse("index.html")
