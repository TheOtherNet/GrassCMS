#!/usr/bin/python
from flup.server.fcgi import WSGIServer
from grasscms.server import app
from werkzeug.contrib.fixers import LighttpdCGIRootFix
import os
os.environ['grasscms_config'] = '/var/www/grasscms.com/application.cfg'

if __name__ == '__main__':
    WSGIServer(LighttpdCGIRootFix(app)).run()

