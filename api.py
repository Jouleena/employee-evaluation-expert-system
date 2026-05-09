from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fuzzy_system import evaluate_employee
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class EmployeeData(BaseModel):
    attendance: float
    productivity: float
    cooperation: float
    suggestions: float

@app.post("/evaluate")
def evaluate(employee: EmployeeData):
    score, label = evaluate_employee(
        employee.attendance,
        employee.productivity,
        employee.cooperation,
        employee.suggestions
    )
    return { "score": score, "label": label}
