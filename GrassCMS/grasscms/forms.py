from flaskext.wtf import Form, TextField, FieldList, FileField, HiddenField

class FileUploadForm(Form):
    filename = FileField('Upload your images')
    type_ = HiddenField()

class TextUploadForm(Form):
    content = TextField('Insert text')
    type_ = HiddenField()
