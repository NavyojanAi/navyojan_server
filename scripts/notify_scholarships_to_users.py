import os
import django
from django.utils import timezone
from datetime import timedelta
from openai import OpenAI
from django.db.models import Q
from tasks.send_email import send_email_task

from userapp.models.user import (
    User, UserProfile, UserDocuments, UserPreferences, UserScholarshipStatus, 
    UserDocumentSummary
)
from userapp.models.scholarships import (
    ScholarshipData, Category, Eligibility, Documents, 
    UserScholarshipApplicationData
)
from sys import stdout
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "navyojan.settings")
django.setup()

def check_eligibility_with_gpt(user, scholarship):
    client = OpenAI(api_key="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")

    try:
        # Get all relevant user data
        user_profile = UserProfile.objects.get(user=user)
        print(f"Found user profile for {user.username}")  # Debug print
        
        doc_summary = UserDocumentSummary.objects.get(user=user)
        print(f"Found document summary for {user.username}")  # Debug print
        

        # Prepare detailed user data
        user_data = {
            "personal_info": {
                "gender": user_profile.gender,
                "education_level": user_profile.education_level,
                "field_of_study": user_profile.field_of_study,
                "country": user_profile.country
            },
            "academic_details": {
                "cgpa": doc_summary.cgpa,
                "percentage": doc_summary.percentage,
                "tenth_details": doc_summary.certificate_tenth,
                "twelfth_details": doc_summary.certificate_inter,
            },
            "certificates": {
                "disability": doc_summary.certificate_disability,
                "sports": doc_summary.certificate_sports
            }
        }

        # Prepare scholarship requirements
        scholarship_requirements = {
            "eligibility_criteria": [
                {"name": e.name, "display_name": e.display_name} 
                for e in scholarship.eligibility.all()
            ],
            "required_documents": [
                d.name for d in scholarship.document_needed.all()
            ],
            "categories": [
                c.name for c in scholarship.categories.all()
            ]
        }
        # print(scholarship_requirements)
        # print(user_data)
        # print(scholarship.title)
        # Prepare the prompt
        prompt = f"""
        Analyze if the user is eligible for this scholarship based on the following data:

        Scholarship Title:
        {scholarship.title}

        Scholarship Requirements:
        {scholarship_requirements}

        User Profile and Documents:
        {user_data}

        Consider the following rules:
        1. Check if the user's academic performance meets the requirements
        2. Match gender-specific criteria if any
        ***
        IMPORTANT NOTE: RESPOND WITH ONLY 'Yes' if the criteria are met, or 'No' if ANY criterion is not met, DO NOT RETURN WITH ANY PARAGRAPHS OR EXPLANATIONS,just say 'yes' or 'no'.
        ***
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a precise scholarship eligibility verification system who verifies whether the student is eligible for the particular scholarship or not (Be a little lenient)."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        print(response.choices[0].message.content.strip().lower())
        return response.choices[0].message.content.strip().lower() == 'yes'

    except (UserProfile.DoesNotExist, UserDocumentSummary.DoesNotExist):
        return False
    except Exception as e:
        print(f"Error checking eligibility for user {user.id}: {str(e)}")
        return False

def notify_user(user, scholarship, auto_apply):
    try:
        if auto_apply:
            # Create application with 'applied' status
            UserScholarshipApplicationData.objects.update_or_create(
                user=user,
                scholarship=scholarship,
                defaults={'status': 'applied'}
            )
            # stdout.write(stdout.style.SUCCESS(f'Successfully scraped and imported scholarships'))

            print(f"User {user.username} has been auto-applied for scholarship {scholarship.title}.")
            # Get scholarship provider's email
            # provider_email = scholarship.host.user.email if scholarship.host else None

            # if provider_email:
            #     # Prepare and send provider email
            #     subject_provider = "New Scholarship Application Received"
            #     body_provider = f"""
            #     New application received:
            #     Scholarship: {scholarship.title}
            #     Applicant: {user.username}
            #     Email: {user.email}
            #     Phone: {user.userprofile.phone_number}
            #     Education: {user.userprofile.education_level}
            #     Field: {user.userprofile.field_of_study}
            #     """
            #     send_email_task.delay(subject_provider, body_provider, [provider_email])

            # # Notify user about auto-application
            # subject_user = "Scholarship Application Submitted"
            # body_user = f"""
            # Dear {user.username},
            
            # We've submitted your application for:
            # {scholarship.title}
            
            # Application Status: Submitted
            # Next Steps: The scholarship provider will review your application
            # """
            # send_email_task.delay(subject_user, body_user, [user.email])

        else:
            # Create notification with 'eligible' status
            UserScholarshipApplicationData.objects.update_or_create(
                user=user,
                scholarship=scholarship,
                defaults={'status': 'eligible'}
            )
            print(f"Notifying user {user.username} about scholarship {scholarship.title}.")
            # Notify user about eligibility
            # subject_user = "New Scholarship Opportunity"
            # body_user = f"""
            # Dear {user.username},
            
            # You're eligible for:
            # {scholarship.title}
            
            # Visit navyojan.in to apply!
            # """
            # send_email_task.delay(subject_user, body_user, [user.email])

    except Exception as e:
        print(f"Error notifying user {user.id} about scholarship {scholarship.id}: {str(e)}")

