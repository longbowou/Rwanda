"""
WSGI config for rwanda project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
import signal
import sys
import time
import traceback

from django.core.wsgi import WSGIHandler

sys.path.append('/var/www/clients/client1/web16/web/backend')

sys.path.append('/var/www/clients/client1/web16/web/venv/lib/python3.8/site-packages')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rwanda.settings')

try:
    application = WSGIHandler()
except Exception:
    # Error loading applications
    if 'mod_wsgi' in sys.modules:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(2.5)
