import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


# Define the fuzzy variables

attendance_range   = np.arange(0, 101, 1)
productivity_range = np.arange(0, 101, 1)
cooperation_range  = np.arange(0, 11, 1)
suggestions_range  = np.arange(0, 11, 1)
proactivity_range  = np.arange(0, 11, 1)
performance_range  = np.arange(0, 101, 1)

attendance_low    = fuzz.trapmf(attendance_range, [0, 0, 40, 60])
attendance_medium = fuzz.trimf(attendance_range,  [40, 65, 85])
attendance_high   = fuzz.trapmf(attendance_range, [75, 90, 100, 100])


productivity_low    = fuzz.trapmf(productivity_range, [0, 0, 40, 55])
productivity_medium = fuzz.trimf(productivity_range,  [45, 65, 80])
productivity_high   = fuzz.trapmf(productivity_range, [70, 85, 100, 100])


cooperation_weak       = fuzz.trapmf(cooperation_range, [0, 0, 3, 5])
cooperation_acceptable = fuzz.trimf(cooperation_range,  [4, 6, 8])
cooperation_excellent  = fuzz.trapmf(cooperation_range, [7, 9, 10, 10])


suggestions_few    = fuzz.trapmf(suggestions_range, [0, 0, 2, 4])
suggestions_medium = fuzz.trimf(suggestions_range,  [3, 5, 7])
suggestions_many   = fuzz.trapmf(suggestions_range, [6, 8, 10, 10])

proactivity_low    = fuzz.trapmf(proactivity_range, [0, 0, 3, 5])
proactivity_medium = fuzz.trimf(proactivity_range,  [4, 6, 8])
proactivity_high   = fuzz.trapmf(proactivity_range, [7, 9, 10, 10])

performance_weak       = fuzz.trapmf(performance_range, [0, 0, 30, 45])
performance_acceptable = fuzz.trimf(performance_range,  [35, 50, 65])
performance_good       = fuzz.trimf(performance_range,  [55, 70, 85])
performance_excellent  = fuzz.trapmf(performance_range, [75, 90, 100, 100])

# print("Fuzzy variables and membership functions defined successfully.")

# Define the rules
def get_membership(value, mf_array, universe):
    return float(fuzz.interp_membership(universe, mf_array, value))

def _strongest_membership(memberships):
    term, strength = max(memberships.items(), key=lambda item: item[1])
    return {"term": term, "strength": round(float(strength), 3)}


def _apply_profile_tuning(profile, strengths, memberships, proactivity_val=None):
    adjusted = dict(strengths)
    adjustments = []
    score_bias = 0.0

    if profile == "technical":
        technical_focus = max(memberships["attendance"]["high"], memberships["productivity"]["high"])
        if technical_focus > 0:
            previous = adjusted["Excellent"]
            adjusted["Excellent"] = min(1.0, adjusted["Excellent"] + technical_focus * 0.12)
            score_bias += technical_focus * 2.0
            if adjusted["Excellent"] > previous:
                adjustments.append({
                    "type": "technical_focus",
                    "before": round(previous, 3),
                    "after": round(adjusted["Excellent"], 3),
                    "reason": "Technical profile gives extra weight to strong attendance and productivity.",
                })
        return adjusted, adjustments, score_bias

    if profile == "leadership" and proactivity_val is not None:
        proactivity_strength = get_membership(proactivity_val, proactivity_high, proactivity_range)
        if proactivity_strength > 0:
            previous = adjusted["Excellent"]
            adjusted["Excellent"] = min(1.0, adjusted["Excellent"] + proactivity_strength * 0.15)
            score_bias += proactivity_strength * 1.5
            if adjusted["Excellent"] > previous:
                adjustments.append({
                    "type": "leadership_proactivity",
                    "before": round(previous, 3),
                    "after": round(adjusted["Excellent"], 3),
                    "reason": "Leadership profile rewards high proactivity.",
                })

    return adjusted, adjustments, score_bias


