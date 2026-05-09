from fuzzy_system import evaluate_employee

def get_input(prompt, min_val, max_val):
    """Function to read input from the user with range validation"""
    while True:
        try:
            value = float(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"  Error: Please enter a value between {min_val} and {max_val}")
        except ValueError:
            print(" Error: Invalid input. Please enter a numeric value.")

def get_label_stars(label):
    stars = {
        "Excellent":  "★★★★★",
        "Good":    "★★★★☆",
        "Acceptable":  "★★★☆☆",
        "Weak":   "★★☆☆☆"
    }
    return stars.get(label, "")

def main():
    print("=" * 50)
    print("Employee Performance Evaluation System")
    print("Using Fuzzy Logic")
    print("=" * 50)

    print("\nEnter Employee Data:\n")

    name = input("Employee Name: ")

    attendance_val   = get_input("Attendance and Punctuality  (0-100): ", 0, 100)
    productivity_val = get_input("Productivity         (0-100): ", 0, 100)
    cooperation_val  = get_input("Teamwork with Colleagues  (0-10):  ", 0, 10)
    suggestions_val  = get_input("Development Suggestions (0-10): ", 0, 10)

    score, label = evaluate_employee(
        attendance_val,
        productivity_val,
        cooperation_val,
        suggestions_val
    )

    stars = get_label_stars(label)

    print("\n" + "=" * 50)
    print(f"   Result of Employee Evaluation: {name}")
    print("=" * 50)
    print(f"  Attendance:       {attendance_val}%")
    print(f"  Productivity:    {productivity_val}/100")
    print(f"  Cooperation:      {cooperation_val}/10")
    print(f"  Suggestions:    {suggestions_val}/10")
    print("-" * 50)
    print(f"  Final Score:          {score} / 100")
    print(f"  Evaluation:          {label}  {stars}")
    print("=" * 50)

    again = input("\nDo you want to evaluate another employee? (yes/no): ")
    if again.strip() == "yes":
        print()
        main()
    else:
        print("\nThank you for using the system     !")

if __name__ == "__main__":
    main()
