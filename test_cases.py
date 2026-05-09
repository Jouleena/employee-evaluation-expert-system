from fuzzy_system import evaluate_employee

# =====================================================
# Test Cases — Employee Performance Expert System
# =====================================================

test_cases = [
    {
        "id": "TC01",
        "name": "Lujain Alashfa",
        "description": "Ideal employee — all metrics high",
        "attendance": 95, "productivity": 92,
        "cooperation": 9, "suggestions": 8,
        "expected": "Excellent"
    },
    {
        "id": "TC02",
        "name": "LoLO Alashafi",
        "description": "Remote worker — low attendance, high productivity",
        "attendance": 35, "productivity": 88,
        "cooperation": 7, "suggestions": 6,
        "expected": "Good"
    },
    {
        "id": "TC03",
        "name": "Jouleen ashafi",
        "description": "Present but unproductive",
        "attendance": 92, "productivity": 30,
        "cooperation": 5, "suggestions": 3,
        "expected": "Acceptable"
    },
    {
        "id": "TC04",
        "name": "JoJo ashash",
        "description": "Weak employee — all metrics low",
        "attendance": 25, "productivity": 20,
        "cooperation": 2, "suggestions": 1,
        "expected": "Weak"
    },
    {
        "id": "TC05",
        "name": "jOUL LEEN",
        "description": "Average employee — all metrics medium",
        "attendance": 65, "productivity": 62,
        "cooperation": 6, "suggestions": 5,
        "expected": "Good"
    },
    {
        "id": "TC06",
        "name": "jOUL jOUL",
        "description": "High productivity, low cooperation and suggestions",
        "attendance": 88, "productivity": 90,
        "cooperation": 2, "suggestions": 1,
        "expected": "Good"
    },
    {
        "id": "TC07",
        "name": "lUJAIN LUJAIN",
        "description": "Medium productivity boosted by excellent cooperation",
        "attendance": 70, "productivity": 65,
        "cooperation": 9, "suggestions": 7,
        "expected": "Excellent"
    },
    {
        "id": "TC08",
        "name": "JOUL JOULEEN",
        "description": "Low attendance, medium productivity, weak cooperation",
        "attendance": 40, "productivity": 55,
        "cooperation": 3, "suggestions": 2,
        "expected": "Weak"
    },
]


def run_tests():
    print("=" * 70)
    print("   Employee Performance Expert System — Test Cases")
    print("=" * 70)

    passed = 0
    failed = 0

    for tc in test_cases:
        score, label = evaluate_employee(
            tc["attendance"],
            tc["productivity"],
            tc["cooperation"],
            tc["suggestions"]
        )

        status = "PASS" if label == tc["expected"] else "FAIL"
        passed += 1 if status == "PASS" else 0
        failed += 1 if status == "FAIL" else 0

        print(f"\n{tc['id']} — {tc['name']}")
        print(f"  Description  : {tc['description']}")
        print(f"  Attendance   : {tc['attendance']}%   "
              f"Productivity : {tc['productivity']}   "
              f"Cooperation : {tc['cooperation']}/10   "
              f"Suggestions : {tc['suggestions']}/10")
        print(f"  Score        : {score} / 100")
        print(f"  Result       : {label}")
        print(f"  Expected     : {tc['expected']}")
        print(f"  Status       : [ {status} ]")

    print("\n" + "=" * 70)
    print(f"  Total: {len(test_cases)} tests  |  Passed: {passed}  |  Failed: {failed}")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
