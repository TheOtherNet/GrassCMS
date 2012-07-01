#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
    GrassCMS - Simple drag and drop content management system
"""

from grasscms.odt2html import Odt2html, quick_xsl
import os, mimetypes, zipfile
from PIL import Image

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
            zipf.extract(image, '')

def convert_odt(path):
    """
        Convert from odt
    """
    result = odt_converter.convert(path)
    extract_odt_images(path)
    os.unlink(path)
    return result.decode('utf-8')

def do_conversion(filename, path, static_root=False, user=False):
    """
        Automatically convert convertable files
    """
    type_ = get_type(path)
    if type_[0] == "image":
        height, width = Image.open(path).size
        path = ( '%suploads/%s/%s' %(static_root, user, filename), width, height )
        type_ = "image"
    elif type_[0] == "video" or type_[1] == "ogg":
        try:
            type_ = "video"
            os.system('avconv -i %s -s 960x540 -b 20000 -acodec libvorbis -ab 100k -f webm -y %s.webm' %(path, path));
            path = filename + ".webm"
        except Exception, error:
            flash('Error converting video')
            raise Exception('avconv', error)
    elif type_[1] in odt_mimetypes:
        path = convert_odt(path)
        type_ = "text"
    return (type_, path)

def read_file(file_):
    with open(file_) as filen:
        return filen.read().decode('utf-8')
