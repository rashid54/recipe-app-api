import time
from django.db import connections
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError


class Command(BaseCommand):
    """command to pause executions untill database is available"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']  # for testing
                # db_conn = connections['default'].cursor()  # for release
            except OperationalError:
                self.stdout.write('Database unavailable,waiting for 1 second')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available'))
