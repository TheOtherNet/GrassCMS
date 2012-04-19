from grasscms.models import File, Text, Blog, Page, Html
from grasscms.main import *
from grasscms.forms import *
from grasscms.openid_login import *
from grasscms.converters import *
from grasscms.helpers import *
import json, os, urllib
from werkzeug import secure_filename

def get_element_by_id(id_, type_):
    return Html.query.filter_by(id_=id_, user=g.user.id).first()

def get_page(page):
    user_blog = Blog.query.filter_by(id=g.user.blog).first()
    return Page.query.filter_by(blog=user_blog.id, name = page).first()

def get_path(filename):
    return os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], str(g.user.id) ), filename)

def save_file(file_):
    file_secure_name = secure_filename(file_.filename)
    path = get_path(file_secure_name)
    file_.save(path)
    return (file_secure_name, path)

def check_user():
    if g.user:
        user_blog = Blog.query.filter_by(id=g.user.blog).first()
        user_page = Page.query.filter_by(id=g.user.index).first() if g.user else ""
    else:
        user_page = False
        user_blog = False
    return (user_blog, user_page)

def get_blog_and_page(page):
    blog = Blog.query.filter_by(id=g.user.blog).first()
    page = get_page(page).id
    return (blog, page)

def render_html(object_, type_=False, is_ajax=False):
    return '<div style="z-index:%s; position:fixed; display:block; opacity:%s;\
                -moz-transform: rotate(%sdeg); -webkit-transform:rotate(%sdeg);\
                -o-transform(%sdeg); -ms-transform(%sdeg); width:%spx;\
                height:%spx; top:%spx; left:%spx" class="static_html" id="%s">\
                %s </div>' %(
                    object_.zindex, object_.opacity, object_.rotation, object_.rotation,
                    object_.rotation, object_.rotation, object_.width, object_.height,
                    object_.x, object_.y, object_.id_, object_.content)

app.jinja_env.filters['html'] = render_html

class Objects(object):
    def text(page, text="Insert your text here"): 
        blog, page = get_blog_and_page(page)
        object_ = Html(field_name="text", content="<div class='handler'></div><textarea class='alsoResizable'>%s</textarea>" %(text), user=g.user, page=page, blog=blog.id)
        db_session.add(object_)
        return render_html(object_, is_ajax=True)

    def image(page, content):
        blog, page = get_blog_and_page(page)
        object_ = Html(field_name="video", 
            content = "<img src='%suploads/%s/%s' class='alsoResizable' />" \
                %(app.config['STATIC_ROOT'], g.user.id, filename),
            user=g.user, page=page, blog=blog.id)
        db_session.add(object_)
        return render_html(object_, is_ajax=True)

    def video(page, content):
        blog, page = get_blog_and_page(page)
        object_ = Html(field_name="video", 
            content="<video width='100%%' height='100%%' \
                class='alsoResizable'><source \
                src='%suploads/%s/%s'></source></video>" 
                %(app.config['STATIC_ROOT'], g.user.id, 
                filename.decode('utf-8')), 
            user=g.user, page=page, blog=blog.id)
        db_session.add(object_)
        return render_html(object_, is_ajax=True)

    def page(page):
        blog, page = get_blog_and_page(page)
        if not page:
            db_session.add(Page(g.user.blog, name))
            db_session.commit()
            return "/" +  blog.name + "/" + name
        else:
            abort(401)

    def menu(page):
        blog, page = get_blog_and_page(page)
        menu_blog = Html.query.filter_by(blog=blog.id, page=page.id, field_name="menu" ).first()
        content='\n'.join([ "<a href=\"http://%s.%s/page/%s\">%s</a>"\
                %(blog.name.replace(' ', '_'), app.config['SERVER_NAME'], a.name, a.name) for a in \
                Page.query.filter_by(blog = blog.id)]), 
        if not menu_blog:
            menu_blog = Html(content=content, blog=blog.id, 
                user = g.user, width=200, height=100)
            menu_blog.field_name = "menu"
            db_session.add(menu_blog)
        else:
            menu_blog.content=content
        db_session.commit()
        return render_html(menu_blog, 'menu', True)

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
    static_htmls = Html.query.filter_by(blog=blog.id)

    if not g.user_is_admin:
        return render_template( 'index.html', main_url=main_url,
            imgs=File.query.filter_by(page=page.id, type_="image"), page=page, blog=user_blog, 
            static_htmls=static_htmls)
    else:
        return render_template('admin.html', first_run=request.args.get('first_run'),
            main_url=main_url,
            imgs=File.query.filter_by(page=page.id, type_="image"), blog=user_blog,
                page=page, static_htmls=static_htmls)

@app.route("/upload/<page>", methods=("GET", "POST"), subdomain="<subdomain>")
@app.route("/upload/<page>", methods=("GET", "POST"))
def upload_(page, subdomain=False):
    for i in request.files.keys():
        filename, path = save_file(request.files[i])
        try:
           field_name, content = do_conversion(filename, path)
        except:
            return flash('Error file, unsupported format')
        if field_name == "image":
            content = "<img src='%suploads/%s/%s' class='alsoResizable' />" \
                %(app.config['STATIC_ROOT'], g.user.id, filename)
        elif type_ == "text":
            content = filename.decode('utf-8')
        elif type_ == "video":
            content = "<video width='100%%' height='100%%' class='alsoResizable'><source src='%suploads/%s/%s'></source></video>" %(app.config['STATIC_ROOT'], g.user.id, filename.decode('utf-8'))
        else: 
            abort(500)
        return getattr(Objects, field_name)(page, content)
    return render_template("upload.html", filedata="", page=page, blog=blog)

@app.route('/new/<type_>/<page>', methods=['DELETE'], subdomain="<subdomain>")
def new(type_, page):
    return getattr(Objects, type_)(page)
    
@app.route('/delete/<id_>/<is_page>', methods=['DELETE'], subdomain="<subdomain>")
@app.route('/delete/<id_>', methods=['DELETE'], subdomain="<subdomain>")
def delete(id_, is_page=False):
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
    
@app.route('/get_property/<what>/<id_>', methods=['GET', 'POST'], subdomain="<subdomain>")
def get(what, id_, subdomain=False):
    element = get_element_by_id(id_)
    try:
        return json.dumps(getattr(element, what)) 
    except Exception, error:
        app.logger.info(error)
        return "False"

@app.route('/set_property/<what>/<id_>/<result>', methods=['GET', 'POST'], subdomain="<subdomain>")
def set(what, id_, result):
    element = get_element_by_id(id_)
    try:
        setattr(element, what, result)
        db_session.commit()
        return json.dumps(getattr(element, what)) 
    except Exception, error:
        app.logger.info(error)
        return "False"

