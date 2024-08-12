import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "navyojan.settings")
django.setup()

from userapp.models.scholarships import Category

def initialize_categories():
    categories = [
        "MERIT",
        "FEMALE",
        "MALE",
        "SPORTS",
        "COLLEGE LEVEL",
        "MINORITIES",
        "TALENT BASED",
        "DIFFERENTLY ABLED",
        "SCHOOL LEVEL",
    ]

    for category_name in categories:
        Category.objects.get_or_create(name=category_name)

    print("Categories initialized successfully.")

if __name__ == "__main__":
    initialize_categories()