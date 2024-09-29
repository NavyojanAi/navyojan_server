import os
import django
from django.utils import timezone
from datetime import timedelta
from openai import OpenAI
from ai.config import OPEN_AI_KEY

from userapp.models.user import (
    User, UserProfile, UserDocuments, UserPreferences, UserScholarshipStatus
)
from userapp.models.scholarships import ScholarshipData, Category
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "navyojan.settings")
django.setup()


def perform():
    now = timezone.now()
    one_day_ago = now - timedelta(days=1)
    
    # Get scholarships created in the last day
    scholarships = ScholarshipData.objects.filter(
        datetime_created__date=one_day_ago.date(),
        is_approved=True
    )

    for scholarship in scholarships:
        # Get users who have preferences matching the scholarship categories and an active subscription
        users = User.objects.filter(
            userplantracker__end_date__gt=timezone.now(),
            category_preferences__categories__in=scholarship.categories.all()
        ).distinct()

        for user in users:
            if check_eligibility_with_gpt(user, scholarship):
                notify_user(user, scholarship)

def check_eligibility_with_gpt(user, scholarship):
    client = OpenAI(api_key=OPEN_AI_KEY)

    # Prepare user profile data
    user_profile = user.userprofile
    user_documents = user.documents
    user_data = f"""
    User Profile:
    - Gender: {user_profile.gender}
    - Education Level: {user_profile.education_level}
    - Field of Study: {user_profile.field_of_study}
    - Country: {user_profile.country}

    User Documents:
    - 10th Marksheet: {"Uploaded" if user_documents.certificate_tenth else "Not Uploaded"}
    - 12th Marksheet: {"Uploaded" if user_documents.certificate_inter else "Not Uploaded"}
    - Disability Certificate: {"Uploaded" if user_documents.certificate_disability else "Not Uploaded"}
    - Sports Certificate: {"Uploaded" if user_documents.certificate_sports else "Not Uploaded"}
    """

    # Prepare scholarship eligibility and document requirements
    scholarship_data = f"""
    Scholarship Eligibility Criteria:
    {', '.join([f"{e.name}: {e.display_name}" for e in scholarship.eligibility.all()])}

    Required Documents:
    {', '.join([d.name for d in scholarship.document_needed.all()])}
    """

    prompt = f"""
    Based on the following information, determine if the user is eligible for the scholarship.
    Consider both the eligibility criteria and the required documents.

    {scholarship_data}

    {user_data}

    Is the user eligible for this scholarship? Respond with only 'Yes' or 'No'.
    """

    response = client.chat.completions.create(
        model="gpt-4-mini",
        messages=[
            {"role": "system", "content": "You are an AI assistant that determines scholarship eligibility."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip().lower() == 'yes'

def notify_user(user, scholarship):
    # Create or update UserScholarshipStatus
    UserScholarshipStatus.objects.update_or_create(
        user=user,
        scholarship=scholarship,
        defaults={'status': 'pending'}
    )
    
    # Here you would typically send an email or push notification to the user
    print(f"Notifying user {user.username} about scholarship {scholarship.title}")

if __name__ == "__main__":
    perform()