def _apply_corporate_guardrails(strengths, memberships):
    adjusted = dict(strengths)
    adjustments = []

    att_low = memberships["attendance"]["low"]
    prod_low = memberships["productivity"]["low"]
    coop_weak = memberships["cooperation"]["weak"]
    sugg_few = memberships["suggestions"]["few"]

    # Guardrail 1: Weak teamwork and few suggestions can reduce top-tier outcomes.
    behavior_risk = max(coop_weak, sugg_few)
    if behavior_risk > 0:
        previous = adjusted["Excellent"]
        adjusted["Excellent"] = min(adjusted["Excellent"], 1.0 - behavior_risk)
        if adjusted["Excellent"] < previous:
            adjustments.append({
                "type": "excellent_cap_behavior",
                "before": round(previous, 3),
                "after": round(adjusted["Excellent"], 3),
                "risk": round(behavior_risk, 3),
                "reason": "Weak cooperation or few suggestions limit Excellent outcomes.",
            })

    # Guardrail 2: Persistent low attendance should not support top-tier outcomes.
    if att_low > 0:
        previous = adjusted["Excellent"]
        adjusted["Excellent"] = min(adjusted["Excellent"], 1.0 - att_low)
        if adjusted["Excellent"] < previous:
            adjustments.append({
                "type": "excellent_cap_attendance",
                "before": round(previous, 3),
                "after": round(adjusted["Excellent"], 3),
                "risk": round(att_low, 3),
                "reason": "High low-attendance membership caps Excellent outcomes.",
            })

    # Guardrail 3: Low attendance with low productivity should pull toward Weak.
    weak_boost = min(att_low, prod_low)
    if weak_boost > 0:
        previous = adjusted["Weak"]
        adjusted["Weak"] = max(adjusted["Weak"], weak_boost)
        if adjusted["Weak"] > previous:
            adjustments.append({
                "type": "weak_boost_core",
                "before": round(previous, 3),
                "after": round(adjusted["Weak"], 3),
                "risk": round(weak_boost, 3),
                "reason": "Combined low attendance and low productivity increase Weak support.",
            })

    return adjusted, adjustments


