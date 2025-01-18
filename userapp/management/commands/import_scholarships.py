from django.core.management.base import BaseCommand
from tasks.daily_automation import daily_automation_task
from logs import logger
import os
import django

class Command(BaseCommand):
    help = 'Scrap and Import scholarships'

    def handle(self, *args, **options):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "navyojan.settings")
        django.setup()
        try:
            logger.info("Starting the import scholarships task...")
            self.stdout.write("Starting the import scholarships task...")
            daily_automation_task.delay()
            logger.info("Import scholarships task has been queued successfully")
            self.stdout.write(self.style.SUCCESS("Import scholarships task has been queued."))
        except Exception as e:
            logger.error(f"Failed to queue import scholarships task: {str(e)}")
            self.stdout.write(self.style.ERROR(f'Failed to queue import scholarships task: {e}'))