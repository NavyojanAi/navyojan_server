from django.core.management.base import BaseCommand
from scripts.govt_scholarships import main
import asyncio 
class Command(BaseCommand):
    help = 'Scrap and Import scholarships'

    def handle(self, *args, **options):
        try:
            asyncio.run(main())
            self.stdout.write(self.style.SUCCESS(f'Successfully scraped and imported scholarships'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to import scholarships: {e}'))
            