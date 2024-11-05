from django.core.management import BaseCommand
from django.db import connection

from airport.management.commands._decorators import reconnect


class Command(BaseCommand):
    @reconnect(max_retries=3)
    def handle(self, *args, **options) -> None:
        try:
            connection.ensure_connection()
            self.stdout.write(
                self.style.SUCCESS("Successfully connected to database")
            )
        finally:
            connection.close()

