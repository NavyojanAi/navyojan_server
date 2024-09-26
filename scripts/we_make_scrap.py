import asyncio
from playwright.async_api import async_playwright
import json
import re
from dateutil import parser as date_parser
from openai import OpenAI
from ai.config import OPEN_AI_KEY
import os
import django
from ai.ai_categorizer import categorize_scholarship

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "navyojan.settings")
django.setup()

from userapp.models.scholarships import ScholarshipData, Category, Eligibility, Documents
from django.db import transaction
from asgiref.sync import sync_to_async

base_url = "https://www.wemakescholars.com/other/government-of-india/scholarships"

client = OpenAI(api_key=OPEN_AI_KEY)

def extract_sections(content):
    sections = {
        "Eligibility": "",
        "Application Process": "",
        "Documents": ""
    }
    
    eligibility_start = content.find("Eligibility Criteria")
    application_start = content.find("Application Process:")
    documents_start = content.find("Documents:")
    
    if eligibility_start != -1:
        eligibility_end = min(x for x in [application_start, documents_start] if x != -1)
        sections["Eligibility"] = content[eligibility_start:eligibility_end].strip()
    
    if application_start != -1:
        application_end = documents_start if documents_start != -1 else len(content)
        sections["Application Process"] = content[application_start:application_end].strip()
    
    if documents_start != -1:
        sections["Documents"] = content[documents_start:].strip()
    
    for key in sections:
        sections[key] = re.sub(f"{key}.*?:", "", sections[key], flags=re.IGNORECASE).strip()
        sections[key] = [item.strip() for item in re.split(r'\n+', sections[key]) if item.strip()]
    
    return sections


def parse_date(date_string):
        if not date_string:
            return None 
        if date_string.lower() == "Deadline varies":
            return None
        try:
            return date_parser.parse(date_string).date()
        except ValueError:
            print(f"Unable to parse date: {date_string}")
            return None



