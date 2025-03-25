from bright_credit.wsgi import application

# This is the handler that Vercel uses for serverless functions
def handler(request, **kwargs):
    return application(request.environ, lambda x, y: []) 