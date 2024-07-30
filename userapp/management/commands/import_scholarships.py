import json
from django.core.management.base import BaseCommand
from userapp.models import ScholarshipData

class Command(BaseCommand):
    help = 'Import scholarships from JSON file'

    def handle(self, *args, **options):
        try:
            with open('scripts/scholarships2.json', 'r', encoding='utf-8') as file:
                scholarships = json.load(file)

            for scholarship in scholarships:
                ScholarshipData.objects.create(
                    title=scholarship['name'],
                    description=scholarship.get('Scholarship Details', ''),
                    eligibility=scholarship.get('Eligibility', ''),
                    amount=scholarship.get('Amount', '0'),
                    deadline=scholarship.get('Application Deadline', ''),
                    link=scholarship.get('Official Link', '')
                )

            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(scholarships)} scholarships'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to import scholarships: {e}'))
            