import os
from dotenv import load_dotenv
load_dotenv()

env = os.getenv('ENVIRONMENT', 'development')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'core.settings.{env}')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
