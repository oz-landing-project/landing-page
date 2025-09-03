"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# app 폴더를 Python path에 추가
BASE_DIR = Path(__file__).resolve().parent.parent
app_path = BASE_DIR / 'app'
if str(app_path) not in sys.path:
    sys.path.insert(0, str(app_path))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

application = get_wsgi_application()
