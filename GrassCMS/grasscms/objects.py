from grasscms.models import Html, Page, Blog
from grasscms.main import *

def render_html(object_, type_=False, is_ajax=False):
    if object_.rotation != "0":
        rotation = "-moz-transform: rotate(%sdeg); -webkit-transform:rotate(%sdeg);\
                -o-transform(%sdeg); -ms-transform(%sdeg); " %( object_.rotation, 
                object_.rotation, object_.rotation, object_.rotation)
    else:
        rotation = ""
    return '<div style="z-index:%s; position:fixed; display:block; opacity:%s;\
            width:%spx; height:%spx; top:%spx;left:%spx;%s" class="static_html"\
            id="%s"> %s </div>' %(object_.zindex, object_.opacity, object_.width,
            object_.height, object_.x, object_.y, rotation,
             object_.id_, object_.content)

class Objects(object):
    def get_page(self, page):
        blog = Blog.query.filter_by(id=g.user.blog).first()
        return Page.query.filter_by(blog = blog.id, name = page).first()
    
    def get_blog_and_page(self, page):
        blog = Blog.query.filter_by(id=g.user.blog).first()
        page = self.get_page(page).id
        return (blog, page)
    
    def text(self, page, text="Insert your text here"): 
        blog, page = self.get_blog_and_page(page)
        object_ = Html(field_name="text", content="<div class='handler'></div><textarea class='alsoResizable'>%s</textarea>" %(text), user=g.user, page=page, blog=blog.id)
        db_session.add(object_)
        db_session.commit()
        return render_html(object_, is_ajax=True)
    
    def image(self, page, content):
        blog, page = self.get_blog_and_page(page)
        object_ = Html(field_name="image", 
            content = "<img src='%suploads/%s/%s' class='alsoResizable' />" \
                %(app.config['STATIC_ROOT'], g.user.id, content),
            user=g.user, page=page, blog=blog.id)
        db_session.add(object_)
        db_session.commit()
        return render_html(object_, is_ajax=True)
    
    def video(self, page, content):
        blog, page = self.get_blog_and_page(page)
        object_ = Html(field_name="video", 
            content="<video width='100%%' height='100%%' \
                class='alsoResizable'><source \
                src='%suploads/%s/%s'></source></video>" 
                %(app.config['STATIC_ROOT'], g.user.id, 
                content.decode('utf-8')), 
            user=g.user, page=page, blog=blog.id)
        db_session.add(object_)
        db_session.commit()
        return render_html(object_, is_ajax=True)
    
    def page(self, page):
        blog = Blog.query.filter_by(id=g.user.blog).first()
        page_ = Page.query.filter_by(blog = blog.id, name = page).first()
        if not page_:
            db_session.add(Page(g.user.blog, page))
            db_session.commit()
            return "http://%s.%s/%s" %(blog.subdomain,
                app.config['SERVER_NAME'], page)
        else:
            abort(401)
    
    def menu(self, page):
        blog, page = self.get_blog_and_page(page)
        menu_blog = Html.query.filter_by(blog=blog.id, page=page, field_name="menu" ).first()
        if not menu_blog:
            menu_blog = Html(content='', blog=blog.id, page=page, 
                user = g.user, width=200, height=100, field_name = "menu")
            db_session.add(menu_blog)
        db_session.commit()

        menu_blogs = Html.query.filter_by(blog=blog.id, field_name="menu" ).all()
        for menu_blog in menu_blogs:
            menu_blog.content='\n'.join([ "<a href=\"http://%s.%s/%s\">%s</a>"\
                %(blog.subdomain, app.config['SERVER_NAME'], a.name, a.name) for a in \
                Page.query.filter_by(blog = blog.id)])
        db_session.commit()
        return render_html(menu_blog, 'menu', True)
