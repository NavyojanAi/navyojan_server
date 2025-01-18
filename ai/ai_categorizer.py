from ai.config import OPEN_AI_KEY
import os
import django
from openai import OpenAI
from django.utils import timezone
from datetime import timedelta
from userapp.models.scholarships import ScholarshipData, Category
from asgiref.sync import sync_to_async
from logs import logger

# Initialize OpenAI client with environment variable
client = OpenAI(api_key=OPEN_AI_KEY)

def setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "navyojan.settings")
    django.setup()

def categorize_scholarship(details):
    logger.info("Starting scholarship categorization")
    categories = list(Category.objects.values_list('name', flat=True))
    
    prompt = f"Categorize the following scholarship into one or more of these categories: {', '.join(categories)}. Respond with only the category names, separated by commas if there are multiple categories.\n\nScholarship Details: {details}\n\nCategories:"

    response = client.chat.completions.create(
        model = "gpt-4o",
        messages = [
            {"role": "user", "content": prompt}
        ]
    )
    
    suggested_categories = [cat.strip().upper() for cat in response.choices[0].message.content.split(',')]
    filtered_categories = [cat for cat in suggested_categories if cat in categories]
    logger.info(f"Successfully categorized scholarship. Suggested categories: {filtered_categories}")
    return filtered_categories

@sync_to_async
def get_recent_scholarships():
    logger.info("Fetching recent scholarships")
    recent_time = timezone.now() - timedelta(hours=24)
    scholarships = list(ScholarshipData.objects.filter(
        datetime_created__gte=recent_time,
        category__isnull=True
    ))
    logger.info(f"Found {len(scholarships)} recent scholarships needing categorization")
    return scholarships

@sync_to_async
def save_scholarship_categories(scholarship, categories):
    for category_name in categories:
        category = Category.objects.get(name=category_name)
        scholarship.categories.add(category)
    scholarship.save()
    logger.info(f"Saved categories for scholarship: {scholarship.title}")

async def update_recent_scholarships():
    logger.info("Starting update of recent scholarships")
    recent_scholarships = await get_recent_scholarships()

    for scholarship in recent_scholarships:
        logger.info(f"Processing scholarship: {scholarship.title}")
        details = f"Title: {scholarship.title}\nEligibility: {scholarship.eligibility}\nDocuments Needed: {scholarship.document_needed}\nHow To Apply: {scholarship.how_to_apply}\nPublished On: {scholarship.published_on}\nState: {scholarship.state}\nDeadline: {scholarship.deadline}\nLink: {scholarship.link}"
        categories = await sync_to_async(categorize_scholarship)(details)
        
        await save_scholarship_categories(scholarship, categories)
        print(f"Updated categories for '{scholarship.title}' to '{', '.join(categories)}'")

if __name__ == "__main__":
    import asyncio 
    # setup_django()
    logger.info("Starting scholarship categorization script")
    asyncio.run(update_recent_scholarships())
    logger.info("Completed scholarship categorization script")