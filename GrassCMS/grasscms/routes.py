from grasscms.models import File, Text, Blog, Page, Html
from grasscms.main import *
from grasscms.forms import *
from grasscms.openid_login import *
from grasscms.converters import *
from grasscms.helpers import *
import json, os, urllib
from werkzeug import secure_filename

def render_html(html, type_=False, is_ajax=False):
    if is_ajax:
        return '<div class="static %s static_html" style="width:%spx; height:%spx; \
            top:%spx; left:%spx;" id="%s%s"> %s </div>' %(html.field_name, html.width, html.height, html.x, html.y, html.field_name, html.id_, html.content)
    else:
        return '<div class="static %s static_html" style="width:%spx; height:%spx; \
           top:%spx; left:%spx;" id="%s%s"> %s </div>' %(html.field_name, html.width, html.height, html.x, html.y, html.field_name, html.id_, html.content)

def render_text(text, is_ajax=False):
    if g.user_is_admin or is_ajax: 
        return '<div class="text_blob draggable texts" style="top:%spx; left:%spx;" id="%s" > \
                <div class="handler" style="display:none;" id="handler_text_%s" > \
                    <a style="color:white; margin-left:3px;" onclick="delete_text(this); return false;">X</a> </div> \
                <div>\
                    <textarea  style="min-width:1em; min-height:1em;"  \
                        id="text_%s" class="CKeditor_blob editor"> \
                            %s</textarea>\
                </div>\
            </div>' %(text.x, text.y, text.id_, text.id_, text.id_, text.content)
    else:
        return '<div class="text_blob" style="position:fixed; top:%spx; left:%spx; width:%spx; height:%spx; overflow:auto; opacity:%s; rotation:%s;">%s</div>' %(text.x, text.y, text.width, text.height, text.opacity, text.rotation, text.content)

def render_image(image, is_ajax=False):
    if g.user_is_admin or is_ajax:
        return '<img class="img" style="z-index:%s; opacity:%s; -moz-transform: rotate(%sdeg); -webkit-transform:rotate(%sdeg); -o-transform(%sdeg); -ms-transform(%sdeg); width:%spx;height:%spx;" id="img%s" \
           src="%s" />' %(image.zindex, image.opacity, image.rotation, image.rotation, image.rotation, image.rotation, image.width, image.height, image.id_, image.content)
    else:
        return '<img class="img" style="z-index:%s;top:%spx; position:fixed; left:%spx; opacity:%s; -moz-transform: rotate(%sdeg); -webkit-transform:rotate(%sdeg); -o-transform(%sdeg); -ms-transform(%sdeg); width:%spx;height:%spx;" id="img%s" \
           src="%s" />' %(image.zindex, image.x, image.y, image.opacity, image.rotation, image.rotation, image.rotation, image.rotation, image.width, image.height, image.id_, image.content)

app.jinja_env.filters['html'] = render_html
app.jinja_env.filters['text'] = render_text
app.jinja_env.filters['image'] = render_image


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
    return render_template('landing.html', page=user_page, blog=user_blog)

@app.route('/')
@app.route('/', subdomain="<blog_name>")
@app.route('/page/<page>', subdomain='<blog_name>')
@app.route('/<blog_name>/<page>') 
def index(blog_name=False, page="index"):
    blog_name = blog_name.replace('_', ' ')
    user_blog, user_page = check_user()

    if not page:
        page = "index"

    try:
        tmp_blog = Blog.query.filter("UPPER(%s) LIKE '%s%s%s'" %("name", '%', urllib.unquote(blog_name).upper(), '%')).first()
        app.logger.info(page)
        page = Page.query.filter_by(blog=tmp_blog.id, name = page).first()
        blog = tmp_blog
        app.logger.info(blog)
        app.logger.info(page)
    except AttributeError, error:
        page = user_page
        blog = user_blog
        pass


    if page:
        txt_blobs = Text.query.filter_by(page=page.id)
        static_htmls = Html.query.filter_by(blog=blog.id)
    else:
        return render_template('landing.html')

    g.requested_blog=tmp_blog

    if g.requested_blog == user_blog and g.user:
        g.user_is_admin = True

    if not g.user_is_admin:
        return render_template( 'index.html',
            imgs=File.query.filter_by(page=page.id, type_="image"), page=page, blog=user_blog, 
            static_htmls=static_htmls, txt_blobs=txt_blobs )
    else:
        return render_template('admin.html', first_run=request.args.get('first_run'),
            base_subdomain_url = "http://" + blog_name + "." + app.config['SERVER_NAME'],
            imgs=File.query.filter_by(page=page.id, type_="image"), blog=user_blog,
                page=page, static_htmls=static_htmls, txt_blobs=txt_blobs)

