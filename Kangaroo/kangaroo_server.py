from kangaroo.openid_login import engine, app, db_session, g, Base
from flaskext.wtf import Form, TextField, FieldList, FileField
from flaskext.gravatar import Gravatar
from flask import render_template, request, redirect, url_for
from sqlalchemy import ForeignKey, Column, Integer, String
import json, os
from werkzeug import secure_filename

"""
    TODO LIST:
        - All images can be accesible (and overwritten) by other users
        - There's no validation on page input.
        - Improve styles and usability
"""

class File(Base):
    __tablename__ = "file"
    id_ = Column(Integer, primary_key=True)
    x = Column(Integer)
    y = Column(Integer)
    filename = Column(String(60))
    type_ = Column(String(60))
    page = Column(String(60))
    user = Column(Integer, ForeignKey('users.id'))

    def __init__(self, type_, user=False, filename=False, id_=False, x=100, y=100):
        self.type_ = type_
        self.user = user.id
        self.page = user.page
        self.filename = filename
        self.x = x
        self.y = y

class FileUploadForm(Form):
    filename = FileField('Upload your images')
    type_ = TextField('Type')

@app.route("/upload/", methods=("GET", "POST"))
def upload_():
    form = FileUploadForm()
    if form.validate_on_submit():
        file_ = form.filename.file
        if file_: 
            filename = secure_filename(file_.filename)
            file_.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db_session.add(File(form.type_.data, g.user, file_.filename))
            db_session.commit()
    else:
        filename = None
    return render_template("upload.html",
                           form=form,
                           filedata=filename)

@app.route('/<page>')
def index(page):
    if not g.user and g.user.page != page:
        return render_template('index.html',
            imgs=File.query.filter_by(page=page,
                    type_="img"))
    else:
        return render_template('admin.html',
            imgs=File.query.filter_by(user=g.user.id,
                    type_="img"))

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
    app.run()
