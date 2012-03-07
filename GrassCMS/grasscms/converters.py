#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
    GrassCMS - Simple drag and drop content management system
"""

from grasscms.odt2html import Odt2html, quick_xsl
import json, os, mimetypes, zipfile

odt_mimetypes = [ 'vnd.oasis.opendocument.text' ]
docx_mimetypes = [
    'vnd.openxmlformats-officedocument.wordprocessingml.document' 
] 
odt_converter = Odt2html(quick_xsl)

def get_type(path):
    """
        Get the mimetype of the file, returns an array.
    """
    return mimetypes.guess_type(path)[0].split('/')

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

def read_file(file_):
    with open(file_) as filen:
        return filen.read().decode('utf-8')
