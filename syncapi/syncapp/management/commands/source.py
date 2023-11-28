from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Your custom source command'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Successfully')

