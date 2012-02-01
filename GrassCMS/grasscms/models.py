from grasscms.main import *

class Text(Base):
    __tablename__ = "text"
    id_ = Column(Integer, primary_key=True)
    x = Column(Integer)
    y = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    content = Column(String(60))
    blog = Column(Integer, ForeignKey('blogs.id'))
    page = Column(Integer, ForeignKey('pages.id'))
    user = Column(Integer, ForeignKey('users.id'))

    def __init__(self, content=False, user=False, page=False, blog=False, x=100, y=100, width=100, height=100):
        self.user = user.id
        self.page = page
        self.content = content
        self.x = x
        self.blog = blog
        self.y = y
        self.width = width
        self.height = height

class File(Base):
    __tablename__ = "file"
    id_ = Column(Integer, primary_key=True)
    x = Column(Integer)
    y = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    content = Column(String(60))
    type_ = Column(String(60))
    page = Column(Integer, ForeignKey('pages.id'))
    user = Column(Integer, ForeignKey('users.id'))

    def __init__(self, type_, user=False, page=False, content=False, id_=False, x=100, y=100, width=100, height=100):
        self.type_ = type_
        self.user = user.id
        self.page = page
        self.content = content
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class Blog(Base):
    __tablename__ = "blogs"
    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    def __init__(self, blog):
        self.name = blog

class Page(Base):
    __tablename__ = "pages"
    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    blog = Column(Integer, ForeignKey('blogs.id'))

    def __init__(self, blog, name):
        self.name = name
        self.blog = blog

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    email = Column(String(200))
    openid = Column(String(200))
    blog = Column(Integer, ForeignKey('blogs.id'))
    index = Column(Integer, ForeignKey('pages.id'))

    def __init__(self, name, email, openid, blog, index):
        self.name = name
        self.email = email
        self.openid = openid
        self.blog = blog
        self.index = index
