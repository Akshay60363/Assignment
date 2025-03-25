import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bright_credit.settings')
application = get_wsgi_application()

def handler(request, **kwargs):
    return application(request.environ, lambda status, headers: [])

app = application 