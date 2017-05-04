from __future__ import absolute_import, unicode_literals

from base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'yzm0q4sii0&fx%8o=+8os&sb64eqsq&#(1*5+g&^-#os9!5doe'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# try:
#     from local import *
# except ImportError:
#     pass
