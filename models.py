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
    pw_hash = db.StringProperty(required=True)
    name = db.StringProperty()
    github = db.StringProperty()
    twitter = db.StringProperty()
    website = db.StringProperty()

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
        u = User(parent = users_key(),
                    username = username,
                    pw_hash = pw_hash,
                    email = email)
        u.put() 
        s = Settings(user = u.key())
        s.put()
        
    @classmethod
    def login(cls, username, pw):
        u = cls.by_name(username)
        if u and valid_pw(username, pw, u.pw_hash):
            return u

class TranscriptItem(db.Model):
    title = db.StringProperty(required=True)
    link = db.LinkProperty()
    date = db.DateProperty()
    content = db.TextProperty()
    owner = db.ReferenceProperty(User)
    category = db.CategoryProperty(choices=['project', 'course', 'book', 'opensource', 'meatspace'])

    @classmethod
    def by_username(cls, username):
        u = User.all().filter('username =', username).get()
        i = TranscriptItem.all().filter('owner =', u.key()).run()
        return i
    
class Settings(db.Model):
    link_color = db.StringProperty()
    sidebar_color = db.StringProperty()
    header_color = db.StringProperty()
    header_font = db.StringProperty()
    body_font = db.StringProperty()
    projects = db.BooleanProperty(default=False)
    courses = db.BooleanProperty(default=False)
    books = db.BooleanProperty(default=False)
    online = db.BooleanProperty(default=False)
    open_source = db.BooleanProperty(default=False)
    meatspace = db.BooleanProperty(default=False)
    user = db.ReferenceProperty(User, required=True)

    @classmethod
    def by_username(cls, username):
        u = User.all().filter('username =', username).get()
        s = Settings.all().filter('user =', u.key()).get()
        return s
