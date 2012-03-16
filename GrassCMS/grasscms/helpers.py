#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
    GrassCMS - Simple drag and drop content management system
"""
import json, os
from werkzeug import secure_filename

def render_html(type_, html):
    if type_ == "menu_old":
        return json.dumps([html.id_, html.content])
    else:
        return json.dumps(['', '<div class="static static_html" style="width:%spx; height:%spx; \
        top:%spx; left:%spx;" id="%s%s"> %s </di>' %(html.width, html.height, html.x, html.y, type_, html.id_, html.content)])

def render_text(text):
    return '<div class="text_blob draggable texts" style="top:%spx; left:%spx;" id="%s" >\
              <div class="handler" style="display:none; background:black; height:8px;\
              border-radius:3px" id="handler_text_%s" > </div>\
              <div>\
                  <textarea  style="min-width:1em; min-height:1em;"  \
                      id="text_%s" class="CKeditor_blob editor">%s</textarea>\
              </div>\
          </div>' %(text.x, text.y, text.id_, text.id_, text.id_, text.content)


def render_image(image):
    return json.dumps('<img class="img" style="width:%spx;height:%spx;" id="%s" \
           src="/static/uploads/%s" />' %(image.width, image.height, image.id_, image.content))

