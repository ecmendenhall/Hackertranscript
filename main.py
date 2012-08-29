#!/usr/bin/env python
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "lib/bcrypt"))

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from models import User, Settings
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
        pass_re = re.compile(r"^.{8,25}$")
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

        #Check if user already exists
        u = User.by_name(self.username)
        if u:
            params['username_error'] = 'That user already exists.'
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
        User.register(self.username, self.password, self.email)
        
        #self.login(u)
        self.redirect('/' + self.username)


class Edit(CustomHandler):
    def get(self, username):

        #Check if user exists
        u = User.by_name(username)
        if not u:
            self.response.out.write('404 Not Found')

        else:
            params = { 'name': u.name,
                       'twitter': u.twitter,
                       'github': u.github,
                       'website': u.website }
            
            s = Settings.by_username(username)
            if s:
                params['linkcolor'] = s.link_color
                params['sidebarcolor'] = s.sidebar_color
                params['headercolor'] = s.header_color
                params['headerfont'] = s.header_font
                params['bodyfont'] = s.body_font 

            self.render('edit.html', **params)

    def post(self, username):
        self.name = self.request.get('name')
        self.twitter = self.request.get('twitter')
        self.github = self.request.get('github')
        self.website = self.request.get('website')
        
        u = User.by_name(username)
        u.name = self.name
        u.twitter = self.twitter
        u.github = self.github
        u.website = self.website
        u.put()

        self.linkcolor = self.request.get('linkcolor')
        self.sidebarcolor = self.request.get('sidebarcolor')
        self.headercolor = self.request.get('headercolor')
        self.headerfont = self.request.get('headerfont')
        self.bodyfont = self.request.get('bodyfont')
        
        s = Settings.by_username(username)
        s.link_color = self.linkcolor
        s.sidebar_color = self.sidebarcolor
        s.header_color = self.headercolor
        s.header_font = self.headerfont
        s.body_font = self.bodyfont
        s.put()


        
        self.redirect('/' + username)

      

class Transcript(CustomHandler):
    def get(self, username):
        
        #Check if user exists
        u = User.by_name(username)
        if not u:
            self.response.out.write('404 Not Found')

        else:
            params = { 'username': u.username,
                       'name': u.name,
                       'twitter': u.twitter,
                       'github': u.github,
                       'website': u.website }
            self.render('transcript.html', **params)


app = webapp2.WSGIApplication([webapp2.Route('/', Main),
                               webapp2.Route('/signin', SignIn),
                               webapp2.Route('/signup', SignUp),
                               webapp2.Route('/finish', FinishSignUp),
                               webapp2.Route('/<username>', Transcript),
                               webapp2.Route('/<username>/edit', Edit)],
                              debug=True)