async def categorize_with_gpt(text, category_type, predefined_keys):
    keys_str = ", ".join(predefined_keys)
    prompt = f"""
    Given the following {category_type} information, categorize it into key-value pairs. 
    Use ONLY the following predefined keys: {keys_str}
    If a piece of information doesn't match any key, skip it.

    Information:
    {text}

    Output format: JSON with only the predefined keys used.
    """
    # response = await sync_to_async(client.chat.completions.create)(
    #     model="gpt-4o-mini",
    #     messages=[
    #         {"role": "system", "content": "You are a helpful assistant that categorizes scholarship information."},
    #         {"role": "user", "content": prompt}
    #     ]
    # )
    
    # return response.choices[0].message.content
    
    try:
        response = await sync_to_async(client.chat.completions.create)(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that categorizes scholarship information using only predefined keys."},
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.choices[0].message.content.strip()
        
        if not content:
            print(f"Empty response from GPT for {category_type}")
            return "{}"
        
        # Remove Markdown code block syntax if present
        content = re.sub(r'^```json\s*|\s*```$', '', content, flags=re.MULTILINE)
        
        # Try to parse the JSON response
        try:
            parsed_json = json.loads(content)
            return json.dumps(parsed_json)  # Ensure it's a valid JSON string
        except json.JSONDecodeError:
            print(f"Invalid JSON response from GPT for {category_type}: {content}")
            # Attempt to clean and fix the JSON
            cleaned_content = content.replace("'", '"').replace("\n", "")
            try:
                parsed_json = json.loads(cleaned_content)
                return json.dumps(parsed_json)
            except json.JSONDecodeError:
                print(f"Failed to clean and parse JSON for {category_type}")
                return "{}"
    except Exception as e:
        print(f"Error in categorize_with_gpt for {category_type}: {str(e)}")
        return "{}"
@sync_to_async
@transaction.atomic
def save_scholarship(details):
    scholarship = ScholarshipData(
        title=details["Title"],
        amount=int(re.sub(r'[^\d]', '', details["Scholarship value"])) if details["Scholarship value"] else None,
        published_on=parse_date(details["Deadline"]),  # Assuming "Deadline" is equivalent to "published_on"
        deadline=parse_date(details["Deadline"]),
        link=details["Apply Now Link"],
        is_approved=True
    )
    scholarship.save()

    try:
        # Process eligibility
        eligibility_data = json.loads(details["categorized_eligibility"])
        for key, value in eligibility_data.items():
            eligibility, created = Eligibility.objects.get_or_create(name=key)
            scholarship.eligibility.add(eligibility)

        # Process documents
        document_data = json.loads(details["categorized_documents"])
        for key, value in document_data.items():
            document, created = Documents.objects.get_or_create(name=key)
            scholarship.document_needed.add(document)

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for scholarship {details['Title']}: {str(e)}")
        print(f"Eligibility data: {details['categorized_eligibility']}")
        print(f"Document data: {details['categorized_documents']}")
    except Exception as e:
        print(f"Unexpected error processing scholarship {details['Title']}: {str(e)}")

    # Process how to apply
    scholarship.how_to_apply = details["Application Process"]

    # Categorize scholarship
    categories = categorize_scholarship(details)
    for category_name in categories:
        category, created = Category.objects.get_or_create(name=category_name)
        scholarship.categories.add(category)

    scholarship.save()
    print(f"Saved and categorized scholarship: {scholarship.title}")

async def scrape_scholarship_details(page, url, eligibility_keys, document_keys):
    await page.goto(url)
    await page.wait_for_load_state("networkidle")

    details = {
        "Title": "",
        "Degree": "",
        "Deadline": "",
        "Scholarship value": "",
        "Provided by": "",
        "Eligibility": [],
        "Application Process": [],
        "Documents": [],
        "Apply Now Link": ""
    }

    try:
        print(f"Scraping URL: {url}")

        eligibility_selectors = [
            'div.editor:has-text("Eligibility Criteria")'
        ]
        
        #extract title
        title_selector = 'h1.clrwms.fw4.font18'
        title_element = await page.query_selector(title_selector)
        if title_element:
            details["Title"] = await title_element.inner_text()
        
        #extract details like degree, deadline, scholarship value, provided by
        row_mb10_selector = 'div.row.mb10'
        row_mb10_element = await page.query_selector(row_mb10_selector)
        if row_mb10_element:
            list_items = await row_mb10_element.query_selector_all('li')
            for item in list_items:
                text = await item.inner_text()
                if "Degree:" in text:
                    details["Degree"] = text.split("Degree:")[1].strip()
                elif "Deadline:" in text:
                    details["Deadline"] = (text.split("Deadline:")[1].strip())
                elif "Scholarship value:" in text:
                    details["Scholarship value"] = text.split("Scholarship value:")[1].strip()
                elif "Provided by:" in text:
                    details["Provided by"] = text.split("Provided by:")[1].strip()
        
        #extract apply now link
        apply_now_selector = 'a.btn.btn-new.width100p.font14.pull-right.scholarship-applied'
        apply_now_element = await page.query_selector(apply_now_selector)
        if apply_now_element:
            apply_now_link = await apply_now_element.get_attribute('href')
            details["Apply Now Link"] = apply_now_link if apply_now_link else ""

        #extract eligibility, application process and documents
        all_content = ""
        for selector in eligibility_selectors:  
            # for selector in selectors:
            element = await page.query_selector(selector)
            if element:
                    all_content = await element.inner_text()
                    print(f"Found using selector: {selector}")
                    break

        if not all_content:
            print("No specific elements found. Grabbing all content.")
            main_content = await page.query_selector('div.editor')
            if main_content:
                all_content = await main_content.inner_text()

        # Extract sections from the scraped content
        extracted_sections = extract_sections(all_content)
        details.update(extracted_sections)

        # Use GPT to categorize eligibility and documents with predefined keys
        details["categorized_eligibility"] = await categorize_with_gpt("\n".join(details["Eligibility"]), "eligibility", eligibility_keys)
        details["categorized_documents"] = await categorize_with_gpt("\n".join(details["Documents"]), "documents", document_keys)

        await save_scholarship(details)

    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        # You might want to log the full traceback for debugging
        import traceback
        print(traceback.format_exc())

    return details




async def scrape_scholarships():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  
        page = await browser.new_page()
        await page.goto(base_url)
        
        # scholarships = []
        limit = 5
        
        eligibility_keys, document_keys = await get_predefined_keys()
        
        for i in range(0, limit, 2):
            try:
                view_apply_buttons = await page.query_selector_all('a[href*="/scholarship/"]')
                if i >= len(view_apply_buttons):
                    break

                await view_apply_buttons[i].click()
                await page.wait_for_load_state('networkidle')

                # details = await scrape_scholarship_details(page, page.url)
                # scholarships.append(details)
                await scrape_scholarship_details(page, page.url, eligibility_keys, document_keys)
               
                await page.go_back()
                await page.wait_for_load_state('networkidle')

            except Exception as e:
                print(f"Error navigating scholarship {i}: {e}")
        
        await browser.close()

        # with open("scholarships_wemakescholars23.json", "w", encoding="utf-8") as f:
        #     json.dump(scholarships, f, indent=2)
    # print("Data saved to scholarships_wemakescholars23.json")
        print("Scraping completed and data saved to the database.")


if __name__ == "__main__":
    asyncio.run(scrape_scholarships())

@sync_to_async
def get_predefined_keys():
    eligibility_keys = list(Eligibility.objects.values_list('name', flat=True))
    document_keys = list(Documents.objects.values_list('name', flat=True))
    return eligibility_keys, document_keys