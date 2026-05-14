# Quick Start Guide — Running the System with All 5 Features

## Prerequisites
- Python 3.12+ with pip
- Chrome, Firefox, Safari, or Edge browser
- The following packages (install via `pip install -r requirements.txt`):
  - fastapi
  - uvicorn
  - numpy
  - scikit-fuzzy
  - pydantic

## Step 1: Install Dependencies
```bash
cd "c:\Users\loujain\Desktop\Expert System Project"
pip install -r requirements.txt
```

## Step 2: Start the API Server
```bash
python api.py
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## Step 3: Open the Web Interface
Open your browser and navigate to: **http://localhost:8000**

You should see the PerfEval system with:
- Profile selector dropdown (General/Technical/Leadership)
- Mode toggle (Baseline/Corporate V2)
- CSV export button
- Employee table

## Step 4: Test the Features

### Test 1: General Profile Evaluation
1. Keep profile as "General"
2. Click "Add Employee"
3. Fill in a row:
   - Attendance: 95
   - Productivity: 92
   - Cooperation: 9
   - Suggestions: 8
4. Click "Evaluate"
5. Observe:
   - ✅ Main explanation card shows fuzzy reasoning
   - ✅ Comparison card appears showing Baseline vs Corporate V2
   - ✅ Rule strength chart visualizes top 10 firing rules

### Test 2: Leadership Profile with Proactivity
1. Change profile to "Leadership"
2. Notice: Proactivity column appears in table
3. Click "Add Employee"
4. Fill in a row (example weak leader):
   - Attendance: 88
   - Productivity: 90
   - Cooperation: 2
   - Suggestions: 1
   - Proactivity: 8 (high proactivity compensates)
5. Click "Evaluate"
6. Compare results with same employee in General profile
7. Notice: Proactivity boost may improve Excellent likelihood

### Test 3: Mode Switching & Validation Panel
1. Evaluate an employee in Corporate V2 mode
2. Click "Mode: Corporate V2" button to switch to Baseline
3. The comparison card updates showing:
   - Baseline score (higher, no guardrails)
   - Corporate V2 score (may be lower due to policy)
   - Explanation of which guardrails fired

### Test 4: CSV Export
1. Add 3-4 employees and evaluate them
2. Click "CSV" button
3. A file like `employee_eval_2025-05-14.csv` downloads
4. Open in Excel or view raw (should see columns: ID, Attendance, Productivity, Cooperation, Suggestions, Score, Label, Mode)

### Test 5: Chart Visualization
1. Evaluate any employee
2. Look at comparison card
3. Below the baseline/corporate results, observe bar chart
4. Chart shows top 10 rules that fired with their strength (0–1 scale)

## Manual Testing Checklist

- [ ] General profile evaluation works
- [ ] Leadership profile shows proactivity input
- [ ] Switching mode updates comparison card
- [ ] CSV export downloads with correct data
- [ ] Chart renders for rule strengths
- [ ] Proactivity input is optional (doesn't break on 0 or missing)
- [ ] Multiple employees can be evaluated sequentially
- [ ] Delete button removes employees correctly
- [ ] Stats update after each evaluation

## Interpreting Results

### Score Ranges
- **Excellent**: 75–100 (blue badge)
- **Good**: 55–74 (purple badge)
- **Acceptable**: 35–54 (orange badge)
- **Weak**: 0–34 (red badge)

### Guardrail Explanations
If switching from Baseline to Corporate V2 lowers the score, check for:
1. **Weak cooperation/few suggestions**: Caps Excellent ceiling
2. **Low attendance**: Prevents Excellent outcomes
3. **Low attendance + low productivity**: Boosts Weak rating

### Leadership Profile Boost
- Proactivity ≥ 7 (high): May elevate to Excellent even with lower core metrics
- Proactivity 4–6 (medium): Neutral effect
- Proactivity < 4 (low): May further reduce Excellent likelihood

## Troubleshooting

### Issue: "Could not reach API" error
**Solution**: Ensure `api.py` is running. Check terminal for:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Issue: Profile selector doesn't change
**Solution**: Clear browser cache (Ctrl+Shift+Delete) and reload

### Issue: Proactivity column doesn't appear in Leadership
**Solution**: Wait a moment for JavaScript to execute after profile change, or refresh page

### Issue: CSV export is empty or malformed
**Solution**: Evaluate at least one employee before exporting

### Issue: Chart doesn't render
**Solution**: Ensure Chart.js CDN is accessible (check browser console for 403 errors); try reloading page

## Advanced Testing: CLI Interface

For backend-only testing without the UI:

```bash
python main.py
```

This prompts for interactive employee input and displays results with explanations in the terminal. Supports both baseline and corporate modes (hardcoded to corporate_v2 in main.py; edit to switch).

## Running Tests

Verify all fuzzy logic is working:

```bash
python test_cases.py
```

Expected output:
```
======================================================================
   Employee Performance Expert System — Test Cases
======================================================================

TC01 — Lujain Alashfa
  Description  : Ideal employee — all metrics high
  [Output showing Score, Label, Expected, Status: PASS]

...

======================================================================
  Total: 8 tests  |  Passed: 8  |  Failed: 0
======================================================================
```

All 8 test cases should **PASS** with both profiles (baseline and corporate_v2).

## Code Structure for Feature Access

Want to integrate features into your own code?

### Use Case 1: Evaluate employee with leadership profile
```python
from fuzzy_system import evaluate_employee

score, label, explanation = evaluate_employee(
    attendance_val=88,
    productivity_val=90,
    cooperation_val=2,
    suggestions_val=1,
    proactivity_val=8,  # Leadership-specific
    profile="leadership",
    evaluation_mode="corporate_v2",
    explain=True
)
print(f"Score: {score}, Label: {label}")
print(f"Policy adjustments: {explanation['policy_adjustments']}")
```

### Use Case 2: Access policy adjustments
```python
adjustments = explanation.get('policy_adjustments', [])
for adj in adjustments:
    print(f"  {adj['type']}: {adj['reason']}")
```

### Use Case 3: Compare modes in your code
```python
baseline_score, baseline_label, baseline_exp = evaluate_employee(..., evaluation_mode="baseline", explain=True)
corporate_score, corporate_label, corporate_exp = evaluate_employee(..., evaluation_mode="corporate_v2", explain=True)

score_diff = baseline_score - corporate_score
print(f"Corporate guardrails reduced score by {score_diff} points")
```

## Performance Notes

- **API response time**: ~5–10ms per evaluation
- **Chart rendering**: ~50–100ms for 10+ rules
- **CSV generation**: ~1–5ms for 100+ records
- **Profile switching**: Instant (no server call)

## Next Steps After Testing

1. **For Submission**: Include FEATURES_IMPLEMENTED.md in your project deliverables
2. **For Enhancement**: Add more profiles (Sales, Operations) with different rule weights
3. **For Analysis**: Export CSV, analyze trends in Google Sheets or Python
4. **For Deployment**: Run `uvicorn api:app --host 0.0.0.0 --port 8000` to expose to network

---

## Questions or Issues?

Refer to:
- **Technical Details**: FEATURES_IMPLEMENTED.md
- **Code Comments**: See fuzzy_system.py, api.py, index.html
- **Test Cases**: test_cases.py (8 predefined employee profiles)
