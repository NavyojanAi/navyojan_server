from celery import shared_task

from logs import logger
from scripts.govt_scholarships import main as govt_scholarships_main
from scripts.we_make_scrap import scrape_scholarships as we_make_scrap
from scripts.initialize_categories import (
    initialize_categories,
    initialize_eligibility,
    initialize_documents,
    initialize_subscription_plans,
)
from scripts.initialize_questions import initialize_questions
from scripts.notify_scholarships_to_users import perform as notify_scholarships_to_users
from scripts.extract_details import process_user_documents

@shared_task(name="initialize-categories")
def initialize_categories_task():
    logger.info("Initializing categories...")
    initialize_categories()
    logger.info("Categories initialized successfully.")

@shared_task(name="initialize-documents")
def initialize_documents_task():
    logger.info("Initializing documents...")
    initialize_documents()
    logger.info("Documents initialized successfully.")

@shared_task(name="initialize-eligibility")
def initialize_eligibility_task():
    logger.info("Initializing eligibility...")
    initialize_eligibility()
    logger.info("Eligibility initialized successfully.")

@shared_task(name="initialize-subscription-plans")
def initialize_subscription_plans_task():
    logger.info("Initializing subscription plans...")
    initialize_subscription_plans()
    logger.info("Subscription plans initialized successfully.")

@shared_task(name="scrape-govt-scholarships")
def scrape_govt_scholarships_task():
    logger.info("Scraping scholarships from govt_scholarships...")
    govt_scholarships_main()
    logger.info("Successfully scraped and imported scholarships from govt_scholarships.")

@shared_task(name="scrape-we-make-scrap")
def scrape_we_make_scrap_task():
    logger.info("Scraping scholarships from we_make_scrap...")
    we_make_scrap()
    logger.info("Successfully scraped and imported scholarships from we_make_scrap.")

@shared_task(name="notify-scholarships-to-users")
def notify_scholarships_to_users_task():
    logger.info("Notifying scholarships to users...")
    notify_scholarships_to_users()
    logger.info("Successfully notified scholarships to users.")

@shared_task(name="process-user-documents")
def process_user_documents_task():
    logger.info("Processing user documents...")
    process_user_documents()
    logger.info("Successfully processed user documents.")

@shared_task(name="automation-task")
def daily_automation_task():
    try:
        initialize_categories_task.delay()
        initialize_documents_task.delay()
        initialize_eligibility_task.delay()
        initialize_subscription_plans_task.delay()
        scrape_govt_scholarships_task.delay()
        scrape_we_make_scrap_task.delay()
        notify_scholarships_to_users_task.delay()
        process_user_documents_task.delay()
    except Exception as e:
        logger.error(f"Failed to import scholarships: {e}") 