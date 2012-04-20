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

@app.route('/')
def landing():
    user_page, user_blog = check_user()
    if g.user:
        main_url = "http://" + g.user.name.replace(' ','_') + "." + app.config['SERVER_NAME'] 
    else:
        main_url = "http://grasscms.com"
    return render_template('landing.html', main_url=main_url, page=user_page, blog=user_blog)

@app.route('/<page>', subdomain='<blog_name>')
@app.route('/', subdomain='<blog_name>')
def page(blog_name=False, page="index", main_url=False):
    user_blog, user_page = check_user()
    try:
        blog = Blog.query.filter("UPPER(%s) LIKE '%s%s%s'" %("name", '%', urllib.unquote(blog_name).upper(), '%')).first()
        page = Page.query.filter_by(blog=blog.id, name = page).first()
    except AttributeError, error:
        page = user_page
        blog = user_blog
    
    if not page:
        abort(404)
    if g.user:
        main_url = "http://" + g.user.name.replace(' ','_') + "." + app.config['SERVER_NAME'] 

    if blog == user_blog and g.user:
        g.user_is_admin = True
    static_htmls = Html.query.filter_by(blog=blog.id, page=page.id)
    if not g.user_is_admin:
        return render_template( 'index.html', main_url=main_url, page=page, 
            blog=user_blog, static_htmls=static_htmls)
    else:
        return render_template( 'admin.html', main_url=main_url, page=page,
            blog=user_blog, static_htmls=static_htmls, 
            first_run=request.args.get('first_run'))

@app.route("/upload/<page>", methods=("GET", "POST"), subdomain="<subdomain>")
@app.route("/upload/<page>", methods=("GET", "POST"))
def upload_(page, subdomain=False):
    object_base = Objects()
    for i in request.files.keys():
        filename, path = save_file(request.files[i])
        try:
           field_name, content = do_conversion(filename, path)
        except:
            return flash('Error file, unsupported format')
        return getattr(object_base, field_name)(page, content)
    return render_template("upload.html", filedata="", page=page, blog=blog)

@app.route('/new/<type_>/<page>', methods=['GET', 'POST'], subdomain="<subdomain>")
def new(type_, page, subdomain=False):
    object_base = Objects()
    return getattr(object_base, type_)(page)
    
@app.route('/delete/<id_>/<is_page>', methods=['DELETE'], subdomain="<subdomain>")
@app.route('/delete/<id_>', methods=['DELETE'], subdomain="<subdomain>")
def delete(id_, is_page=False, subdomain=False):
    if is_page:
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
    try:
        return json.dumps(getattr(element, what)) 
    except Exception, error:
        app.logger.info(error)
        return "False"

@app.route('/set/<what>/<id_>/<result>', methods=['GET', 'POST'], subdomain="<subdomain>")
def set(what, id_, result, subdomain=False):
    element = get_element_by_id(id_)
    try:
        setattr(element, what, result)
        db_session.commit()
        return json.dumps(getattr(element, what)) 
    except Exception, error:
        app.logger.info(error)
        return "False"
