from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.core.management import call_command
from .models import ParserSettings,MarketStat

@receiver(post_migrate)
def load_data(sender, **kwargs):
    if not ParserSettings.objects.all().exists() and  not MarketStat.objects.all().exists():
        call_command('loaddata', 'apps/parser_functions/fixtures/initial_data.json')
