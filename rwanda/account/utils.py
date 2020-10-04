import os

from django.conf import settings


def natural_size(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def create_folder_if_not_exits(folder):
    if not os.path.exists(os.path.join(settings.BASE_DIR, "media", folder)):
        os.makedirs(os.path.join(settings.BASE_DIR, "media", folder))
