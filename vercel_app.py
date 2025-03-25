import os
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse
from django.urls import path
from django.core.handlers.wsgi import WSGIHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bright_credit.settings')
application = get_wsgi_application()

def handler(request, **kwargs):
    # Get the path from the request
    path = request.get('path', '')
    
    # Handle static files
    if path.startswith('/static/'):
        return {
            'statusCode': 404,
            'body': 'Not Found'
        }
    
    # Create WSGI environment
    environ = {
        'REQUEST_METHOD': request.get('method', 'GET'),
        'PATH_INFO': path,
        'QUERY_STRING': request.get('query', {}),
        'wsgi.input': request.get('body', ''),
        'wsgi.errors': [],
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input_terminated': True,
        'SERVER_NAME': request.get('headers', {}).get('host', ''),
        'SERVER_PORT': '443',
        'HTTP_HOST': request.get('headers', {}).get('host', ''),
        'HTTP_USER_AGENT': request.get('headers', {}).get('user-agent', ''),
        'HTTP_ACCEPT': request.get('headers', {}).get('accept', '*/*'),
        'HTTP_ACCEPT_LANGUAGE': request.get('headers', {}).get('accept-language', ''),
        'HTTP_ACCEPT_ENCODING': request.get('headers', {}).get('accept-encoding', ''),
        'HTTP_CONNECTION': request.get('headers', {}).get('connection', ''),
        'HTTP_UPGRADE_INSECURE_REQUESTS': request.get('headers', {}).get('upgrade-insecure-requests', ''),
        'HTTP_SEC_FETCH_DEST': request.get('headers', {}).get('sec-fetch-dest', ''),
        'HTTP_SEC_FETCH_MODE': request.get('headers', {}).get('sec-fetch-mode', ''),
        'HTTP_SEC_FETCH_SITE': request.get('headers', {}).get('sec-fetch-site', ''),
        'HTTP_SEC_FETCH_USER': request.get('headers', {}).get('sec-fetch-user', ''),
        'HTTP_CACHE_CONTROL': request.get('headers', {}).get('cache-control', ''),
    }
    
    # Add headers from the request
    for key, value in request.get('headers', {}).items():
        environ[f'HTTP_{key.upper().replace("-", "_")}'] = value
    
    # Call the WSGI application
    try:
        response = application(environ, lambda status, headers: [])
        return {
            'statusCode': int(status.split()[0]),
            'headers': dict(headers),
            'body': response[0].decode('utf-8') if response else ''
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }

app = application 