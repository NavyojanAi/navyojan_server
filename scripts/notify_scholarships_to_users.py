import os
import django
from django.utils import timezone
from datetime import timedelta
from openai import OpenAI
from ai.config import OPEN_AI_KEY

from userapp.models.user import (
    User, UserProfile, UserDocuments, UserPreferences, UserScholarshipStatus
)

from userapp.models.scholarships import ScholarshipData, Category, Eligibility, Documents, UserScholarshipApplicationData
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "navyojan.settings")
django.setup()



def perform():
    now = timezone.now()
    # one_day_ago = now - timedelta(days=1)
    
    # Get all available scholarships that are not expired
    scholarships = ScholarshipData.objects.filter(
        # datetime_created__date=one_day_ago.date(),
        is_approved=True,
        deadline__gte=now  #ensures the scholarship is not expired
    )

    for scholarship in scholarships:
        # Get users who have preferences matching the scholarship categories
        users = User.objects.filter(
            plan_tracker__end_date__gt=timezone.now(),
            # userprofile__plan__isnull=False,
            category_preferences__categories__in=scholarship.categories.all()
        ).distinct()

        for user in users:
            if check_eligibility_with_gpt(user, scholarship):
                if user.userprofile.plan.amount == 14900:
                    notify_user(user, scholarship, auto_apply=False)
                elif user.userprofile.plan.amount == 24900:
                    notify_user(user, scholarship, auto_apply=True)

def check_eligibility_with_gpt(user, scholarship):
    client = OpenAI(api_key=OPEN_AI_KEY)

    # Correct way to access UserProfile and UserDocuments
    user_profile = UserProfile.objects.get(user=user)
    try:
        user_documents = UserDocuments.objects.get(user=user)
    except UserDocuments.DoesNotExist:
        user_documents = None

    user_data = f"""
    User Profile:
    - Gender: {user_profile.gender}
    - Education Level: {user_profile.education_level}
    - Field of Study: {user_profile.field_of_study}
    - Country: {user_profile.country}

    User Documents:
    - 10th Marksheet: {"Uploaded" if user_documents and user_documents.certificate_tenth else "Not Uploaded"}
    - 12th Marksheet: {"Uploaded" if user_documents and user_documents.certificate_inter else "Not Uploaded"}
    - Disability Certificate: {"Uploaded" if user_documents and user_documents.certificate_disability else "Not Uploaded"}
    - Sports Certificate: {"Uploaded" if user_documents and user_documents.certificate_sports else "Not Uploaded"}
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
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI assistant that determines scholarship eligibility."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip().lower() == 'yes'




# def notify_user(user, scholarship):
#     # Create or update UserScholarshipStatus
#     UserScholarshipStatus.objects.update_or_create(
#         user=user,
#         scholarship=scholarship,
#         defaults={'status': 'pending'}
#     )
    
#     # Here you would typically send an email or push notification to the user
#     print(f"Notifying user {user.username} about scholarship {scholarship.title}")

def notify_user(user, scholarship, auto_apply):
    if auto_apply:
        # Create or update UserScholarshipStatus
        UserScholarshipApplicationData.objects.update_or_create(     #change this with respect to scholarships.py
            user=user,
            scholarship=scholarship,
            defaults={'status': 'applied'}
        )
        # Notify user about auto-application
        print(f"User {user.username} has been auto-applied for scholarship {scholarship.title}.")
        
        # SEND ALL THIS USER DETAIL TO SCHOLARSHIP PROVIDER
        # APPLY AND SEND THE MAIL
        
        
        # ScholarshipData.host = who actually hosted it 
        # ScholarshipData.host.user.email
        
        
        # Here you would typically send an email or push notification to the user
    else:
        # Create or update UserScholarshipStatus
        UserScholarshipApplicationData.objects.update_or_create(
            user=user,
            scholarship=scholarship,
            defaults={'status': 'eligible'}
        )
        # Notify user about the scholarship details
        print(f"Notifying user {user.username} about scholarship {scholarship.title}.")


        # SEND ONLY MAIL TO USER

if __name__ == "__main__":
    perform()
    
    
#for 149 I have to send user the 