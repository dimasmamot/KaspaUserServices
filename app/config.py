import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '9L1reyib-080982-qwerty'