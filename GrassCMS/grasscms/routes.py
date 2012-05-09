from grasscms.models import Blog, Page, Html
from grasscms.openid_login import *
from grasscms.converters import *
from grasscms.objects import *
from werkzeug import secure_filename
import json, os, urllib
app.jinja_env.filters['html'] = render_html

def save_file(file_):
    file_secure_name = secure_filename(file_.filename)
    path = get_path(file_secure_name)
    file_.save(path)
    return (file_secure_name, path)

def get_element_by_id(id_):
    return Html.query.filter_by(id_=id_, user=g.user.id).first()

def get_path(filename):
    return os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], str(g.user.id) ), filename)

def check_user():
    if g.user:
        user_blog = Blog.query.filter_by(id=g.user.blog).first()
        user_page = Page.query.filter_by(id=g.user.index).first() if g.user else ""
    else:
        user_page = False
        user_blog = False
    return (user_blog, user_page)

@app.route('/image/edit', subdomain="<subdomain>")
def svgedit(subdomain=False):
    user_page, user_blog = check_user()
    return render_template('svg-editor.html', page=request.args.get('page'))

@app.route('/page_admin/<page>/')
def page_admin(page=False):
    user_page, user_blog = check_user()
    return render_template('pages.html')

@app.route('/')
def landing():
    user_page, user_blog = check_user()
    if g.user:
        main_url = "http://" + g.user.name.replace(' ','_') + "." + app.config['SERVER_NAME'] 
    else:
        main_url = "http://grasscms.com"
    return render_template('landing.html', main_url=main_url, page=user_page, blog=user_blog)

@app.route('/<page>', subdomain='<blog_name>')
@app.route('/<page>/<subpage>', subdomain='<blog_name>')
@app.route('/', subdomain='<blog_name>')
def page(blog_name=False, page="index", subpage=0, main_url=False):
    blog_name=blog_name.lower()
    user_blog, user_page = check_user()
    try:
        blog = Blog.query.filter_by(subdomain=blog_name).first()
        page = Page.query.filter_by(blog=blog.id, name = page).first()
    except AttributeError, error:
        pass

    if not blog:
        return render_template('start_your_blog.html', url=app.config['SERVER_NAME'])
    elif not page:
        abort(404)

    if g.user:
        main_url = "http://" + user_blog.subdomain + "." + app.config['SERVER_NAME'] 

    if blog == user_blog and g.user:
        g.user_is_admin = True

    static_htmls = Html.query.filter_by(blog=blog.id, page=page.id)

    # In a future, each page must have a full title.
    title=page.name
    if title == "index": 
        title = blog.name

    if not g.user_is_admin:
        return render_template( 'index.html', main_url=main_url, page=page, 
            blog=user_blog, static_htmls=static_htmls, 
            description=blog.description, title=title)
    else:
        return render_template( 'admin.html', main_url=main_url, page=page,
            blog=user_blog, static_htmls=static_htmls, title=title, 
            first_run=request.args.get('first_run'))

@app.route('/svgicons.svg', subdomain="<subdomain>")
@app.route('/svgicons.svg')
def icons(subdomain=False):
    with open(data_dir + "/static/svg-edit/images/svg_edit_icons.svg") as f:
        return f.read()

@app.route("/upload/<page>", methods=("GET", "POST"), subdomain="<subdomain>")
@app.route("/upload/<page>", methods=("GET", "POST"))
def upload_(page, subdomain=False):
    object_base = Objects()
    for i in request.files.keys():
        filename, path = save_file(request.files[i])
        try:
           field_name, content = do_conversion(filename, path, app.config['STATIC_ROOT'], g.user.id)
        except Exception, error:
            flash('Error file, unsupported format, reason: %s' %(error))
            return ""
        result = getattr(object_base, field_name)(page, content)
        if not result:
            result = ""
        return result
    return render_template("upload.html", filedata="", page=page, blog=blog)

@app.route('/new/<type_>/<page>', methods=['GET', 'POST'], subdomain="<subdomain>")
def new(type_, page, subdomain=False):
    object_base = Objects()
    try:
        result = request.form['result']
    except KeyError, err:
        result = ""
    return getattr(object_base, type_)(page, result)
    
@app.route('/delete/<id_>/<name>', methods=['DELETE'], subdomain="<subdomain>")
@app.route('/delete/<id_>/', methods=['DELETE'], subdomain="<subdomain>")
def delete(id_, name=False, subdomain=False):
    if name:
        blog = Blog.query.filter_by(id=g.user.blog).first()
        page = Page.query.filter_by(name=name, blog=blog.id).first()
        if page:
            db_session.delete(page)
            db_session.commit()
        else:
            abort(404)
        return "true"

    object_ = Html.query.filter_by(id_=id_).first();
    db_session.delete(object_)
    db_session.commit()
    return json.dumps("True")
    
@app.route('/get/<what>/<id_>', methods=['GET', 'POST'], subdomain="<subdomain>")
def get(what, id_, subdomain=False):
    element = get_element_by_id(id_)
    if id_ == "undefined":
        abort(404)
    try:
        return json.dumps(getattr(element, what)) 
    except Exception, error:
        app.logger.info(error)
        return "False"

@app.route('/set/<what>/<id_>/<result>', methods=['GET', 'POST'], subdomain="<subdomain>")
def set(what, id_, result, subdomain=False):
    element = get_element_by_id(id_)
    if result == "in_post":
        result ="<div class='handler'></div><textarea class='alsoResizable'>%s</textarea>" %(request.form['result'])
    try:
        setattr(element, what, result)
        db_session.commit()
        return json.dumps(getattr(element, what)) 
    except Exception, error:
        app.logger.info(error)
        return "False"
