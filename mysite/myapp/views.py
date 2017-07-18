# -*- coding: utf-8 -*-
from django.shortcuts import render
from forms import SignUpForm

# Create your views here.

def signup_view(request):
    if request.method == "POST":
        print 'Sign up form submitted'
    elif request.method == 'GET':
        form = SignUpForm()

    return render(request, 'index.html', {'form' : form})

