import os

from dotenv import load_dotenv

from conf import settings_base

load_dotenv()

for setting in dir(settings_base):
    if setting == setting.upper():
        globals()[setting] = getattr(settings_base, setting)


ALLOWED_HOSTS = ["*"]
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
