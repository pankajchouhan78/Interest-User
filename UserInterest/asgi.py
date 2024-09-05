import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from interest_app.routing import websocket_urlpatterns

# Set the default Django settings module for the 'django' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UserInterest.settings')

# Get the ASGI application for the Django project.
django_asgi_app = get_asgi_application()

# Define the ASGI application.
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
