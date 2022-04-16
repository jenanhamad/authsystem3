from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Will load seed data'


    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Data was loaded'))