@app.route("/upload/<page>", methods=("GET", "POST"), subdomain="<subdomain>")
@app.route("/upload/<page>", methods=("GET", "POST"))
def upload_(page, subdomain=False):

    """
        Launch upload page, this will be unlikely rendered (only on old browsers)
        Instead, it will save a file, and create a file object for it.
    """

    blog = Blog.query.filter_by(id=g.user.blog).first()
    page = Page.query.filter_by(name=page, blog=blog.id).first()
    for i in request.files.keys():
        filename, path = save_file(request.files[i])
        type_, filename = do_conversion(filename, path)
        if type_ == "image":
            object_ = File(user=g.user, page=page.id, content="%suploads/%s/%s" %(app.config['STATIC_ROOT'], g.user.id, filename))
            object_.type_="image"
            db_session.add(object_)
            db_session.commit()
            result = render_image(object_, is_ajax=True)
        elif type_ == "text":
            object_ = Text(filename.decode('utf-8'), g.user, page.id, blog.id)
            db_session.add(object_)
            db_session.commit()
            result = render_text(text, is_ajax=True)
        elif type_ == "video":
            object_ = Html('', g.user, page.id, blog.id)
            db_session.add(object_)
            db_session.commit()
            object_.content = "<video width='100%%' height='100%%' id='video%s'><source src='%suploads/%s/%s'></source></video>" %(object_.id_, app.config['STATIC_ROOT'], g.user.id, filename.decode('utf-8'))
            object_.field_name="video"
            db_session.commit()
            result = render_html(object_, is_ajax=True)
        else: 
            abort(500)

        return result

    return render_template("upload.html", filedata="", page=page, blog=blog)

@app.route('/delete_file/<id_>/', methods=['DELETE'])
@app.route('/delete_file/<id_>/', methods=['DELETE'])
@app.route('/delete_img/<id_>/', methods=['DELETE'])
@app.route('/delete_img/<id_>/', methods=['DELETE'], subdomain="<subdomain>")
def delete_file(id_, subdomain=False):
    """
        Delete a file object
    """
    db_session.delete(File.query.filter_by(id_ = id_, user=g.user.id).first())
    db_session.commit()
    return json.dumps(True)

@app.route('/delete_page/<name>')
@app.route('/delete_page/<name>', subdomain="<subdomain>")
def delete_page(name, subdomain=False):
    blog = Blog.query.filter_by(id=g.user.blog).first()
    page = Page.query.filter_by(name = name, blog=blog.id).first()
    if page:
        db_session.delete(page)
        db_session.commit()
    else:
        abort(404)
    return "true"

@app.route('/new_page/<name>')
@app.route('/new_page/<name>', subdomain="<subdomain>")
def new_page(name, subdomain=False):
    blog = Blog.query.filter_by(id=g.user.blog).first()
    page = Page.query.filter_by(name = name, blog=blog.id).first()
    if not page:

        db_session.add(Page(g.user.blog, name))
        db_session.commit()
        return "/" +  blog.name + "/" + name
    else:
        abort(401)

@app.route('/get_pagination/')
@app.route('/get_pagination/', subdomain="<subdomain>")
def get_pagination(blog, page, subdomain=False):
    return "Not implemented"

