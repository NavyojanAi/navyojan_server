from django.core.management.base import BaseCommand
from scripts.notify_scholarships_to_users import perform
import asyncio 


class Command(BaseCommand):
    help = 'Apply scholarships'

    def handle(self, *args, **options):
        try:
            # perform.delay()
            asyncio.run(perform())
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to auto apply scholarships: {e}'))
            