import os
import django
from decimal import Decimal
from logs import logger

# Set up Django environment
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "navyojan.settings")
# django.setup()

from userapp.models.scholarships import Category, Eligibility, Documents
from userapp.models.user_plans import SubscriptionPlan

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

    logger.info("Categories initialized successfully.")


#14900 - 149, get_notified
#24900 - 249, get_notified and auto_applied
#if user is subscribed to scholarship, then auto_applied is true

def initialize_eligibility():
    eligibility_criteria = {
        "state_domicile": "Applicant must be a permanent resident of the specified state.",
        "caste_category": "Applicant must belong to a specific caste category (e.g., SC, ST, OBC).",
        "sc_caste": "Applicant must belong to a specific caste category of SC.",    
        "st_caste": "Applicant must belong to a specific caste category of ST.",
        "obc_caste": "Applicant must belong to a specific caste category of OBC.",
        "general_category": "Applicant must belong to a specific caste category of General.",
        "annual_family_income": "Total yearly income of the applicant's family should be within the specified limit.",
        # "minimum_marks": "Applicant must have achieved the minimum required marks in their previous examination.",
        "gender": "Scholarship may be specific to a particular gender.",
        "male": "Applicant must be male.",  
        "female": "Applicant must be female.",
        "other_gender": "Applicant must be of other gender.",
        
        "course_level": "Applicable for students studying at a specific education level (e.g., high school, undergraduate, postgraduate).",
        "disability_status": "Applicant must have a recognized disability as per government norms.",
        "minority_status": "Applicant must belong to a recognized minority community.",
        "nationality": "Applicant must be a citizen of the specified country.",
        "others": "Details to be specified by the scholarship provider.",
    }

    for name, description in eligibility_criteria.items():
        Eligibility.objects.get_or_create(name=name, defaults={'description': description})

    logger.info("Eligibility criteria initialized successfully.")

def initialize_documents():
    required_documents = {
        "aadhar_card": "A unique identification number issued by the Indian government. It serves as proof of identity and address.",
        "10th_marksheet": "Official academic record showing the applicant's grades or marks in various subjects of 10th standard.",
        "12th_marksheet": "Official academic record showing the applicant's grades or marks in various subjects of 12th standard.",
        "passport_size_photo": "A recent photograph of the applicant, typically 35mm x 45mm, with a light background.",
        "domicile_certificate": "An official document proving the applicant's permanent residence in a particular state.",
        "caste_certificate": "An official document certifying the applicant's caste, issued by a competent authority.",
        "income_certificate": "An official document stating the annual income of the applicant's family, issued by a revenue officer.",
        "bank_passbook": "A copy of the first page of the applicant's bank passbook, showing account details.",
        "bonafide_certificate": "A document issued by the educational institution certifying that the applicant is a genuine student.",
        "disability_certificate": "An official document certifying the nature and extent of the applicant's disability.",
        "ration_card": "A document issued by the government that entitles households to obtain essential goods at subsidized rates.",
        "parivar_pehchan_patra": "A family ID card issued by some state governments in India.",
        "others": "Details to be specified by the scholarship provider.",
    }

    for name, description in required_documents.items():
        Documents.objects.get_or_create(name=name, defaults={'description': description})

    logger.info("Required documents initialized successfully.")
    
#TODO: add display_name and description to all the models
#TODO: check if data which is coming from scraped scholarships has key:value pair for eligibility, documents, etc.,
#       and after that add them to the database in that structure only.
#TODO: make an initialization for the subscribed scholarships, 14900 - 149, get_notified
#TODO: make an initialization for the subscribed scholarships, 24900 - 249, get_notified and auto_applied

def initialize_subscription_plans():
    subscription_plans = [
        {
            "title": "Get Notified",
            "amount": 14900,   #Decimal('149.00'),
            "duration": 365,  # 1 year in days
            # "description": "Receive notifications for new scholarships"
        },
        {
            "title": "Get Notified and Auto Apply",
            "amount": 24900,   #Decimal('249.00')
            "duration": 365,  # 1 year in days
            # "description": "Receive notifications and automatic application for new scholarships"
        }
    ]

    for plan in subscription_plans:
        SubscriptionPlan.objects.get_or_create(
            title=plan['title'],
            defaults={
                'amount': plan['amount'],
                'duration': plan['duration']
            }
        )

    logger.info("Subscription plans initialized successfully.")


# if __name__ == "__main__":
#     initialize_categories()
#     initialize_eligibility()
#     initialize_documents()
#     initialize_subscription_plans()