import os

import psycopg
from django.core.management import BaseCommand

from airport.management.commands._decorators import reconnect


class Command(BaseCommand):
    @reconnect(max_retries=3)
    def handle(self, *args, **options) -> None:
        connection = None
        try:
            connection = psycopg.connect(
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host=os.getenv("POSTGRES_HOST"),
                port=os.getenv("POSTGRES_PORT")
            )
            self.stdout.write(
                self.style.SUCCESS("Successfully connected to database")
            )
        finally:
            if connection:
                connection.close()

