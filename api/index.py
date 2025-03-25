from api.wsgi_handler import handler

def lambda_handler(event, context):
    return handler(event, context) 