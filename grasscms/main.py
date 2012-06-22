from sqlalchemy import create_engine, ForeignKey, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, render_template, request, g, session, flash, redirect, url_for, abort
from grasscms import data_dir
import os, urlparse

UPLOAD_FOLDER =  "/var/www/grasscms.com/static/uploads"
app = Flask(__name__)
app.config.update(
	DATABASE_URI = 'mysql://root:root@localhost/grasscms',
        SECRET_KEY = 'Foobar',
    	STATIC_ROOT =  'http://grasscms.com/static/',
	    SERVER_NAME = "grasscms.com",
        UPLOAD_FOLDER = UPLOAD_FOLDER,
        DEBUG = False )

engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
    bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def static(path):
    root = app.config.get('STATIC_ROOT', None)
    if root is None: # fallback on the normal way
        return url_for('static', filename=path)
    return urlparse.urljoin(root, path)

@app.context_processor
def inject_static():
    return dict(static=static)

