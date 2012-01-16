# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, g, session, flash, \
     redirect, url_for, abort
from flaskext.openid import OpenID
from sqlalchemy import create_engine, ForeignKey, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

UPLOAD_FOLDER = '/home/xayon/Kangaroo/kangaroo/static/uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

app.config.update(
        DATABASE_URI = 'sqlite:////tmp/flask-openid.db',
        SECRET_KEY = 'Foobar',
        UPLOAD_FOLDER = UPLOAD_FOLDER,
        DEBUG = True )

oid = OpenID(app)

engine = create_engine(app.config['DATABASE_URI'])

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,
    bind=engine))

Base = declarative_base()

Base.query = db_session.query_property()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    email = Column(String(200))
    openid = Column(String(200))
    page = Column(String, ForeignKey('users.page'))

    def __init__(self, name, email, openid, page):
        self.name = name
        self.email = email
        self.openid = openid
        self.page = page

@app.before_request
def before_request():
    g.user = None
    if 'openid' in session:
        g.user = User.query.filter_by(openid=session['openid']).first()

@app.after_request
def after_request(response):
    db_session.remove()
    db_session.commit()
    return response

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    """
        Does the login via OpenID.  Has to call into `oid.try_login`
        to start the OpenID machinery.
    """
    if g.user is not None:
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
        if openid:
            return oid.try_login(openid, ask_for=['email', 'fullname',
                                                  'nickname'])
    return render_template('login.html', next=oid.get_next_url(),
                           error=oid.fetch_error())
@oid.after_login
def create_or_login(resp):
    """
        This is called when login with OpenID succeeded and it's not
        necessary to figure out if this is the users's first login or not.
        This function has to redirect otherwise the user will be presented
        with a terrible URL which we certainly don't want.
    """
    session['openid'] = resp.identity_url
    user = User.query.filter_by(openid=resp.identity_url).first()
    if user is not None:
        flash(u'Successfully signed in')
        g.user = user
        return redirect(oid.get_next_url())
    return redirect(url_for('create_profile', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email))

@app.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    """
        If this is the user's first login, the create_or_login function
        will redirect here so that the user can set up his profile.
    """
    if g.user is not None or 'openid' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        page = request.form['page']
        if not name:
            flash(u'Error: you have to provide a name')
        elif '@' not in email: # TODO: Do this with wtf forms.
            flash(u'Error: you have to enter a valid email address')
        else:
            flash(u'Profile successfully created')
            db_session.add(User(name, email, session['openid'], page))
            db_session.commit()
            return redirect(oid.get_next_url())
    return render_template('create_profile.html', next_url=oid.get_next_url())

@app.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    """
        Updates a profile
    """
    if g.user is None:
        abort(401)
    form = dict(name=g.user.name, email=g.user.email)
    if request.method == 'POST':
        if 'delete' in request.form:
            db_session.delete(g.user)
            db_session.commit()
            session['openid'] = None
            flash(u'Profile deleted')
            return redirect(url_for('index'))
        form['name'] = request.form['name']
        form['email'] = request.form['email']
        if not form['name']:
            flash(u'Error: you have to provide a name')
        elif '@' not in form['email']:
            flash(u'Error: you have to enter a valid email address')
        else:
            flash(u'Profile successfully created')
            g.user.name = form['name']
            g.user.email = form['email']
            return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html', form=form)

@app.route('/logout')
def logout():
    session.pop('openid', None)
    flash(u'You have been signed out')
    return redirect(oid.get_next_url())

