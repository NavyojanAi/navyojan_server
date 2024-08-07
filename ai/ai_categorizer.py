from ai.config import OPEN_AI_KEY
import os
import django
from openai import OpenAI
from django.utils import timezone
from datetime import timedelta
from userapp.models.scholarships import ScholarshipData,Category
from asgiref.sync import sync_to_async

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "navyojan.settings")
django.setup()



# Initialize OpenAI client
client = OpenAI(api_key=OPEN_AI_KEY)

def categorize_scholarship(details):
    categories = Category.objects.values_list('name', flat=True)
    
    prompt = f"Categorize the following scholarship into the following categories(give only the word) and give 'None' in case of not finding any relevancy: {', '.join(categories).lower()}.\n\nDetails: {details}\n\nCategory:"

    response = client.chat.completions.create(
        model = "gpt-4o",
        messages = [
            {"role": "user", "content": prompt}
        ]
    )
            
    category = response.choices[0].message.content.strip()
    return category if category in categories else "NONE"




@sync_to_async
def get_recent_scholarships():
    recent_time = timezone.now() - timedelta(hours=24)
    return list(ScholarshipData.objects.filter(
        datetime_created__gte=recent_time,
        category__isnull=True
    ))

@sync_to_async
def save_scholarship(scholarship):
    scholarship.save()

async def update_recent_scholarships():
    recent_scholarships = await get_recent_scholarships()

    for scholarship in recent_scholarships:
        details = f"Title: {scholarship.title}\nEligibility: {scholarship.eligibility}\nDocuments Needed: {scholarship.documents_needed}\nHow To Apply: {scholarship.how_to_apply}\nPublished On: {scholarship.published_on}\nState: {scholarship.state}\nDeadline: {scholarship.deadline}\nLink: {scholarship.link}"
        category = await sync_to_async(categorize_scholarship)(details)
        
        scholarship.category = category
        await save_scholarship(scholarship)
        print(f"Updated category for '{scholarship.title}' to '{category}'")




# def update_recent_scholarships():
#     # Get scholarships added in the last 24 hours with empty category
#     recent_time = timezone.now() - timedelta(hours=24)
#     recent_scholarships = ScholarshipData.objects.filter(
#         datetime_created__gte=recent_time,
#         category__isnull=True
#     )

#     for scholarship in recent_scholarships:
#         details = f"Title: {scholarship.title}\nEligibility: {scholarship.eligibility}\nDocuments Needed: {scholarship.document_needed}\nHow To Apply: {scholarship.how_to_apply}\nPublished On: {scholarship.published_on}\nState: {scholarship.state}\nDeadline: {scholarship.deadline}\nLink: {scholarship.link}"
#         category = categorize_scholarship(details)
        
#         scholarship.category = category
#         scholarship.save()
#         print(f"Updated category for '{scholarship.title}' to '{category}'")

if __name__ == "__main__":
    import asyncio 
    asyncio.run(update_recent_scholarships())
    
    