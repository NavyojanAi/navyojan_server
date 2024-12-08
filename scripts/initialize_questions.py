import json
from userapp.models import Questions

# Load data from questions.json
def initialize_questions():
    with open('D:/navyojan_backend/navyojan/scripts/questions.json', 'r') as file:
        questions_data = json.load(file)

    # Create Question objects for each data entry
    for question in questions_data:
        Questions.objects.get_or_create(
            text=question['text'],
            category=question['category'],
            options=question.get('options', {})
        )
