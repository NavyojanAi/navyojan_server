import asyncio
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup
import json
import os
from openai import OpenAI 
# from config import OPEN_AI_KEY
import django
from userapp.models.scholarships import ScholarshipData
from ai.ai_categorizer import update_recent_scholarships

from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


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
        if len(scholarship_list) >= 5:  # Limiting to 10 scholarships
            break 
        h4_tag = div.find("h4")
        if h4_tag and h4_tag.find("a"):
            anchor_tag = h4_tag.find("a")
            scholarship_list.append(anchor_tag.text)

# Paginate through the pages to scrape all scholarship names
def get_scholarship_list():
    global scholarship_list
    page_number = 1
    while len(scholarship_list) < 5:
        print(f"Scraping page {page_number}...")
        initial_len = len(scholarship_list)
        scrape_page(page_number)

        # Check if new data was added, if not, break the loop
        if len(scholarship_list) == initial_len:
            break

        page_number += 1

    # Ensure only 25 scholarships are being processed
    scholarship_list = scholarship_list[:5]

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
    "Provider", "How To Apply", "Published on", "Status", "Category", "Type",
    "State", "Gender", "Amount", "Application Deadline", "Official Link"
]

# Function to scrape details of a single scholarship
async def scrape_scholarship_details(page, endpoint):
    url = detail_base_url + endpoint
    print(f"Scraping details from {url}...")
    
    
    # if ScholarshipData.objects.filter(title=name).exists():
    #     print(f"Scholarship {name} already exists. Skipping.")
    #     return
    
    
    await page.goto(url)
    await page.wait_for_load_state("networkidle")

    # details = {field: "" for field in fields}
    name = endpoint.replace("-", " ").title()

    try:
        job_details_body = await page.query_selector(".job-details-body")
        if job_details_body:
            elements = await job_details_body.query_selector_all("h6, p, ul")
            details = {field: "" for field in fields}
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
                        
        def parse_date(date_string):
            try:
                return datetime.strptime(date_string.strip(), "%B %d, %Y").date()
            except ValueError:
                return None


        # Helper function to validate URL
        def validate_url(url_string):
            try:
                URLValidator()(url_string)
                return url_string
            except ValidationError:
                return None
            
                        
        scholarship = ScholarshipData(
            title = name,
            eligibility = details.get('Eligibility', ''),
            documents_needed = details.get('Documents Needed', ''),
            how_to_apply = details.get('How To Apply', ''),
            published_on = parse_date(details.get('Published on', '')),
            state = details.get('State', ''),
            deadline = parse_date(details.get('Application Deadline', '')),
            link = validate_url(details.get('Official Link', '')),
            category = details.get('Category', '')
        )
        scholarship.save()
        print(f"Saved scholarship: {name}")
    except Exception as e:
        print(f"Error scraping {url}: {e}")

    


# Function to load existing data from JSON file
def load_existing_data():
    if os.path.exists("navyojan/scripts/scholarships2.json"):
        with open("navyojan/scripts/scholarships2.json", "r", encoding="utf-8") as json_file:
            return json.load(json_file)
    return []

# Function to save data to JSON file
def save_data(data):
    with open("navyojan/scripts/scholarships2.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=2, ensure_ascii=False)

async def main():
    # existing_data = load_existing_data()
    # existing_names = set(scholarship["name"] for scholarship in existing_data)


    formatted_list = get_scholarship_list()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # new_scholarships = []
        for endpoint in formatted_list:
            name = endpoint.replace("-", " ").title()
            if not ScholarshipData.objects.filter(title=name).exists():
                await scrape_scholarship_details(page, endpoint)
            else:
                print(f"Scholarship {name} already exists. Skipping.")

        await browser.close()
        
    print("Scrapping Completed.")

    update_recent_scholarships()
    print("Categorization Completed.")


    # Combine existing data with new scholarships
    # updated_data = existing_data + new_scholarships

    # # Write updated JSON to file
    # if new_scholarships:
    #     save_data(updated_data)
    #     print(f"Scraping complete. Added {len(new_scholarships)} new scholarships to 'scholarships2.json'")
    # else:
    #     print("No new scholarships found. JSON file remains unchanged.")




# asyncio.run(main())