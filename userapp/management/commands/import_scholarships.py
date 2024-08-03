import json
from django.core.management.base import BaseCommand
from userapp.models import ScholarshipData
from scripts.govt_scholarships import main
import asyncio 


class Command(BaseCommand):
    help = 'Scrap and Import scholarships'

    def handle(self, *args, **options):
        try:
            asyncio.run(main())
            
            # with open('scripts/scholarships2.json', 'r', encoding='utf-8') as file:
            #     scholarships = json.load(file)


            # for scholarship in scholarships:
            #     ScholarshipData.objects.get_or_create(
            #         title=scholarship["name"],
            #         eligibility=scholarship.get('Eligibility', ''),
            #         # amount=scholarship.get('Amount', '0'),
            #         documents_needed=scholarship.get('Documents Needed', ''),
            #         how_to_apply=scholarship.get('How To Apply', ''),
            #         published_on=scholarship.get('Published on', ''),
            #         state = scholarship.get('State', ''),
            #         deadline=scholarship.get('Application Deadline', ''),
            #         link=scholarship.get('Official Link', ''),
            #         category=scholarship.get('Category', '')
            #     )

            self.stdout.write(self.style.SUCCESS(f'Successfully scraped and imported scholarships'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to import scholarships: {e}'))
            