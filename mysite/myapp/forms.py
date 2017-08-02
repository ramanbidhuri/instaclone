from django import forms
from models import UserModel, PostModel, LikeModel, CommentModel, Search, CommentLike


class SignUpForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields=['email','username','name','password']

class LoginForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['username', 'password']


class PostForm(forms.ModelForm):

    class Meta:
        model = PostModel
        fields = ['image', 'caption']


class LikeForm(forms.ModelForm):

    class Meta:
        model = LikeModel
        fields = ['post']


class CommentForm(forms.ModelForm):

    class Meta:
        model = CommentModel
        fields = ['comment_text', 'post']


class searchform(forms.ModelForm):
    class Meta:
        model = Search
        fields = ['category']


#Form for upvote functionality

class commentlikeform(forms.ModelForm):
    class Meta:
        model = CommentLike
        fields = ['comment','user']
