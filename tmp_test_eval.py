from fuzzy_system import evaluate_employee

# Sample inputs
attendance = 80
productivity = 75
cooperation = 8
suggestions = 6

print('Testing general profile...')
print(evaluate_employee(attendance, productivity, cooperation, suggestions, explain=True, evaluation_mode='baseline', profile='general'))

print('\nTesting leadership profile without proactivity...')
print(evaluate_employee(attendance, productivity, cooperation, suggestions, explain=True, evaluation_mode='baseline', profile='leadership'))

print('\nTesting leadership profile with proactivity 8...')
print(evaluate_employee(attendance, productivity, cooperation, suggestions, explain=True, evaluation_mode='baseline', profile='leadership', proactivity_val=8))

print('\nTesting technical profile...')
print(evaluate_employee(attendance, productivity, cooperation, suggestions, explain=True, evaluation_mode='baseline', profile='technical'))
