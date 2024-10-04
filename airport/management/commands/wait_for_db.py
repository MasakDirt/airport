import os

import psycopg2
from django.core.management import BaseCommand

from airport.management.commands._decorators import reconnect


class Command(BaseCommand):
    @reconnect(max_retries=3)
    def handle(self, *args, **options) -> None:
        connection = None
        try:
            connection = psycopg2.connect(
                database=os.environ["POSTGRES_DB"],
                user=os.environ["POSTGRES_USER"],
                password=os.environ["POSTGRES_PASSWORD"],
                host=os.environ["POSTGRES_HOST"],
            )
            self.stdout.write(
                self.style.SUCCESS("Successfully connected to database")
            )
        finally:
            if connection:
                connection.close()

