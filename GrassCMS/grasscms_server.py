#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from grasscms.main import * 
from grasscms.forms import *
from grasscms.openid_login import *
from grasscms.models import File, Text

from flaskext.gravatar import Gravatar
from werkzeug import secure_filename
import json, os, mimetypes
import docx
from odt2rst import odt2rst, Options
#from odt2txt import OpenDocumentTextFile # Markdown is disabled right now

odt_mimetypes = [ 'vnd.oasis.opendocument.text' ]
docx_mimetypes = [ 'vnd.openxmlformats-officedocument.wordprocessingml.document' ] 

"""
    TODO LIST:
        - All images can be accesible (and overwritten) by other users
        - Document this
"""

def get_path(filename):
    return os.path.join(app.config['UPLOAD_FOLDER'], filename)

def get_type(path):
    return mimetypes.guess_type(path)[0].split('/')

def save_file(file_):
    file_secure_name = secure_filename(file_.filename)
    path = get_path(file_secure_name)
    file_.save(path)
    return (file_secure_name, path)

def convert_odt(path):
    """
        TODO: Each time this is called Options and the rest of stuffs that should be static are executed.
        TODO Create a tmp dir foreach name.
    """
    options = Options()
    options.temp_folder = '/tmp'
    options.images_relative_folder = 'static/uploads'
    odt2rst(path, path, options)
    return

def convert_docx(path):
    file_contents = docx.getdocumenttext(docx.opendocx(path))
    with open(path, 'w') as file_:
        file_.write('\n'.join([ unicode(a.decode('utf-8')) for a in file_contents]))

def do_conversion(filename, path):
    type_ = get_type(path)
    app.logger.info(type_)
    if type_[0] == "image":
        return ("image", filename)
    if type_[1] in odt_mimetypes:
        convert_odt(path)
        type_ = "rst"
    if type_[1] in docx_mimetypes:
        convert_docx(path)
        type_ = "rst"
    return (type_, path)

@app.route("/upload/", methods=("GET", "POST"))
def upload_():
    page = Page.query.filter_by(id = g.user.page).first()
    for i in request.files.keys():
        filename, path = save_file(request.files[i])
        type_, filename = do_conversion(filename, path)
        db_session.add(File(type_, g.user, page.id, filename))
        db_session.commit()
        return redirect(page.name)

    return render_template("upload.html", filedata="", page=page)

@app.route('/update_rst/<id_>')
def update_rst_file(id_):
    """
        TODO Make this work
    """
    file_ = File.query.filter_by(id=id_)
    if not file_.user == g.user.id:
        abort(401)

    with open(get_path(file_.content, 'w')):
        file_.write(getattr(form.request, 'rst_%s' %id_))

@app.route('/text_blob')
@app.route('/text_blob/<id>')
def text(id_=False):
    """
        If called without an id, a new text (empty) will be created
        Otherwise, it'll try to update the text to the text in the form,
        if we have not specified text in the form (i.e, the first time after
        a text creation), it returns the text
    """
    if not id_:
        db_session.add(Text(text, g.user, page.id))
        db_session.commit()
        
    else:
        text = Text.query.filter_by(id=id_).first()
        future_text = getattr(request.form, 'text_%s' %id_)
        if future_text:
            Text.content = future_text
            db_session.commit()
        else:
            return text.text

def read_file(file_):
    with open(file_) as filen:
        return filen.read().decode('utf-8')

@app.route('/')
@app.route('/<page>')
def index(page=-1):
    user_page = Page.query.filter_by(id=g.user.page).first() if g.user else ""

    if page != -1:
        page = Page.query.filter_by(name="%s" %page).first()
        if not page:
            flash(u'There\'s no such page')

    if page == -1 or not page:
        return render_template('landing.html', page=user_page)

    txts = [ (read_file(file_.content), file_.id_) for file_ in\
        File.query.filter_by(user=g.user.id, type_="rst")\
        if file_.content]

    if not g.user or g.user.page != page.id:
        return render_template('index.html',
            imgs=File.query.filter_by(page=page.id, type_="image"), page=user_page,
            txts=txts)
    else:
        return render_template('admin.html',
            imgs=File.query.filter_by(user=g.user.id, type_="image"), page=user_page,
            txts=txts)


@app.route('/get/<id_>', methods=['GET', 'POST'])
def get_data(id_):
    element = File.query.filter_by(id_=id_, user=g.user.id).first()
    return json.dumps([element.x, element.y])

@app.route('/set/<id_>', methods=['GET', 'POST'])
def set_data(id_):
    element = File.query.filter_by(id_=id_, user=g.user.id).first()
    element.x = int(request.args.get('x'))
    element.y = int(request.args.get('y'))
    db_session.commit()
    return json.dumps([element.x, element.y])

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False)
    app.run(host='0.0.0.0', port=80)
