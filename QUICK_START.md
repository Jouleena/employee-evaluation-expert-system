# Quick Start

This short guide shows how to install dependencies, run the API or CLI, and execute the test harness.

Prerequisites
- Python 3.10+ and `pip`
- A modern browser (Chrome, Firefox, Edge, Safari)

1) Install dependencies
```bash
cd "c:\Users\loujain\Desktop\Expert System Project"
pip install -r requirements.txt
```

2) Start the API (recommended)
Run the API with Uvicorn:
```bash
uvicorn api:app --reload
```
The service listens by default on http://127.0.0.1:8000.

3) Open the frontend
Open http://localhost:8000 in your browser to use the web UI.

4) Run the CLI (alternative)
```bash
python main.py
```
The CLI prompts for metrics and can print the explanation when requested.

5) Run tests
```bash
python test_cases.py
```
`run_tests()` prints per-case results and a final pass/fail summary.

Troubleshooting
- "Could not reach API": ensure Uvicorn is running and listening on the expected port.
- Port already in use: stop other services using port 8000 or run Uvicorn on a different port (`--port 8080`).

Notes
- The core fuzzy engine lives in `fuzzy_system.py` and is shared by the CLI, API, and frontend.
- If expected test results differ (e.g., legacy cases), review `test_cases.py` and the rule base for alignment.

No emojis are used in this guide.





