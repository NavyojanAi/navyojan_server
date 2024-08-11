from django.core.management.base import BaseCommand
from scripts.govt_scholarships import main
from scripts.initialize_categories import initialize_categories
import asyncio 
class Command(BaseCommand):
    help = 'Scrap and Import scholarships'

    def handle(self, *args, **options):
        try:
            self.stdout.write("Initializing categories...")
            initialize_categories()
            self.stdout.write(self.style.SUCCESS("Categories initialized successfully."))

            asyncio.run(main())
            self.stdout.write(self.style.SUCCESS(f'Successfully scraped and imported scholarships'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to import scholarships: {e}'))
            