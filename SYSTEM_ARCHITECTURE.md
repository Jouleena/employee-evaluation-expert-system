# System Architecture Diagram

## Data Flow Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        WEB BROWSER (UI)                             │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────────┐ │
│  │ Profile      │  │ Evaluation   │  │ CSV Export Button          │ │
│  │ Selector     │  │ Form         │  │ (Client-side Blob API)    │ │
│  └──────────────┘  └──────────────┘  └────────────────────────────┘ │
│         │                  │                       │                 │
│         ├─ changeProfile() │                       │                 │
│         │ (toggle cols)    │                       └─ exportToCSV()  │
│         │                  │                                         │
│         │            runEval() {                                    │
│         │            + runEval()                                    │
│         │            + fetchBaselineComparison()                   │
│         │            + renderComparison()                          │
│         │            + Chart.js render}                            │
│         ▼                  ▼                                         │
│    ┌────────────────────────────────┐                              │
│    │ JavaScript Global State        │                              │
│    │ - currentProfile               │                              │
│    │ - evaluationMode               │                              │
│    │ - results{}                    │                              │
│    │ - lastEvalData                 │                              │
│    └────────────────────────────────┘                              │
│                       │                                              │
└───────────────────────┼──────────────────────────────────────────────┘
                        │
                   HTTP POST
                   {attendance, productivity, cooperation, suggestions,
                    evaluation_mode, profile, proactivity}
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND (api.py)                         │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ POST /evaluate                                                │  │
│  │ Pydantic EmployeeInput validation                            │  │
│  │ │                                                              │  │
│  │ └─► evaluate_employee(                                        │  │
│  │     attendance, productivity, cooperation, suggestions,      │  │
│  │     profile, proactivity, evaluation_mode, explain=True      │  │
│  │     )                                                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                        │                                             │
│                        ▼                                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Return {score, label, explanation}                           │  │
│  │ explanation = {                                               │  │
│  │   inputs: {                                                   │  │
│  │     attendance: {value, memberships, strongest},             │  │
│  │     productivity: {...},                                      │  │
│  │     cooperation: {...},                                       │  │
│  │     suggestions: {...},                                       │  │
│  │     proactivity: {...}  // if leadership                     │  │
│  │   },                                                           │  │
│  │   rule_strengths: [{id, strength, output, ...}, ...],       │  │
│  │   output_strengths: {Excellent, Good, Acceptable, Weak},    │  │
│  │   policy_adjustments: [{type, before, after, reason}, ...], │  │
│  │   evaluation_mode: "baseline|corporate_v2"                   │  │
│  │ }                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                        │
                   HTTP Response
                   JSON with full explanation
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FUZZY LOGIC ENGINE                              │
│                   (fuzzy_system.py)                                 │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ 1. Calculate Membership Functions                              │ │
│  │    • attendance: low, medium, high                             │ │
│  │    • productivity: low, medium, high                           │ │
│  │    • cooperation: weak, acceptable, excellent                 │ │
│  │    • suggestions: few, medium, many                           │ │
│  │    • proactivity: low, medium, high (if leadership)           │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                        ▼                                             │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ 2. Apply Profile-Specific Rules                                │ │
│  │    • General: Use standard 21-rule base                       │ │
│  │    • Technical: Same as general (placeholder)                 │ │
│  │    • Leadership: Standard rules + proactivity boost           │ │
│  │      if proactivity_high: strength_excellent = max(...)      │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                        ▼                                             │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ 3. Aggregate Rule Outputs                                      │ │
│  │    strength_excellent  = max(r1, r2, r4, r10, r16, r18, ...) │ │
│  │    strength_good       = max(r3, r5, r11, r12, r15, ...)     │ │
│  │    strength_acceptable = max(r6, r7, r8, r13, r14, ...)      │ │
│  │    strength_weak       = max(r9, r21)                         │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                        ▼                                             │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ 4. Apply Policy Guardrails (if corporate_v2 mode)            │ │
│  │    if evaluation_mode == "corporate_v2":                       │ │
│  │      • Guardrail 1: Weak cooperation/suggestions cap Excellent│ │
│  │      • Guardrail 2: Low attendance caps Excellent             │ │
│  │      • Guardrail 3: Low att + low prod boost Weak             │ │
│  │      Track all adjustments for explanation                    │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                        ▼                                             │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ 5. Defuzzify to Crisp Score                                   │ │
│  │    Aggregate output memberships using max operator            │ │
│  │    Calculate centroid of aggregated membership                │ │
│  │    Result: score (0–100)                                      │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                        ▼                                             │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ 6. Generate Explanation Object                                 │ │
│  │    Capture all memberships, rule strengths, adjustments       │ │
│  │    Return: (score, label, explanation)                        │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   UI RENDERING (index.html)                         │
│                                                                       │
│  renderExplanation(data):                                            │
│  ├─ Display input memberships (bars)                               │
│  ├─ Show strongest membership for each input                       │
│  ├─ List top 6 firing rules                                        │
│  ├─ Show output strengths (Excellent, Good, Acceptable, Weak)    │
│  └─ Add profile chip to summary                                    │
│                                                                       │
│  renderComparison(baseline, corporate):                             │
│  ├─ Baseline results box                                           │
│  ├─ Corporate results box + policy adjustments                     │
│  └─ Chart.js bar chart (top 10 rules)                             │
│                                                                       │
│  Result Display:                                                    │
│  ├─ Score in table row (filled badge with color)                 │
│  ├─ Label badge (color-coded: blue/purple/orange/red)            │
│  ├─ Explanation card with all details                            │
│  ├─ Comparison card with baseline vs corporate                   │
│  └─ Rule strength chart visualization                            │
│                                                                       │
│  exportToCSV():                                                     │
│  ├─ Collect all results[id] objects                               │
│  ├─ Extract inputs and scores                                     │
│  ├─ Generate CSV headers + rows                                   │
│  ├─ Create Blob (client-side)                                     │
│  └─ Trigger browser download                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Profile Routing Logic

