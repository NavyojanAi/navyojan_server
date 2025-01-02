from django.core.management.base import BaseCommand
from scripts.govt_scholarships import main
from scripts.we_make_scrap import scrape_scholarships as we_make_scrap
from scripts.initialize_categories import initialize_categories, initialize_eligibility, initialize_documents, initialize_subscription_plans
import asyncio 
# from scripts.notify_scholarships_to_users import perform as notify_scholarships_to_users
from scripts.notify_scholarships_to_users import main as notify_scholarships_to_users

from scripts.extract_details import process_user_documents
from scripts.initialize_questions import initialize_questions


class Command(BaseCommand):
    help = 'Scrap and Import scholarships'

    def handle(self, *args, **options):
        try:
            self.stdout.write("Initializing categories...")
            initialize_categories()
            self.stdout.write(self.style.SUCCESS("Categories initialized successfully."))
            
            self.stdout.write("Initializing documents...")
            initialize_documents()
            self.stdout.write(self.style.SUCCESS("Documents initialized successfully."))

            self.stdout.write("Initializing eligibility...")
            initialize_eligibility()
            self.stdout.write(self.style.SUCCESS("Eligibility initialized successfully."))

            self.stdout.write("Initializing subscription plans...")
            initialize_subscription_plans()
            self.stdout.write(self.style.SUCCESS("Subscription plans initialized successfully."))
            
            self.stdout.write("Scraping scholarships from govt_scholarships...")
            asyncio.run(main())
            self.stdout.write(self.style.SUCCESS(f'Successfully scraped and imported scholarships'))

            self.stdout.write("Scraping scholarships from we_make_scrap...")
            asyncio.run(we_make_scrap())
            
            initialize_questions()
            # self.stdout.write(self.style.SUCCESS("Questions initialized successfully."))
            # notify_scholarships_to_users()
            # process_user_documents()
            self.stdout.write(self.style.SUCCESS(f'Successfully scraped and imported scholarships'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to import scholarships: {e}'))
            