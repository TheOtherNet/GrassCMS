__all__=['helpers', 'models', 'objects', 'server', 'routes', 'converters']

import os, sys
encoding = sys.getfilesystemencoding()
if hasattr(sys, 'frozen'):
    data_dir = os.path.abspath(os.path.dirname(unicode(sys.executable, encoding)))
data_dir = os.path.abspath(os.path.dirname(unicode(__file__, encoding)))

class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite:////tmp/grasscms.db'
    SERVER_NAME = "grasscms.com"
    SECRET_KEY="goodscretkyehere"

class ProductionConfig(Config):
    DATABASE_URI = "mysql://root:root@localhost/grasscms"

class DevelopmentConfig(Config):
    DEBUG = True
    SERVER_NAME="grasstest.com"
    TESTING = True
