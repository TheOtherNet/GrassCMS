# -*- coding: utf-8 -*-
from grasscms.main import *
from grasscms.models import Page, User, Blog
from flaskext.openid import OpenID
oid = OpenID(app)

def check_form(name, email, page_name):
    possible_blog = Blog.query.filter_by(name=page_name).first()
    if not name:
        flash(u'Error: you have to provide a name')
    elif '@' not in email: # TODO: Do this with wtf forms.
        flash(u'Error: you have to enter a valid email address')
    elif possible_blog is not None and g.user.blog != possible_blog.id:
        flash(u'Error: That page name is already taken')
    else:
        return True
    return False

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
        openid = request.form.get('openid_identifier')
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
    form = {}
    if g.user is not None or 'openid' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        form['name'] = request.form['name']
        form['email'] = request.form['email']
        form['page_name'] = request.form['page']
        if check_form(form['name'], form['email'], form['page_name']):
            flash(u'Profile successfully created')
            blog = Blog(form['page_name'])
            db_session.add(blog) # Create a blog with that name
            db_session.commit()

            page=Page(blog.id, 'index') # Add the page to the blog
            db_session.add(page)
            db_session.commit()

            db_session.add(User(form['name'], form['email'], session['openid'], blog.id, page.id)) # Add a user with that blog referenced
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
    else:
        user_blog = Blog.query.filter_by(id=g.user.blog).first()
        user_index = Page.query.filter_by(blog=user_blog.id).first()

    form = dict(name=g.user.name, email=g.user.email, page=user_blog.name)

    if request.method == 'POST':
        if 'delete' in request.form:
            db_session.delete(g.user)
            db_session.commit()
            session['openid'] = None
            flash(u'Profile deleted')
            return redirect(url_for('index'))
        
        form['name'] = request.form['name']
        form['email'] = request.form['email']
        form['page'] = request.form['page']

        if check_form(form['name'], form['email'], form['page']):
            flash(u'Profile successfully updated')
            g.user.name = form['name']
            g.user.email = form['email']
            user_blog.name = form['page']
            db_session.commit()
            return redirect(url_for('edit_profile'))

    return render_template('edit_profile.html', form=form, blog=user_blog, page=user_index)

@app.route('/logout')
def logout():
    session.pop('openid', None)
    flash(u'You have been signed out')
    return redirect(oid.get_next_url())

