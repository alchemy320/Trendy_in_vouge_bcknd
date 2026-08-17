"""
ASGI config for trendy_in_vogue project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

sys.path.append('/home/trendy/www/Trendy_in_vouge_bcknd/Trendy_in_vouge_bcknd')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Trendy_in_vouge_bcknd.settings')
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trendy_in_vogue.settings')

application = get_asgi_application()
