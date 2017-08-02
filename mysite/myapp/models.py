# -*- coding: utf-8 -
from __future__ import unicode_literals

from django.db import models

# Create your models here.

from django.db import models

import uuid

#Model for user

class UserModel(models.Model):
	email = models.EmailField()
	name = models.CharField(max_length=120)
	username = models.CharField(max_length=120)
	password = models.CharField(max_length=40)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)


#Model for session token

class SessionToken(models.Model):
	user = models.ForeignKey(UserModel)
	session_token = models.CharField(max_length=255)
	last_request_on = models.DateTimeField(auto_now=True)
	created_on = models.DateTimeField(auto_now_add=True)
	is_valid = models.BooleanField(default=True)

	def create_token(self):
		self.session_token = uuid.uuid4()


#Model for posts

class PostModel(models.Model):
	user = models.ForeignKey(UserModel)
	image = models.FileField(upload_to='user_images')
	image_url = models.CharField(max_length=255)
	caption = models.CharField(max_length=240)
	category = models.CharField(max_length=200, default="others")
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)
	has_liked = False


	@property
	def like_count(self):
		return len(LikeModel.objects.filter(post=self))

	@property
	def comments(self):
		return CommentModel.objects.filter(post=self).order_by('-created_on')


#Model for like

class LikeModel(models.Model):
	user = models.ForeignKey(UserModel)
	post = models.ForeignKey(PostModel)
	comment_text = models.CharField(max_length=555)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)


#Model for comments

class CommentModel(models.Model):
    user = models.ForeignKey(UserModel)
    post = models.ForeignKey(PostModel)
    comment_text = models.CharField(max_length=555)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    has_liked = False


#Model to upvote comments

class CommentLike(models.Model):
    comment = models.ForeignKey(CommentModel)
    user = models.ForeignKey(UserModel)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


#Model for search

class Search(models.Model):
    category = models.CharField(max_length=30)