def perform():

    # Debug counts
    print(f"Total scholarships: {ScholarshipData.objects.all().count()}")
    print(f"Approved scholarships: {ScholarshipData.objects.filter(is_approved=True).count()}")
    print(f"Future deadline scholarships: {ScholarshipData.objects.filter(deadline__gte=timezone.now()).count()}")
    print(f"Total users: {User.objects.all().count()}")
    print(f"Users with plans: {User.objects.filter(plan_tracker__end_date__gt=timezone.now()).count()}")
    print(f"Users with doc summaries: {UserDocumentSummary.objects.all().count()}")
    print("\nStarting main process...")

    now = timezone.now()
    
    # Get active scholarships
    scholarships = ScholarshipData.objects.filter(
        is_approved=True,
        deadline__gte=now
    )
    
    print(f"Found {scholarships.count()} active scholarships")  # Debug print


    for scholarship in scholarships:
        print(f"\nProcessing scholarship: {scholarship.title}")  # Debug print
        # Get users with matching preferences and active plans
        users = User.objects.filter(
            plan_tracker__end_date__gt=timezone.now(),
            category_preferences__categories__in=scholarship.categories.all()
        ).distinct()
        
        
        print(f"Found {users.count()} potentially eligible users")  # Debug print


        for user in users:
            print(f"\nChecking eligibility for user: {user.username}")  # Debug print
            
            if check_eligibility_with_gpt(user, scholarship):
                # Auto-apply for premium plan users
                auto_apply = user.userprofile.plan.amount >= 24900
                notify_user(user, scholarship, auto_apply)




# Add this function
def verify_data():
    # Check scholarships
    scholarships = ScholarshipData.objects.filter(
        is_approved=True,
        deadline__gte=timezone.now()
    )
    if not scholarships.exists():
        print("No active scholarships found!")
        return False

    # Check users
    users_with_plans = User.objects.filter(
        plan_tracker__end_date__gt=timezone.now()
    )
    if not users_with_plans.exists():
        print("No users with active plans found!")
        return False

    # Check category preferences
    users_with_preferences = UserPreferences.objects.all()
    if not users_with_preferences.exists():
        print("No users with category preferences found!")
        return False

    # Check document summaries
    doc_summaries = UserDocumentSummary.objects.all()
    if not doc_summaries.exists():
        print("No document summaries found!")
        return False

    return True

def main():
    if verify_data():
        perform()
    else:
        print("Prerequisites not met. Please check the data in the database.")

# if __name__ == "__main__":
#     perform()





















# import os
# import django
# from django.utils import timezone
# from datetime import timedelta
# from openai import OpenAI
# # from ai.config import OPEN_AI_KEY

# from userapp.models.user import (
#     User, UserProfile, UserDocuments, UserPreferences, UserScholarshipStatus
# )

# from userapp.models.scholarships import ScholarshipData, Category, Eligibility, Documents, UserScholarshipApplicationData
# from tasks.send_email import send_email_task  # Import the send_email_task

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "navyojan.settings")
# django.setup()



# def perform():
#     now = timezone.now()
#     # one_day_ago = now - timedelta(days=1)
    
#     # Get all available scholarships that are not expired
#     scholarships = ScholarshipData.objects.filter(
#         # datetime_created__date=one_day_ago.date(),
#         is_approved=True,
#         deadline__gte=now  #ensures the scholarship is not expired
#     )

#     for scholarship in scholarships:
#         # Get users who have preferences matching the scholarship categories
#         users = User.objects.filter(
#             plan_tracker__end_date__gt=timezone.now(),
#             # userprofile__plan__isnull=False,
#             category_preferences__categories__in=scholarship.categories.all()
#         ).distinct()

#         for user in users:
#             if check_eligibility_with_gpt(user, scholarship):
#                 if user.userprofile.plan.amount == 14900:
#                     notify_user(user, scholarship, auto_apply=False)
#                 elif user.userprofile.plan.amount == 24900:
#                     notify_user(user, scholarship, auto_apply=True)

# def check_eligibility_with_gpt(user, scholarship):
#     client = OpenAI(api_key="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")

#     # Correct way to access UserProfile and UserDocuments
#     user_profile = UserProfile.objects.get(user=user)
#     try:
#         user_documents = UserDocuments.objects.get(user=user)
#     except UserDocuments.DoesNotExist:
#         user_documents = None

#     user_data = f"""
#     User Profile:
#     - Gender: {user_profile.gender}
#     - Education Level: {user_profile.education_level}
#     - Field of Study: {user_profile.field_of_study}
#     - Country: {user_profile.country}