@app.route('/update_menu/<blog>/', methods=['POST'])
@app.route('/update_menu/<blog>/', methods=['POST'], subdomain="<subdomain>")
def get_menu(blog, subdomain=False):
    blog = Blog.query.filter_by(id = blog).first()
    menu_blog = Html.query.filter_by(blog=blog.id, field_name="menu" ).first()
    if not menu_blog:
        type_ = "menu"
        menu_blog = Html(blog=blog.id, user = g.user, width=200, height=100, content="")
        menu_blog.field_name = "menu"
        db_session.add(menu_blog)
        db_session.commit()
        menu_blog.content='<div id="menu%s">%s</div>' %(menu_blog.id_, '\n'.join([ "<a href=\"http://%s.%s/page/%s\">%s</a>"\
            %(blog.name.replace(' ', '_'), app.config['SERVER_NAME'], a.name, a.name) for a in \
            Page.query.filter_by(blog = blog.id)]) + "</div>")
    else:
        type_ = "menu_old"
        menu_blog.content='<div id="%s">' %(menu_blog.id_) + '\n'.join([ "<a href=\"http://%s.%s/page/%s\">%s</a>"\
            %( blog.name.replace(' ', '_'), app.config['SERVER_NAME'], a.name, a.name) for a in \
            Page.query.filter_by(blog = blog.id)])
        app.logger.info(menu_blog.content)
        menu_blog.content += "</div>"
    db_session.commit()
    return render_html(menu_blog, type_, True)
       
@app.route('/delete_static_html/<id_>/', methods=['DELETE'])
@app.route('/delete_static_html/<id_>/', methods=['DELETE'], subdomain="<subdomain>")
@app.route('/delete_div/<id_>/', methods=['DELETE'])
@app.route('/delete_div/<id_>/', methods=['DELETE'], subdomain="<subdomain>")
@app.route('/delete_video/<id_>/', methods=['DELETE'])
@app.route('/delete_video/<id_>/', methods=['DELETE'], subdomain="<subdomain>")
def delete_html(id_, subdomain=False):
    db_session.delete(Html.query.filter_by(user=g.user.id, id_=id_).first())
    db_session.commit()
    return "true"

# Text blobs

@app.route('/text_blob/<page>', methods=['POST'])
@app.route('/text_blob/<page>/', methods=['POST'])
@app.route('/text_blob/<page>/<id_>', methods=['POST'])
@app.route('/text_blob/<page>', methods=['POST'], subdomain="<subdomain>")
@app.route('/text_blob/<page>/', methods=['POST'], subdomain="<subdomain>")
@app.route('/text_blob/<page>/<id_>', methods=['POST'], subdomain="<subdomain>")
def text(page, id_=False, subdomain=False):
    """
        If called without an id, a new text (empty) will be created
        Otherwise, it'll try to update the text to the text in the form,
        if we have not specified text in the form (i.e, the first time after
        a text creation), it returns the text
    """
        
    user_blog = Blog.query.filter_by(id=g.user.blog).first()
    page = get_page(page).id
    if not id_:
        text = Text("Insert your text here", g.user, page, user_blog.id)
        db_session.add(text)
        result = render_text(text, is_ajax=True)
    else:
        text = Text.query.filter_by(id_=int(id_.replace('text_', '')), 
            page=page).first()
        if not text:
            abort(500) # Nope.
        text.content = request.form['text']
        result = render_text(text, is_ajax=True)

    db_session.commit()
    return render_text(text, is_ajax=True)

@app.route('/delete_text_blob/<id_>', methods=['DELETE'])
@app.route('/delete_text_blob/<id_>', methods=['DELETE'], subdomain="<subdomain>")
def delete_text(id_, subdomain=False):
    text = Text.query.filter_by(id_=id_).first();
    db_session.delete(text)
    db_session.commit()
    return json.dumps("True")

# Persistence handlers
@app.route('/get/<what>/<type_>/<id_>', methods=['GET', 'POST'])
@app.route('/get/<what>/<type_>/<id_>', methods=['GET', 'POST'], subdomain="<subdomain>")
def get(what, type_, id_, subdomain=False):
    element = get_element_by_id(id_, type_)
    try:
        return json.dumps(getattr(element, what)) 
    except Exception, error:
        app.logger.info(error)
        return "False"

@app.route('/get_position/<type_>/<id_>', methods=['GET', 'POST'])
@app.route('/get_position/<type_>/<id_>', methods=['GET', 'POST'], subdomain="<subdomain>")
def get_position(type_, id_, subdomain=False):
    id_ = id_.replace('menu', '')
    element = get_element_by_id(id_, type_)

    try:
        return json.dumps([element.x, element.y, element.width, element.height])
    except Exception, error:
        app.logger.info(error)
        return "False"

