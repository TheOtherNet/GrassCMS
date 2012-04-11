#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
    GrassCMS - Simple drag and drop content management system
"""
from grasscms.routes import *
from flaskext.gravatar import Gravatar

Base.metadata.create_all(bind=engine) # Create database if not done.
gravatar = Gravatar(app, # Gravatar module, 100px wide.
                size=100,
                rating='g',
                default='retro',
                force_default=False,
                force_lower=False)

"""
    TODO LIST:
        - All images can be accesible (and overwritten) by other users
        - Delete stuff
        - AJAXIZE stuff
"""

def server():
    """ Main server, will allow us to make it wsgi'able """
    app.config['STATIC_ROOT'] = 'http://grasstest.com/static/'
    app.config['SERVER_NAME'] = "grasstest.com"
    app.run(host='0.0.0.0', port=80) # Running on port 80 in all interfaces.

