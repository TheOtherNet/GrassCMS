from grasscms.models import File, Text, Blog, Page, Html
from grasscms.main import *
from grasscms.forms import *
from grasscms.openid_login import *
from grasscms.converters import *
from grasscms.helpers import *

import json, os

@app.route('/')
@app.route('/<blog_name>')
@app.route('/<blog_name>/<page>')
def index(blog_name=False, page="index"):
    if g.user:
        user_blog = Blog.query.filter_by(id=g.user.blog).first()
        user_page = Page.query.filter_by(id=g.user.index).first() if g.user else ""
        user_blog_id = user_blog.id
    else:
        user_page = False
        user_blog_id = False
        user_blog = False

    try:
        tmp_blog = Blog.query.filter_by(name=blog_name).first()
        page = Page.query.filter_by(blog=tmp_blog.id, name = page).first()
        blog = tmp_blog
    except AttributeError, error:
        page = user_page
        blog = user_blog
        pass

    if not blog_name or not page:
        return render_template('landing.html', page=user_page, blog=user_blog)
    if type(page) is str:
        return render_template('landing.html', page=user_page, blog=user_blog)

    txt_blobs = Text.query.filter_by(page=page.id)
    blog_menu = Html.query.filter_by(blog=blog.id, field_name="menu" ).first()
    if not g.user or g.user.blog != user_blog_id:
        return render_template( 'index.html',
            imgs=File.query.filter_by(page=page.id, type_="image"), page=page, blog=user_blog, 
            blog_menu=blog_menu, txt_blobs=txt_blobs )
    else:
        return render_template('admin.html',
            imgs=File.query.filter_by(page=page.id, type_="image"), blog=user_blog,
                page=page, blog_menu=blog_menu, txt_blobs=txt_blobs)

@app.route("/upload/<page>", methods=("GET", "POST"))
def upload_(page):

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
            object_ = File(user=g.user, page=page.id, content=filename)
            object_.type_="image"
            db_session.add(object_)
            db_session.commit()
            result = render_image(object_)
        elif type_ == "text":
            object_ = Text(filename.decode('utf-8'), g.user, page.id, blog.id)
            db_session.add(object_)
            db_session.commit()
            result = render_text(text)
        else: 
            abort(500)

        return result

    return render_template("upload.html", filedata="", page=page, blog=blog)

@app.route('/delete_file/<id_>/', methods=['DELETE'])
def delete_file(id_):
    """
        Delete a file object
    """
    db_session.delete(File.query.filter_by(id_ = id_).first())
    db_session.commit()
    return json.dumps(True)

@app.route('/new_page/<name>')
def new_page(name):
    page = Page.query.filter_by(name = name).first()
    if not page:
        blog = Blog.query.filter_by(id=g.user.blog).first()
        db_session.add(Page(g.user.blog, name))
        db_session.commit()
        return "/" +  blog.name + "/" + name
    else:
        abort(401)

@app.route('/get_pagination/')
def get_pagination(blog, page):
    return "Not implemented"

@app.route('/update_menu/<blog>/', methods=['POST'])
def get_menu(blog):
    blog = Blog.query.filter_by(id = blog).first()
    menu_blog = Html.query.filter_by(blog=blog.id, field_name="menu" ).first()
    if not menu_blog:
        type_ = "menu"
        menu_blog = Html(blog=blog.id, user = g.user, width=200, height=100,
        content='\n'.join([ "<a href=\"/%s/%s\">%s</a>"\
            %(blog.name, a.name, a.name) for a in \
            Page.query.filter_by(blog = blog.id)]))
        menu_blog.field_name = "menu"
        db_session.add(menu_blog)
    else:
        type_ = "menu_old"
        menu_blog.content='\n'.join([ "<a href=\"/%s/%s\">%s</a>"\
            %(blog.name, a.name, a.name) for a in \
            Page.query.filter_by(blog = blog.id)])
    db_session.commit()
    return render_html(type_, menu_blog)
       
@app.route('/html/<blog>/<id_>', methods=['DELETE'])
def delete_html(blog, id_):
    blog = Blog.query.filter_by(id = blog).first()
    db_session.delete(Html.query.filter_by(blog=blog.id, id_=id_).first())
    db_session.commit()
    return "true"

# Text blobs

@app.route('/text_blob/<page>', methods=['POST'])
@app.route('/text_blob/<page>/', methods=['POST'])
@app.route('/text_blob/<page>/<id_>', methods=['POST'])
def text(page, id_=False):
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
        result = render_text(text)
    else:
        text = Text.query.filter_by(id_=int(id_.replace('text_', '')), 
            page=page).first()
        if not text:
            abort(500) # Nope.
        text.content = request.form['text']
        result = render_text(text)

    db_session.commit()
    return render_text(text)

@app.route('/delete_text_blob/<id_>', methods=['DELETE'])
def delete_text(id_):
    text = Text.query.filter_by(id_=id_).first();
    db_session.delete(text)
    db_session.commit()
    return json.dumps("True")

# Persistence handlers
@app.route('/get_position/<type_>/<id_>', methods=['GET', 'POST'])
def get_position(type_, id_):
    id_ = id_.replace('menu', '')
    element = get_element_by_id(id_, type_)
    try:
        return json.dumps([element.x, element.y, element.width, element.height])
    except:
        return False

@app.route('/set_position/<type_>/<id_>', methods=['GET', 'POST'])
def set_position(type_, id_):
    """
        Sets position.
    """
    element = get_element_by_id(id_, type_)
    element.x = int(request.args.get('x'))
    element.y = int(request.args.get('y'))
    db_session.commit()
    return json.dumps([element.x, element.y])

@app.route('/set_dimensions/<type_>/<id_>', methods=['GET', 'POST'])
def set_dimensions(type_, id_):
    """
        AJAX call to set dimensions of an element.
    """
    element = get_element_by_id(id_, type_)
    element.width = int(request.args.get('width')) or 200
    element.height = int(request.args.get('height')) or 200
    db_session.commit()
    return json.dumps([element.x, element.y])

@app.route('/get_opacity/<type_>/<id_>')
def get_opacity(type_, id_):
    foo=get_element_by_id(id_, type_)
    return json.dumps(foo.opacity)

@app.route('/set_opacity/<type_>/<id_>/<opacity>', methods=['GET', 'POST'])
def set_opacity(type_, id_, opacity):
    """
        AJAX call to set dimensions of an element.
    """
    element = get_element_by_id(id_, type_)
    element.opacity=opacity
    db_session.commit()
    return element.opacity

@app.route('/get_rotation/<type_>/<id_>')
def get_rotation(type_, id_):
    foo=get_element_by_id(id_, type_)
    app.logger.info(foo.rotation)
    return json.dumps(foo.rotation)

@app.route('/set_rotation/<type_>/<id_>/<angle>', methods=['GET', 'POST'])
def set_rotation(type_, id_, angle):
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
        element = Html.query.filter_by(id_=id_, user=g.user.id, 
            field_name=type_).first()
    return element

def get_page(page):
    user_blog = Blog.query.filter_by(id=g.user.blog).first()
    return Page.query.filter_by(blog=user_blog.id, name = page).first()

def get_path(filename):
    """
        Return the full path of a file in local.
    """
    return os.path.join(app.config['UPLOAD_FOLDER'], filename)

def save_file(file_):
    """
        Securely save a file 
    """
    file_secure_name = secure_filename(file_.filename)
    path = get_path(file_secure_name)
    file_.save(path)
    return (file_secure_name, path)
