#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
    GrassCMS - Simple drag and drop content management system
"""
from grasscms.main import * 
from grasscms.forms import *
from grasscms.openid_login import *
from grasscms.odt2html import Odt2html, quick_xsl
from grasscms.models import File, Text, Blog, Page, Html
from flaskext.gravatar import Gravatar
from werkzeug import secure_filename
import json, os, mimetypes, zipfile

odt_mimetypes = [ 'vnd.oasis.opendocument.text' ]
docx_mimetypes = [
    'vnd.openxmlformats-officedocument.wordprocessingml.document' 
] 
odt_converter = Odt2html(quick_xsl)

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
"""

def get_path(filename):
    """
        Return the full path of a file in local.
    """
    return os.path.join(app.config['UPLOAD_FOLDER'], filename)

def get_type(path):
    """
        Get the mimetype of the file, returns an array.
    """
    return mimetypes.guess_type(path)[0].split('/')

def save_file(file_):
    """
        Securely save a file 
    """
    file_secure_name = secure_filename(file_.filename)
    path = get_path(file_secure_name)
    file_.save(path)
    return (file_secure_name, path)

def extract_odt_images(path):
    """
        TODO: same problem as the images, will be overwriten...
    """
    with zipfile.ZipFile(path, 'r') as zipf:
        images = [ image for image in zipf.infolist() \
            if "Pictures" in image.filename  ]
        for image in images:
            zipf.extract(image, get_path(''))

def convert_odt(path):
    """
        Convert from odt
    """
    result = odt_converter.convert(path)
    extract_odt_images(path)
    os.unlink(path)
    return result

def convert_docx(path):
    """
        Convert from docx
    """
    file_contents = docx.getdocumenttext(docx.opendocx(path))
    os.unlink(path)
    return '\n'.join([ unicode(a.decode('utf-8')) for a in file_contents])

def do_conversion(filename, path):
    """
        Automatically convert convertable files
    """
    type_ = get_type(path)
    if type_[0] == "image":
        return ("image", filename)
    if type_[1] in odt_mimetypes:
        path = convert_odt(path)
        type_ = "text"
    if type_[1] in docx_mimetypes:
        path = convert_docx(path)
        type_ = "text"
    return (type_, path)

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
            db_session.add(File(type_, g.user, page.id, filename))
        elif type_ == "text":
            db_session.add(Text(filename.decode('utf-8'), g.user, page.id, blog.id))
            app.logger.info(filename)
        else: 
            abort(500) # TODO: Die gracefully when we cannot import the file.
        db_session.commit()
        return redirect(blog.name + "/" + page.name)

    return render_template("upload.html", filedata="", page=page, blog=blog)

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
        menu_blog = Html(blog=blog.id, user = g.user, width=100, height=100,
        content='\n'.join([ "<a href=\"/%s/%s\">%s</a>"\
            %(blog.name, a.name, a.name) for a in \
            Page.query.filter_by(blog = blog.id)]))
        menu_blog.field_name = "menu"
        db_session.add(menu_blog)
        app.logger.info(menu_blog.content)
    else:
        menu_blog.content='\n'.join([ "<a href=\"/%s/%s\">%s</a>"\
            %(blog.name, a.name, a.name) for a in \
            Page.query.filter_by(blog = blog.id)])
        app.logger.info("Updating")
        app.logger.info(menu_blog.content)
    db_session.commit()
    return ""
        
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
    page = Page.query.filter_by(blog=user_blog.id, name = page).first()

    if not id_:
        try:
            text = request.form['text']
        except:
            text = "Insert your text here"
        db_session.add(Text(text, g.user, page.id, user_blog.id))
        db_session.commit()
        return "" 
    else:
        text = Text.query.filter_by(id_=int(id_.replace('text_', '')), page=page.id).first()
        if not text:
            return ""
        text.content = request.form['text']
        db_session.commit()
        return text.content

def read_file(file_):
    with open(file_) as filen:
        return filen.read().decode('utf-8')

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
    if blog_menu:
        app.logger.info(blog_menu.content)
    if not g.user or g.user.blog != user_blog_id:
        return render_template( 'index.html',
            imgs=File.query.filter_by(page=page.id, type_="image"), page=page, blog=user_blog, 
            blog_menu=blog_menu, txt_blobs=txt_blobs )
    else:
        return render_template('admin.html',
            imgs=File.query.filter_by(page=page.id, type_="image"), blog=user_blog,
                page=page, blog_menu=blog_menu, txt_blobs=txt_blobs)

@app.route('/get/<id_>', methods=['GET', 'POST'])
def get_data(id_):
    try:
        element = File.query.filter_by(id_=id_, user=g.user.id).first()
        return json.dumps([element.x, element.y, element.width, element.height])
    except:
        element = Text.query.filter_by(id_=id_, user=g.user.id).first()
        return json.dumps([element.x, element.y, element.width, element.height])

@app.route('/set_position/<type_>/<id_>', methods=['GET', 'POST'])
def set_position(type_, id_):
    """
        Sets position.
    """
    if type_ == "text":
        element = Text.query.filter_by(id_=id_, user=g.user.id).first()
    elif type_ == "html":
        element = Html.query.filter_by(id_=id_, user=g.user.id).first()
    else:
        element = File.query.filter_by(id_=id_, user=g.user.id).first()
    element.x = int(request.args.get('x'))
    element.y = int(request.args.get('y'))
    db_session.commit()
    return json.dumps([element.x, element.y])

@app.route('/set_dimensions/<type_>/<id_>', methods=['GET', 'POST'])
def set_dimensions(type_, id_):
    """
        AJAX call to set dimensions of an element.
    """
    if type_ == "text":
        element = Text.query.filter_by(id_=id_, user=g.user.id).first()
    elif type_ == "html":
        element = Html.query.filter_by(id_=id_, user=g.user.id).first()
    else:
        element = File.query.filter_by(id_=id_, user=g.user.id).first()
    element.width = int(request.args.get('width')) or 100
    element.height = int(request.args.get('height')) or 100
    db_session.commit()
    return json.dumps([element.x, element.y])

def server():
    """ Main server, will allow us to make it wsgi'able """
    app.run(host='0.0.0.0', port=8181) # Running on port 80 in all interfaces.
