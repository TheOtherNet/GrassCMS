from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, Text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, render_template, request, g, session, flash, redirect, url_for, abort
from grasscms import ProductionConfig, DevelopmentConfig
import os, urlparse

if os.environ.has_key('devel') and os.environ['devel'] == "True":
    app = Flask(__name__)
    uploads_relative_dir="/../grasscms/static/uploads"
    app.config.from_object('grasscms.DevelopmentConfig')
else:
    app = Flask(__name__, instance_path='/var/www/grasscms.com/', instance_relative_config=True)
    uploads_relative_dir="/static/uploads"
    app.config.from_object('grasscms.ProductionConfig')

if os.environ.has_key('grasscms_config'):
    app.config.from_envvar('grasscms_config')

app.config.update(STATIC_ROOT =  'http://' + app.config['SERVER_NAME'] + '/static/',
    UPLOAD_FOLDER=app.instance_path + uploads_relative_dir)

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