@app.route('/set_position/<type_>/<id_>', methods=['GET', 'POST'])
@app.route('/set_position/<type_>/<id_>', methods=['GET', 'POST'], subdomain="<subdomain>")
def set_position(type_, id_, subdomain=False):
    """
        Sets position.
    """
    element = get_element_by_id(id_, type_)
    element.x = float(request.args.get('x'))
    element.y = float(request.args.get('y'))
    db_session.commit()
    return json.dumps([element.x, element.y])

@app.route('/set_dimensions/<type_>/<id_>', methods=['GET', 'POST'])
@app.route('/set_dimensions/<type_>/<id_>', methods=['GET', 'POST'], subdomain="<subdomain>")
def set_dimensions(type_, id_, subdomain=False):
    """
        AJAX call to set dimensions of an element.
    """
    element = get_element_by_id(id_, type_)
    element.width = float(request.args.get('width')) or 200
    element.height = float(request.args.get('height')) or 200
    db_session.commit()
    return json.dumps([element.x, element.y])

@app.route('/get_opacity/<type_>/<id_>')
@app.route('/get_opacity/<type_>/<id_>', subdomain="<subdomain>")
def get_opacity(type_, id_, subdomain=False):
    foo=get_element_by_id(id_, type_)
    return json.dumps(foo.opacity)

@app.route('/set_opacity/<type_>/<id_>/<opacity>', methods=['GET', 'POST'])
@app.route('/set_opacity/<type_>/<id_>/<opacity>', methods=['GET', 'POST'], subdomain="<subdomain>")
def set_opacity(type_, id_, opacity, subdomain=False):
    """
        AJAX call to set dimensions of an element.
    """
    element = get_element_by_id(id_, type_)
    element.opacity=opacity
    db_session.commit()
    return element.opacity

@app.route('/get_rotation/<type_>/<id_>')
@app.route('/get_rotation/<type_>/<id_>', subdomain="<subdomain>")
def get_rotation(type_, id_, subdomain=False):
    foo=get_element_by_id(id_, type_)
    return json.dumps(foo.rotation)

@app.route('/get_zindex/<type_>/<id_>')
@app.route('/get_zindex/<type_>/<id_>', subdomain="<subdomain>")
def get_zindex(type_, id_, subdomain=False):
    foo=get_element_by_id(id_, type_)
    return json.dumps(foo.zindex)

@app.route('/set_zindex/<type_>/<id_>/<zindex>', methods=['GET', 'POST'])
@app.route('/set_zindex/<type_>/<id_>/<zindex>', methods=['GET', 'POST'], subdomain="<subdomain>")
def set_zindex(type_, id_, zindex, subdomain=False):
    """
        AJAX call to set dimensions of an element.
    """
    element = get_element_by_id(id_, type_)
    element.zindex=zindex
    db_session.commit()
    return element.zindex

@app.route('/set_rotation/<type_>/<id_>/<angle>', methods=['GET', 'POST'])
@app.route('/set_rotation/<type_>/<id_>/<angle>', methods=['GET', 'POST'], subdomain="<subdomain>")
def set_rotation(type_, id_, angle, subdomain=False):
    """
        AJAX call to set dimensions of an element.
    """
    element = get_element_by_id(id_, type_)
    element.rotation = angle
    db_session.commit()
    return element.rotation

def get_element_by_id(id_, type_):
    if type_ == "file" or type_ == "img":
        element = File.query.filter_by(id_=id_, user=g.user.id).first()
    elif type_ == "text":
        element = Text.query.filter_by(id_=id_, user=g.user.id).first()
    else:
        element = Html.query.filter_by(id_=id_, user=g.user.id).first()
    return element

def get_page(page):
    user_blog = Blog.query.filter_by(id=g.user.blog).first()
    return Page.query.filter_by(blog=user_blog.id, name = page).first()

def get_path(filename):
    """
        Return the full path of a file in local.
    """
    try:
        os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], str(g.user.id) ))
    except:
        pass
    return os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], str(g.user.id) ), filename)

def save_file(file_):
    """
        Securely save a file 
    """
    file_secure_name = secure_filename(file_.filename)
    path = get_path(file_secure_name)
    file_.save(path)
    return (file_secure_name, path)
