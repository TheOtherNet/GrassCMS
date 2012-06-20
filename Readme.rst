GrassCMS, a flask-based html5, drag-and-drop CMS aiming to be the simplest.

Right now, basically, yo can drag and drop your images and documents from the desktop
and place them and resize them as you want. It also features a rich text editor (ckeditor)
with lots of features.
Remember, you don't need to save anything, it's automatic!

It basically features a personal site, where you can store pages and subpaginate them, 
the administration panel is completly transparent, you'll see everything exactly as
the user sees it, and as it's automagic everything will be saved in real time, 
so you don't need to worry about anything.

Current features:
    - Automagic odt import
    - Txt file import
    - General file uploads with drag-and-drop from the desktop
        - (ODT and any web-viewable image format)
    - Drag and drop and resizable objects
    - On-screen persistence
    - Fixed layout
    - Simple registration via openid
    - Gravatar
    - Simple profile editing
    - Old browsers support via html5shiv
    - Responsive layout (WIP, it still gets a little unusable)
    - Automatic menu generation

Technologies being used
    - odt2html.py
    - ckeditor
    - Twitter Bootstrap
    - Flask
    - Flask-openid
    - Flask-gravatar
    - Jquery
    - Jquery fileupload 
    - The initial web template is disposable at http://github.com/XayOn/Webstarter
    - Html5Shiv