def evaluate_employee(
    attendance_val,
    productivity_val,
    cooperation_val,
    suggestions_val,
    explain=False,
    evaluation_mode="baseline",
    profile="general",
    proactivity_val=None,
):
    att_low    = get_membership(attendance_val,   attendance_low,    attendance_range)
    att_med    = get_membership(attendance_val,   attendance_medium, attendance_range)
    att_high   = get_membership(attendance_val,   attendance_high,   attendance_range)

    prod_low   = get_membership(productivity_val, productivity_low,    productivity_range)
    prod_med   = get_membership(productivity_val, productivity_medium, productivity_range)
    prod_high  = get_membership(productivity_val, productivity_high,   productivity_range)

    coop_weak  = get_membership(cooperation_val,  cooperation_weak,       cooperation_range)
    coop_acc   = get_membership(cooperation_val,  cooperation_acceptable, cooperation_range)
    coop_exc   = get_membership(cooperation_val,  cooperation_excellent,  cooperation_range)

    sugg_few   = get_membership(suggestions_val,  suggestions_few,    suggestions_range)
    sugg_med   = get_membership(suggestions_val,  suggestions_medium, suggestions_range)
    sugg_many  = get_membership(suggestions_val,  suggestions_many,   suggestions_range)

    # Leadership profile uses proactivity as a bonus input
    pact_low   = 0.0
    pact_med   = 0.0
    pact_high  = 0.0
    if profile == "leadership" and proactivity_val is not None:
        pact_low   = get_membership(proactivity_val, proactivity_low,    proactivity_range)
        pact_med   = get_membership(proactivity_val, proactivity_medium, proactivity_range)
        pact_high  = get_membership(proactivity_val, proactivity_high,   proactivity_range)

    memberships = {
        "attendance": {
            "low": att_low,
            "medium": att_med,
            "high": att_high,
        },
        "productivity": {
            "low": prod_low,
            "medium": prod_med,
            "high": prod_high,
        },
        "cooperation": {
            "weak": coop_weak,
            "acceptable": coop_acc,
            "excellent": coop_exc,
        },
        "suggestions": {
            "few": sugg_few,
            "medium": sugg_med,
            "many": sugg_many,
        },
    }

    if profile == "leadership":
        memberships["proactivity"] = {
            "low": pact_low,
            "medium": pact_med,
            "high": pact_high,
        }


   
    r1  = min(prod_high, att_high)   
    r2  = min(prod_high, att_med)     
    r3  = min(prod_high, att_low)  
    r4  = min(prod_med,  att_high)    
    r5  = min(prod_med,  att_med)     
    r6  = min(prod_med,  att_low)     
    r7  = min(prod_low,  att_high)   
    r8  = min(prod_low,  att_med)     
    r9  = min(prod_low,  att_low)     

    r10 = min(prod_high, att_low,  coop_exc,  sugg_many)  
    r11 = min(prod_high, att_med,  coop_weak, sugg_few)    
    r12 = min(prod_high, att_high, coop_weak, sugg_few)    
    r13 = min(prod_low,  att_low,  coop_exc,  sugg_many)   
    r14 = min(prod_med,  att_low,  coop_exc,  sugg_few)    
    r15 = min(prod_med,  att_med,  coop_acc,  sugg_med)   
    r16 = min(prod_med,  att_med,  coop_exc,  sugg_med)    
    r17 = min(prod_med,  att_low,  coop_acc,  sugg_many)   
    r18 = min(prod_high, att_high, coop_acc,  sugg_many)   
    r19 = min(prod_low,  att_low,  coop_acc,  sugg_med)    
    r20 = min(prod_med,  att_med,  coop_weak, sugg_med)    
    r21 = min(prod_low,  att_med,  coop_weak, sugg_few)    

    # Profile-specific rule adjustments for leadership
    if profile == "leadership" and proactivity_val is not None:
        # Leaders with high proactivity get elevated output
        leadership_boost = pact_high
    else:
        leadership_boost = 0.0    

    strength_excellent  = max(r1, r2, r4, r10, r16, r18)
    strength_good       = max(r3, r5, r11, r12, r15, r17, r20)
    strength_acceptable = max(r6, r7, r8, r13, r14, r19)
    strength_weak       = max(r9, r21)

    # Apply profile boost for leadership
    if profile == "leadership" and leadership_boost > 0:
        strength_excellent = max(strength_excellent, leadership_boost)

    pre_policy_strengths = {
        "Excellent": strength_excellent,
        "Good": strength_good,
        "Acceptable": strength_acceptable,
        "Weak": strength_weak,
    }

    policy_adjustments = []
    if evaluation_mode == "corporate_v2":
        adjusted_strengths, policy_adjustments = _apply_corporate_guardrails(
            pre_policy_strengths,
            memberships,
        )
        strength_excellent = adjusted_strengths["Excellent"]
        strength_good = adjusted_strengths["Good"]
        strength_acceptable = adjusted_strengths["Acceptable"]
        strength_weak = adjusted_strengths["Weak"]

    profile_adjustments = []
    tuned_strengths, profile_adjustments, profile_score_bias = _apply_profile_tuning(
        profile,
        {
            "Excellent": strength_excellent,
            "Good": strength_good,
            "Acceptable": strength_acceptable,
            "Weak": strength_weak,
        },
        memberships,
        proactivity_val=proactivity_val,
    )
    strength_excellent = tuned_strengths["Excellent"]
    strength_good = tuned_strengths["Good"]
    strength_acceptable = tuned_strengths["Acceptable"]
    strength_weak = tuned_strengths["Weak"]

    rules = [
        {"id": "r1",  "output": "Excellent",  "strength": r1,  "description": "High productivity and high attendance"},
        {"id": "r2",  "output": "Excellent",  "strength": r2,  "description": "High productivity and medium attendance"},
        {"id": "r3",  "output": "Good",       "strength": r3,  "description": "High productivity and low attendance"},
        {"id": "r4",  "output": "Excellent",  "strength": r4,  "description": "Medium productivity and high attendance"},
        {"id": "r5",  "output": "Good",       "strength": r5,  "description": "Medium productivity and medium attendance"},
        {"id": "r6",  "output": "Acceptable", "strength": r6,  "description": "Medium productivity and low attendance"},
        {"id": "r7",  "output": "Acceptable", "strength": r7,  "description": "Low productivity and high attendance"},
        {"id": "r8",  "output": "Acceptable", "strength": r8,  "description": "Low productivity and medium attendance"},
        {"id": "r9",  "output": "Weak",       "strength": r9,  "description": "Low productivity and low attendance"},
        {"id": "r10", "output": "Excellent",  "strength": r10, "description": "High productivity, low attendance, excellent cooperation, many suggestions"},
        {"id": "r11", "output": "Good",       "strength": r11, "description": "High productivity, medium attendance, weak cooperation, few suggestions"},
        {"id": "r12", "output": "Good",       "strength": r12, "description": "High productivity, high attendance, weak cooperation, few suggestions"},
        {"id": "r13", "output": "Acceptable", "strength": r13, "description": "Low productivity, low attendance, excellent cooperation, many suggestions"},
        {"id": "r14", "output": "Acceptable", "strength": r14, "description": "Medium productivity, low attendance, excellent cooperation, few suggestions"},
        {"id": "r15", "output": "Good",       "strength": r15, "description": "Medium productivity, medium attendance, acceptable cooperation, medium suggestions"},
        {"id": "r16", "output": "Excellent",  "strength": r16, "description": "Medium productivity, medium attendance, excellent cooperation, medium suggestions"},
        {"id": "r17", "output": "Acceptable", "strength": r17, "description": "Medium productivity, low attendance, acceptable cooperation, many suggestions"},
        {"id": "r18", "output": "Excellent",  "strength": r18, "description": "High productivity, high attendance, acceptable cooperation, many suggestions"},
        {"id": "r19", "output": "Acceptable", "strength": r19, "description": "Low productivity, low attendance, acceptable cooperation, medium suggestions"},
        {"id": "r20", "output": "Good",       "strength": r20, "description": "Medium productivity, medium attendance, weak cooperation, medium suggestions"},
        {"id": "r21", "output": "Weak",       "strength": r21, "description": "Low productivity, medium attendance, weak cooperation, few suggestions"},
    ]

    perf_weak_clipped       = np.fmin(strength_weak,       performance_weak)
    perf_acceptable_clipped = np.fmin(strength_acceptable, performance_acceptable)
    perf_good_clipped       = np.fmin(strength_good,       performance_good)
    perf_excellent_clipped  = np.fmin(strength_excellent,  performance_excellent)


    aggregated = np.fmax(perf_weak_clipped,
                 np.fmax(perf_acceptable_clipped,
                 np.fmax(perf_good_clipped,
                         perf_excellent_clipped)))
    if np.sum(aggregated) == 0:
        score = 0.0
    else:
        score = fuzz.defuzz(performance_range, aggregated, 'centroid')

    score = min(100.0, score + profile_score_bias)

    if score >= 75:
        label = "Excellent"
    elif score >= 55:
        label = "Good"
    elif score >= 35:
        label = "Acceptable"
    else:
        label = "Weak"

    explanation = {
        "inputs": {
            "attendance": {
                "value": attendance_val,
                "memberships": memberships["attendance"],
                "strongest": _strongest_membership(memberships["attendance"]),
            },
            "productivity": {
                "value": productivity_val,
                "memberships": memberships["productivity"],
                "strongest": _strongest_membership(memberships["productivity"]),
            },
            "cooperation": {
                "value": cooperation_val,
                "memberships": memberships["cooperation"],
                "strongest": _strongest_membership(memberships["cooperation"]),
            },
            "suggestions": {
                "value": suggestions_val,
                "memberships": memberships["suggestions"],
                "strongest": _strongest_membership(memberships["suggestions"]),
            },
        },
        "rule_strengths": sorted(
            [rule for rule in rules if rule["strength"] > 0],
            key=lambda rule: rule["strength"],
            reverse=True,
        ),
        "output_strengths": {
            "Excellent": strength_excellent,
            "Good": strength_good,
            "Acceptable": strength_acceptable,
            "Weak": strength_weak,
        },
        "pre_policy_output_strengths": pre_policy_strengths,
        "evaluation_mode": evaluation_mode,
        "policy_adjustments": policy_adjustments,
        "profile_adjustments": profile_adjustments,
        "score_band": label,
    }

    if explain:
        return round(score, 2), label, explanation

    return round(score, 2), label
                                

print("Fuzzy control system created successfully with the defined rules.")