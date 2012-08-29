from google.appengine.ext import db
import bcrypt

def make_pw_hash(username, pw, salt = None):
    if not salt:
        salt = bcrypt.gensalt(5)
    h = bcrypt.hashpw(username + pw, salt)
    return '%s,%s' % (h, salt)

    
def valid_pw(username, pw, h):
    return h == bcrypt.hashpw(username + pw, h.split(',')[1])

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

class User(db.Model):
    username = db.StringProperty(required=True)
    email = db.EmailProperty()
    pw_hash = db.StringProperty()
    name = db.StringProperty()
    github = db.StringProperty()
    twitter = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, username):
        u = User.all().filter('username =', username).get()
        return u
    
    @classmethod
    def register(cls, username, pw, email = None):
        pw_hash = make_pw_hash(username, pw)
        return User(parent = users_key(),
                    username = username,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, username, pw):
        u = cls.by_name(username)
        if u and valid_pw(username, pw, u.pw_hash):
            return u

class TranscriptItem(db.Model):
    title = db.StringProperty(required=True)
    link = db.LinkProperty()
    date = db.DateProperty(required=True)
    content = db.TextProperty()
    owner = db.ReferenceProperty(User)

class Project(TranscriptItem):
    pass

class Course(TranscriptItem):
    pass

class Book(TranscriptItem):
    pass

class OpenSource(TranscriptItem):
    pass

class Online(TranscriptItem):
    pass
    
class Settings(db.Model):
    link_color = db.StringProperty()
    sidebar_color = db.StringProperty()
    header_color = db.StringProperty()
    header_font = db.StringProperty()
    body_font = db.StringProperty()
    owner = db.ReferenceProperty(User)
