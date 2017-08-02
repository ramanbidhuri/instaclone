# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm, searchform, commentlikeform
from models import UserModel, SessionToken, PostModel, LikeModel, CommentModel, CommentLike, Search
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from mysite.settings import BASE_DIR
from datetime import timedelta, datetime
from django.utils import timezone
from django.contrib import messages
from imgurpython import ImgurClient
from clarifai import rest
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage


YOUR_CLIENT_ID = "d040607f57981aa"                                #client id of imgur

YOUR_CLIENT_SECRET = "512fde2b320d94a5eb51bf146dc71355870ea6bd"   #client secret of imgur

#to signup for instaclone

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # saving data to DB
            user = UserModel(name=name, password=make_password(password), email=email, username=username)
            user.save()
            return render(request, 'success.html')
            # return redirect('login/')
        else:
            form = SignUpForm()

    elif request.method == "GET":
        form = SignUpForm()
        today = datetime.now()

    return render(request, 'index.html', {'form': form})


#login to get access to instaclone

def login_view(request):
    response_data = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = UserModel.objects.filter(username=username).first()

            if user:
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    response_data['message'] = 'Incorrect Password! Please try again!'

    elif request.method == 'GET':
        form = LoginForm()

    response_data['form'] = form
    return render(request, 'login.html', response_data)


# For posting media

def post_view(request):
    user = check_validation(request)

    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()


                path = str(BASE_DIR + "/" + post.image.url)

                client = ImgurClient(YOUR_CLIENT_ID, YOUR_CLIENT_SECRET)
                post.image_url = client.upload_from_path(path, anon=True)['link']
                print(post.image_url)
                post.save()

                app = ClarifaiApp(api_key='ecc5aea7265040b4b320b3446f96152c')
                model = app.models.get('general-v1.3')
                response = model.predict_by_url(url=post.image_url)

                arr = response['outputs'][0]['data']['concepts']
                for i in range(0, 10):
                    category = arr[i]['name']
                    print category
                    if category == 'nature':
                        post.category = category

                        break
                    elif category == 'technology':
                        post.category = category

                        break
                    elif category == 'food':
                        post.category = category
                        break
                    elif category == 'sports':
                        post.category = category

                        break
                    elif category == 'vehicle':
                        post.category = category

                return redirect('/feed/')

        else:
            form = PostForm()
        return render(request, 'post.html', {'form': form})
    else:
        return redirect('/login/')


def feed_view(request):
    user = check_validation(request)
    if user:

        posts = PostModel.objects.all().order_by('created_on')

        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True

        return render(request, 'feed.html', {'posts': posts})
    else:

        return redirect('/login/')


# to like a post

def like_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)

            else:
                existing_like.delete()
            return redirect('/feed/')
    else:
        return redirect('/login/')


#to comment on a post

def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            return redirect('/feed/')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login')


# For validating the session

def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            time_to_live = session.created_on + timedelta(days=1)
            if time_to_live > timezone.now():
                return session.user
    else:
        return None

# for logging out the current user and deleting the session token


def logout_view(request):
    user = check_validation(request)
    if user is not None:
        latest_session = SessionToken.objects.filter(user=user).last()
        if latest_session:
            latest_session.delete()

    return redirect("/login/")


def search_view(request):
    return render(request, 'search.html', {'form': form})


def search1_view(request):

    user = check_validation(request)
    if user and request.method == 'POST':
        form = searchform(request.POST)
        if form.is_valid():
            search = request.POST('search')
            print search
            return render('/login/')  # Redirect after POST


#for upvote functionality


def commentlike_view(request):

    user = check_validation(request)
    if user and request.method == 'POST':
        form = commentlikeform(request.POST)
        if form.is_valid():
            comment_id = form.cleaned_data.get('comment').id

            existing_like = CommentLike.objects.filter(comment_id=comment_id, user=user).first()

            if not existing_like:
                CommentLike.objects.create(comment_id=comment_id, user=user)
            else:
                existing_like.delete()

            return redirect('/feed/')

    else:
        return redirect('/login/')
