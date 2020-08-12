import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "b'\x927O\x7f\xcc\xd4\xaf*\xa2\x8e\xef\x0b\xc8\xe2\x1ez'"
    MONGODB_SETTINGS = {'db':'Blog'}
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME =  os.environ.get('EMAIL_USER') #'rakesh1432rakei@gmail.com'
    MAIL_PASSWORD =  os.environ.get('EMAIL_PASS') #'8610869807'