import os
os.environ['grasscms_config'] = '/var/www/grasscms.com/application.cfg'
from grasscms.server import app as application
