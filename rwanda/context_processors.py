from django.conf import settings
from django.utils import timezone


def base_url(request):
    return {
        'base_url': settings.BASE_URL
    }


def today(request):
    return {
        'today': timezone.now()
    }
