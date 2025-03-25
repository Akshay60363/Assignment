from api.wsgi_handler import handler

def lambda_handler(event, context):
    """Entry point for the Lambda function."""
    return handler(event, context) 