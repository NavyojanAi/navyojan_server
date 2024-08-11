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
    categories = list(Category.objects.values_list('name', flat=True))
    
    prompt = f"Categorize the following scholarship into one or more of these categories: {', '.join(categories)}. Respond with only the category names, separated by commas if there are multiple categories.\n\nScholarship Details: {details}\n\nCategories:"

    response = client.chat.completions.create(
        model = "gpt-4o",
        messages = [
            {"role": "user", "content": prompt}
        ]
    )
    
    
    suggested_categories = [cat.strip().upper() for cat in response.choices[0].message.content.split(',')]
    return [cat for cat in suggested_categories if cat in categories]




@sync_to_async
def get_recent_scholarships():
    recent_time = timezone.now() - timedelta(hours=24)
    return list(ScholarshipData.objects.filter(
        datetime_created__gte=recent_time,
        category__isnull=True
    ))

@sync_to_async
def save_scholarship_categories(scholarship, categories):
    for category_name in categories:
        category = Category.objects.get(name=category_name)
        scholarship.categories.add(category)
    scholarship.save()
    

async def update_recent_scholarships():
    recent_scholarships = await get_recent_scholarships()

    for scholarship in recent_scholarships:
        details = f"Title: {scholarship.title}\nEligibility: {scholarship.eligibility}\nDocuments Needed: {scholarship.documents_needed}\nHow To Apply: {scholarship.how_to_apply}\nPublished On: {scholarship.published_on}\nState: {scholarship.state}\nDeadline: {scholarship.deadline}\nLink: {scholarship.link}"
        categories = await sync_to_async(categorize_scholarship)(details)
        
        await save_scholarship_categories(scholarship, categories)
        print(f"Updated categories for '{scholarship.title}' to '{', '.join(categories)}'")


if __name__ == "__main__":
    import asyncio 
    asyncio.run(update_recent_scholarships())
    
    