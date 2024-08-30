from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup
import os
import django
from userapp.models.scholarships import ScholarshipData
from ai.ai_categorizer import update_recent_scholarships
from ai.ai_categorizer import categorize_scholarship

from datetime import datetime
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from asgiref.sync import sync_to_async
from userapp.models.scholarships import Category
import re 



# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "navyojan.settings")
django.setup()






# Base URL for scraping list of scholarships
base_url = "https://www.scholarshipforme.com/scholarships?state=&qualification=&category=&availability=&origin=&type=&page={}&is_item=true"

# List to store the scraped data
scholarship_list = []

# Function to scrape a single page
def scrape_page(page_number):
    url = base_url.format(page_number)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all div elements with the class name "job-content"
    job_content_divs = soup.find_all("div", class_="job-content")

    # Extract the text of the anchor tag inside the h4 tag
    for div in job_content_divs:
        if len(scholarship_list) >= 15:  # Limiting to 10 scholarships     #Remove this line to scrape all scholarships
            break                                                         #Remove this line to scrape all scholarships                                       
        h4_tag = div.find("h4")
        if h4_tag and h4_tag.find("a"):
            anchor_tag = h4_tag.find("a")
            scholarship_list.append(anchor_tag.text)

# Paginate through the pages to scrape all scholarship names
def get_scholarship_list():
    global scholarship_list
    page_number = 1
    while len(scholarship_list) < 15:                            #len(scholarship_list) < 5:           #True   (Change this line to 'True' scrape all scholarships)
        print(f"Scraping page {page_number}...")
        initial_len = len(scholarship_list)
        scrape_page(page_number)

        # Check if new data was added, if not, break the loop
        if len(scholarship_list) == initial_len:
            break

        page_number += 1

    # Ensure only 25 scholarships are being processed
    scholarship_list = scholarship_list[:15]      #Remove this line to scrape all scholarships

    # Format the list by removing ',' and ';', replacing spaces with hyphens, and converting to lowercase
    formatted_list = [
        name.replace(",", "")
        .replace(";", "")
        .replace("(", "")
        .replace(")", "")
        .replace("'", " ")
        .replace(" ", "-")
        .lower()
        for name in scholarship_list
    ]

    return formatted_list

# Base URL for individual scholarship details
detail_base_url = "https://www.scholarshipforme.com/scholarships/"

# Define the expected fields
fields = [
    "name", "Scholarship Details", "Award", "Eligibility", "Documents Needed",
    "Provider", "How To Apply", "Published on", "Status", "Type",
    "State", "Gender", "Amount", "Application Deadline", "Official Link"
]

from dateutil import parser as date_parser

@sync_to_async
def save_scholarship(name, details):
    def parse_date(date_string):
        if not date_string:
            return None 
        if date_string.lower() == "always open":
            return None
        try:
            return date_parser.parse(date_string).date()
        except ValueError:
            print(f"Unable to parse date: {date_string}")
            return None

    def validate_url(url_string):
        if not url_string:
            return None
        try:
            URLValidator()(url_string)
            return url_string
        except ValidationError:
            return None
        
    def extract_amount(amount_string):
        numbers = re.findall(r'\d+', amount_string)
        if numbers:
            return max(int(num) for num in numbers)
        return None


    required_fields = [
        'title',
        'eligibility',
        'document_needed',
        'how_to_apply',
        'amount',
        'published_on',
        'state',
        'deadline',
        # 'link',
    ]

    scholarship_data = {
        'title': name,
        'eligibility': details.get('Eligibility', '').strip().split('\n'),
        'document_needed': details.get('Documents Needed', '').strip().split('\n'),
        'how_to_apply': details.get('How To Apply', '').strip().split('\n'),
        'amount': extract_amount(details.get('Amount', '')),
        'published_on': parse_date(details.get('Published on', '')),
        'state': details.get('State', ''),
        'deadline': parse_date(details.get('Application Deadline', '')),
        'link': validate_url(details.get('Official Link', '')),
    }
    
    scholarship_data['eligibility'] = [
    item.strip() for item in scholarship_data['eligibility'] if item.strip()]

    scholarship_data['document_needed'] = [
    item.strip() for item in scholarship_data['document_needed'] if item.strip()]
    
    scholarship_data['how_to_apply'] = [
    item.strip() for item in scholarship_data['how_to_apply'] if item.strip()]

    # Check if all required fields have valid data
    if all(scholarship_data.get(field) for field in required_fields):
        scholarship = ScholarshipData(**scholarship_data)
        scholarship.save()        
        
        categories = categorize_scholarship(details)
        for category_name in categories:
            category, created = Category.objects.get_or_create(name=category_name)
            scholarship.categories.add(category)
        
        print(f"Saved and categorized scholarship: {name}")
        
    else:
        missing_fields = [field for field in required_fields if not scholarship_data.get(field)]
        print(f"Skipping scholarship '{name}' due to missing required fields: {', '.join(missing_fields)}")



# Function to scrape details of a single scholarship
async def scrape_scholarship_details(page, endpoint):
    url = detail_base_url + endpoint
    print(f"Scraping details from {url}...")
    
    
    await page.goto(url)
    await page.wait_for_load_state("networkidle")

    # details = {field: "" for field in fields}
    name = endpoint.replace("-", " ").title()
    details = {field: "" for field in fields}

    try:
        job_details_body = await page.query_selector(".job-details-body")
        if job_details_body:
            elements = await job_details_body.query_selector_all("h6, p, ul")
            current_section = None
            for elem in elements:
                tag_name = await elem.evaluate("el => el.tagName.toLowerCase()")
                if tag_name == "h6":
                    current_section = await elem.inner_text()
                elif tag_name in ["p", "ul"]:
                    if current_section in details:
                        details[current_section] += await elem.inner_text() + " "

        # Clean up the details
        for key in details:
            details[key] = details[key].strip()

        # Scrape additional details from the job overview list
        job_overview = await page.query_selector(".job-overview")
        if job_overview:
            li_elements = await job_overview.query_selector_all("li")
            for li in li_elements:
                text = await li.inner_text()
                if ":" in text:
                    label, value = text.split(":", 1)
                    label = label.strip()
                    value = value.strip()
                    if label in details:
                        details[label] = value
        
        await save_scholarship(name, details)
        
        print(f"Saved scholarship: {name}")
    except Exception as e:
        print(f"Error scraping {url}: {e}")

    return details



async def main():
    formatted_list = get_scholarship_list()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # new_scholarships = []
        for endpoint in formatted_list:
            name = endpoint.replace("-", " ").title()
            if not await sync_to_async(ScholarshipData.objects.filter(title=name).exists)():
                await scrape_scholarship_details(page, endpoint)
            else:
                print(f"Scholarship {name} already exists. Skipping.")

        await browser.close()
        
    print("Scrapping Completed.")
