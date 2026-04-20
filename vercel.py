# Vercel ASGI handler
# This file is required for Vercel to recognize the Python app

from api.index import app

def handler(request, context):
    """Vercel serverless handler."""
    from fastapi import Request
    from starlette.middleware.asgi import ASGIApp
    
    asgi_app = ASGIApp(app)
    return asgi_app(request, context)