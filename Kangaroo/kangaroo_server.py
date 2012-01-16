from kangaroo.openid_login import engine, app, db_session, g, Base, Page
from flaskext.wtf import Form, TextField, FieldList, FileField
from flaskext.gravatar import Gravatar
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import ForeignKey, Column, Integer, String
import json, os
from werkzeug import secure_filename

"""
    TODO LIST:
        - All images can be accesible (and overwritten) by other users
        - Document this
"""

class File(Base):
    __tablename__ = "file"
    id_ = Column(Integer, primary_key=True)
    x = Column(Integer)
    y = Column(Integer)
    content = Column(String(60))
    type_ = Column(String(60))
    page = Column(Integer, ForeignKey('pages.id'))
    user = Column(Integer, ForeignKey('users.id'))

    def __init__(self, type_, user=False, page=False, content=False, id_=False, x=100, y=100):
        self.type_ = type_
        self.user = user.id
        self.page = page
        self.content = content
        self.x = x
        self.y = y

class FileUploadForm(Form):
    filename = FileField('Upload your images')
    type_ = TextField('')

class TextUploadForm(Form):
    content = FileField('Upload your images')
    type_ = TextField('')

@app.route("/upload/", methods=("GET", "POST"))
def upload_():
    form = FileUploadForm()
    content = None
    page = Page.query.filter_by(id = g.user.page).first()
    if form.validate_on_submit():
        file_ = form.filename.file
        if file_: 
            content = secure_filename(file_.filename)
            file_.save(os.path.join(app.config['UPLOAD_FOLDER'], content))
            db_session.add(File(form.type_.data, g.user, page.id, file_.filename))
            db_session.commit()

    return render_template("upload.html", form=form, filedata=content, page=page)

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

    if not g.user or g.user.page != page.id:
        return render_template('index.html',
            imgs=File.query.filter_by(page=page.id, type_="img"), page=user_page)
    else:
        return render_template('admin.html',
            imgs=File.query.filter_by(user=g.user.id, type_="img"), page=user_page)

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
