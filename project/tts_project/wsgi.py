"""
WSGI config for TTS project.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tts_project.settings')

application = get_wsgi_application()