#     User Documents:
#     - 10th Marksheet: {"Uploaded" if user_documents and user_documents.certificate_tenth else "Not Uploaded"}
#     - 12th Marksheet: {"Uploaded" if user_documents and user_documents.certificate_inter else "Not Uploaded"}
#     - Disability Certificate: {"Uploaded" if user_documents and user_documents.certificate_disability else "Not Uploaded"}
#     - Sports Certificate: {"Uploaded" if user_documents and user_documents.certificate_sports else "Not Uploaded"}
#     """

#     # Prepare scholarship eligibility and document requirements
#     scholarship_data = f"""
#     Scholarship Eligibility Criteria:
#     {', '.join([f"{e.name}: {e.display_name}" for e in scholarship.eligibility.all()])}

#     Required Documents:
#     {', '.join([d.name for d in scholarship.document_needed.all()])}
#     """

#     prompt = f"""
#     Based on the following information, determine if the user is eligible for the scholarship.
#     Consider both the eligibility criteria and the required documents.

#     {scholarship_data}

#     {user_data}

#     Is the user eligible for this scholarship? Respond with only 'Yes' or 'No'.
#     """

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You are an AI assistant that determines scholarship eligibility."},
#             {"role": "user", "content": prompt}
#         ]
#     )

#     return response.choices[0].message.content.strip().lower() == 'yes'





# def notify_user(user, scholarship, auto_apply):
#     if auto_apply:
#         # Create or update UserScholarshipApplicationData
#         UserScholarshipApplicationData.objects.update_or_create(
#             user=user,
#             scholarship=scholarship,
#             defaults={'status': 'applied'}
#         )
#         # Notify user about auto-application
#         print(f"User {user.username} has been auto-applied for scholarship {scholarship.title}.")
        
        
        
#         # SEND ALL THIS USER DETAIL TO SCHOLARSHIP PROVIDER
#         # APPLY AND SEND THE MAIL TODO FIXME DONE COMPLETE 
        
        
#         # ScholarshipData.host = who actually hosted it 
#         # ScholarshipData.host.user.email
#         # Prepare email details
        
#         # Prepare email details for the user
#         # subject_user = "Your Scholarship Application is Successful!"
#         # body_user = f"""
#         # Dear {user.username},

#         # Congratulations! You have been successfully auto-applied for the following scholarship:

#         # Scholarship Title: {scholarship.title}
#         # Description: {scholarship.description}
#         # Deadline: {scholarship.deadline.strftime('%Y-%m-%d')}
        
#         # Your profile has been sent to the scholarship provider for consideration.

#         # Best of luck!

#         # Regards,
#         # Navyojan Team
#         # """
        
#         # # Send email to the user
#         # send_email_task.delay(subject_user, body_user, [user.email])  # Send email asynchronously

#         # Prepare email details for the scholarship provider
#         # scholarship_provider_email = scholarship.host.user.email  # Assuming the host has an email field
#         # subject_provider = "New Scholarship Application Received"
#         # body_provider = f"""
#         # Dear Scholarship Provider,

#         # A new application has been received for the following scholarship:

#         # Scholarship Title: {scholarship.title}
#         # Description: {scholarship.description}
#         # Deadline: {scholarship.deadline.strftime('%Y-%m-%d')}

#         # Applicant Details:
#         # - Name: {user.username}
#         # - Email: {user.email}
#         # - Phone Number: {user.userprofile.phone_number}
#         # - Gender: {user.userprofile.gender}
#         # - Education Level: {user.userprofile.education_level}
#         # - Field of Study: {user.userprofile.field_of_study}
#         # - Country: {user.userprofile.country}

#         # Best regards,
#         # The Navyojan Team
#         # """
        
#         # # Send email to the scholarship provider
#         # send_email_task.delay(subject_provider, body_provider, [scholarship_provider_email])  # Send email asynchronously

#     else:
#         # Create or update UserScholarshipApplicationData
#         UserScholarshipApplicationData.objects.update_or_create(
#             user=user,
#             scholarship=scholarship,
#             defaults={'status': 'eligible'}
#         )
#         # Notify user about the scholarship details
#         print(f"Notifying user {user.username} about scholarship {scholarship.title}.")

#         # Prepare email details for the user
#         # subject_user = "Scholarship Opportunities Await You!"
#         # body_user = f"""
#         # Dear {user.username},

#         # You are eligible to apply for the following scholarship:

#         # Scholarship Title: {scholarship.title}
#         # Description: {scholarship.description}
#         # Deadline: {scholarship.deadline.strftime('%Y-%m-%d')}
        
#         # Please visit the scholarship portal navyojan.in to apply by yourself.

#         # Best of luck!

#         # Regards,
#         # Navyojan Team
#         # """
        
#         # # Send email to the user
#         # send_email_task.delay(subject_user, body_user, [user.email])  # Send email asynchronously

# if __name__ == "__main__":
#     perform()
    
    
#for 149 I have to send user the 