from config import OPEN_AI_KEY
import os
import django
from openai import OpenAI
from django.utils import timezone
from datetime import timedelta
from userapp.models.scholarships import ScholarshipData,Category

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "navyojan.settings")
django.setup()



# Initialize OpenAI client
client = OpenAI(api_key=OPEN_AI_KEY)

def categorize_scholarship(details):
    categories = Category.objects.values_list('name', flat=True)
    
    prompt = f"Categorize the following scholarship into the following categories(give only the word) and give 'none' in case of not finding any relevancy: {', '.join(categories).lower()}.\n\nDetails: {details}\n\nCategory:"

    response = client.chat.completions.create(
        model = "gpt-4o",
        messages = [
            {"role": "user", "content": prompt}
        ]
    )
            
    category = response.choices[0].message.content.strip()
    return category if category in categories else "NONE"


def update_recent_scholarships():
    # Get scholarships added in the last 24 hours with empty category
    recent_time = timezone.now() - timedelta(hours=24)
    recent_scholarships = ScholarshipData.objects.filter(
        datetime_created__gte=recent_time,
        category__isnull=True
    )

    for scholarship in recent_scholarships:
        details = f"Title: {scholarship.title}\nEligibility: {scholarship.eligibility}\nDocuments Needed: {scholarship.document_needed}\nHow To Apply: {scholarship.how_to_apply}\nPublished On: {scholarship.published_on}\nState: {scholarship.state}\nDeadline: {scholarship.deadline}\nLink: {scholarship.link}"
        category = categorize_scholarship(details)
        
        scholarship.category = category
        scholarship.save()
        print(f"Updated category for '{scholarship.title}' to '{category}'")

if __name__ == "__main__":
    update_recent_scholarships()