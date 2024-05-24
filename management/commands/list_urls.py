from django.core.management.base import BaseCommand
from django.urls import get_resolver, URLPattern, URLResolver

def list_urls(lis, acc=None):
    if acc is None:
        acc = []
    if not lis:
        return
    for x in lis:
        if isinstance(x, URLPattern):
            acc.append(x.pattern._route)
        elif isinstance(x, URLResolver):
            list_urls(x.url_patterns, acc)
    return acc

class Command(BaseCommand):
    help = 'List all registered URLs'

    def handle(self, *args, **kwargs):
        url_patterns = get_resolver().url_patterns
        urls = list_urls(url_patterns)
        for url in urls:
            self.stdout.write(str(url))
