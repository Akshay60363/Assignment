"""
WSGI config for bright_credit project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bright_credit.settings')

application = get_wsgi_application()

# This is for Vercel deployment
app = application

# For vercel handler to import
def handler(request, **kwargs):
    return app(request.environ, lambda x, y: [])
