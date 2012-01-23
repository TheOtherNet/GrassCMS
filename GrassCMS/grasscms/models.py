from grasscms.main import *

class Text(Base):
    __tablename__ = "text"
    id_ = Column(Integer, primary_key=True)
    x = Column(Integer)
    y = Column(Integer)
    content = Column(String(60))
    page = Column(Integer, ForeignKey('pages.id'))
    user = Column(Integer, ForeignKey('users.id'))

    def __init__(self, user=False, page=False, content=False, id_=False, x=100, y=100):
        self.user = user.id
        self.page = page
        self.content = content
        self.x = x
        self.y = y

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

class Page(Base):
    __tablename__ = "pages"
    id = Column(Integer, primary_key=True)
    name = Column(String(60))

    def __init__(self, name):
        self.name = name

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    email = Column(String(200))
    openid = Column(String(200))
    page = Column(Integer, ForeignKey('pages.id'))

    def __init__(self, name, email, openid, page):
        self.name = name
        self.email = email
        self.openid = openid
        self.page = page
