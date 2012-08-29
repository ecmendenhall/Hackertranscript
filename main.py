#!/usr/bin/env python

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from models import User
import jinja2
import webapp2
import os
import re

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class CustomHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        #params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class SignInHandler(CustomHandler):    
    def valid_username(self, username):
        user_re = re.compile(r"^[a-zA-Z0-9_-]{3,25}$")
        return username and user_re.match(username)
    
    def valid_password(self, password):
        pass_re = re.compile(r"^.{3,25}$")
        return password and pass_re.match(password)

    def valid_email(self, email):
        email_re = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
        return not email or email_re.match(email)

class Main(CustomHandler):
    def get(self):
        self.render('index.html')

class SignIn(SignInHandler):
    def get(self):
        self.response.out.write('This is the sign in page!')

    def post(self):
        self.response.out.write('This is the sign in page!')

class SignUp(SignInHandler):            
    def post(self):
        error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')

        params = { 'username':self.username,
                   'password':self.password }

        if not self.valid_username(self.username):
            params['username_error'] = "That's not a valid username."
            error = True

        if not self.valid_password(self.password):
            params['password_error'] = "That wasn't a valid password."
            error = True
        
        if error:
            self.render('index.html', **params)
        else:
            self.render('signup.html', **params)

class FinishSignUp(SignInHandler):
    def post(self):
        error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')
        
        params = { 'username':self.username,
                   'password':self.password,
                   'email':self.email }

        if self.password != self.verify:
            params['verify_error'] = "Your passwords didn't match."
            error = True

        if not self.valid_email(self.email):
            params['email_error'] = "That's not a valid email."
            error = True

        if error:
            self.render('signup.html', **params)
        else:
            self.done()

    def done(self):
        #Check if user already exists
        u = User.by_name(self.username)
        if u:
            username_error = 'That user already exists.'
            self.render('signup.html', username_error = username_error)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            #self.login(u)
            self.redirect('/')


class Edit(CustomHandler):
    def get(self):
        self.response.out.write('Hello world!')

class Transcript(CustomHandler):
    def get(self):
        self.response.out.write('This is a transcript page!')

app = webapp2.WSGIApplication([('/', Main),
                               ('/signin', SignIn),
                               ('/signup', SignUp),
                               ('/finish', FinishSignUp),
                               ('/transcript', Transcript)],
                              debug=True)
