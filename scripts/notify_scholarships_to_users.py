from userapp.models import ScholarshipData, Category, UserPreferences, UserScholarshipApplicationData,UserProfile
from django.contrib.auth.models import User

from django.utils import timezone
from datetime import timedelta

from openai import OpenAI
import os
from ai.config import OPEN_AI_KEY


def perform():
    now = timezone.now()
    one_day_ago = now - timedelta(days=1)
    categories = Category.objects.all()

    for category in categories:
        scholarships = ScholarshipData.objects.filter(
            categories=category,
            datetime_created__date=one_day_ago.date()
            )
        users = User.objects.filter(
            userprofile__premium_account_privilages=True,
            category_preferences__categories=category
            )
        # user_ids = UserPreferences.objects.filter(categories=category,user__userprofile__premium_account_privilages=True).values_list('user_id', flat=True)

        # TODO: eligibility check

        final_users = users
        final_users1 = []

        for scholarship in scholarships:
            for user in final_users:
                user_profile = UserProfile.objects.get(user=user)
                user_profile_data = f"""
                Gender: {user_profile.gender}
                Education Level: {user_profile.education_level}
                Field of Study: {user_profile.field_of_study}
                Country: {user_profile.country}
                """
                # "documents": {
                #         "sports_certificate": user_profile.documents.certificate_sports if user.documents else None,
                #         "disability_certificate": user_profile.documents.certificate_disability if user.documents else None,
                #     }
                
                is_eligible = check_eligibility_with_gpt(scholarship.eligibility, user_profile_data)
                if is_eligible == "yes":
                    final_users1.append(user)
                    
                    application ,created=UserScholarshipApplicationData.objects.get_or_create(
                        user=user,
                        scholarship=scholarship,
                        is_applied=True
                        )
                    if not created:
                        application.is_interested=True      #change from application.is_applied=True
                        application.save()


def check_eligibility_with_gpt(scholarship_eligibility, user_profile):
    client = OpenAI(api_key=OPEN_AI_KEY)
    prompt = f"""
    Scholarship Eligibility Criteria:
    {scholarship_eligibility}

    User Profile:
    {user_profile}

    Based on the scholarship eligibility criteria and the user profile, is the user eligible for this scholarship? Respond with only 'Yes' or 'No'.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI assistant that determines scholarship eligibility."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip().lower()
