import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testdav.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()