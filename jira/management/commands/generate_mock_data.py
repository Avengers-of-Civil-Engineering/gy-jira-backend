from django.core.management.base import BaseCommand
from jira.generate_mock_data import generate_mock_data, clear_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        clear_data()
        generate_mock_data()