```
                    User Selects Profile
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
           General      Technical    Leadership
              │            │            │
              │            │            ├─ Show Proactivity column
              │            │            ├─ Require Proactivity input
              │            │            └─ Apply proactivity boost
              │            │
              └────────────┼────────────┘
                           │
                  Standard Rule Base
                    (21 rules total)
                    r1–r9: Basic combination
                    r10–r21: Advanced combination
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
         evaluation_mode          (if leadership)
         =========════════        Apply Boost:
         │                        if proactivity_high:
         ├─ baseline:                strength_excellent
         │  No guardrails              = max(previous,
         │  Score = Direct                    proactivity)
         │
         └─ corporate_v2:
            Apply Guardrails
            • behavior_risk cap
            • attendance cap
            • combined_risk boost
            Score adjusted + tracked
```

## Feature Integration Points

```
Feature 1: Profiles
  └─ changeProfile() → visibility toggle → API param

Feature 2: CSV Export
  └─ exportToCSV() → client-side Blob → browser download

Feature 3: Comparison Panel
  └─ fetchBaselineComparison() → dual API calls → renderComparison()

Feature 4: Chart
  └─ Chart.js CDN → canvas element → renderComparison()

Feature 5: Validation Panel
  └─ explanation.policy_adjustments → display in comparison card
```

## Data Structure: Explanation Object

```javascript
explanation = {
  // Input memberships and strongest term
  inputs: {
    attendance: {
      value: 95,
      memberships: {low: 0.0, medium: 0.15, high: 0.95},
      strongest: {term: "high", strength: 0.95}
    },
    productivity: {...},
    cooperation: {...},
    suggestions: {...},
    proactivity: {...}  // only if leadership profile
  },

  // Rules that fired
  rule_strengths: [
    {id: "r1", description: "High productivity and high attendance",
     output: "Excellent", strength: 0.92},
    {id: "r4", description: "Medium productivity and high attendance",
     output: "Excellent", strength: 0.88},
    ...
  ],

  // Output membership strengths
  output_strengths: {
    Excellent: 0.92,
    Good: 0.78,
    Acceptable: 0.45,
    Weak: 0.0
  },

  // For comparison
  pre_policy_output_strengths: {
    Excellent: 0.99,  // Before guardrails
    Good: 0.78,
    Acceptable: 0.45,
    Weak: 0.0
  },

  // Policy adjustments applied
  policy_adjustments: [
    {
      type: "excellent_cap_behavior",
      before: 0.99,
      after: 0.92,
      risk: 0.75,  // weak cooperation membership
      reason: "Weak cooperation or few suggestions limit Excellent outcomes."
    }
  ],

  // Mode info
  evaluation_mode: "corporate_v2",
  score_band: "Excellent"
}
```

---

This architecture ensures clean separation of concerns:
- **fuzzy_system.py**: Pure fuzzy logic computation
- **api.py**: HTTP routing and validation
- **index.html**: UI rendering and user interaction

All features are loosely coupled and can be extended independently.
