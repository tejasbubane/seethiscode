#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
##########################################################################

# By: Tejas Bubane (tejasbubane@gmail.com, twitter username: tejas_bubane)
# This is my independent project to create a webapp to paste and share codesnippets
# Done as a follow-up to the Udacity CS253 course
# Name of the app is "SeeThisCode" :)

import os
import webapp2

import jinja2 #reference: http://jinja.pocoo.org/docs/

from google.appengine.ext import db #reference: https://developers.google.com/appengine/docs/python/datastore/

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class Post(db.Model):
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	lang = db.StringProperty()
	name = db.StringProperty()

class NewPost(Handler):
	def render_newpost(self, name="", content="", error=""):
		self.render("newpost.html", name=name, content=content, error=error)

	def get(self):
		self.render_newpost()

	def post(self):
		name = self.request.get("name")
		content = self.request.get("content")
		lang = self.request.get("lang")
		if content:
			if not name:
				name = "Untitled"
			p = Post(name=name, content=content, lang=lang)
			p.put()
			KEY = p.key().id()
			self.redirect("/"+str(KEY), str(KEY))
		else:
			error = "content, please!"
			self.render_newpost(name, content, error)

class SpecificPost(Handler):
	def get(self, key):
		post = Post.get_by_id(int(key))
		self.render("success.html", post=post)

class MainPage(Handler):
	def render_blog(self, posts):
		self.render("blog.html", posts=posts)

	def get(self):
		posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
		self.render_blog(posts)

app = webapp2.WSGIApplication([('/', MainPage), ('/newpost', NewPost), (r'/(\d+)', SpecificPost)], debug=True)