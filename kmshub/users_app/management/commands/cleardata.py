# In your app directory (e.g., myapp/management/commands/cleardata.py)
from django.core.management.base import BaseCommand
from users_app.models import Resources


class Command(BaseCommand):
    help = "Clears all data from the specified table"

    def handle(self, *args, **kwargs):
        Resources.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS("Data cleared successfully from Resources table")
        )
