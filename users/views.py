from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required

#------------------------------------------------------------------------------
def register(request):
    """ Display a registration form for the new user to sign up. If successful,
        go to the main screen and display a confirmation message. """

    # On initial screen display, show the blank registration form.
    if request.method == 'GET':
        return render(request, 'users/register.html', {'form':UserCreationForm()})
    else:
        # If the passwords match, continue with other checks.
        if request.POST['password1'] == request.POST['password2']:
            try:
                # Attempt to create a new user, using the credentials supplied
                # by the user.
                user = User.objects.create_user(request.POST['username'],
                                    email = request.POST['email'],
                                    password = request.POST['password1'])
                user.save()
                username = request.POST['username']
                messages.success(request,
                f'Welcome {username}, your account has been created!')
                return redirect('index')
            except IntegrityError:
                # Signup failed, as the supplied username already exists.
                return render(request, 'users/register.html', {'form':UserCreationForm(),
                        'error':'Username already exists - please choose another'})
        else:
            return render(request, 'users/register.html', {'form':UserCreationForm(),
                                                    'error':'Passwords did not match'})

#------------------------------------------------------------------------------
def login_user(request):
    """ Allow a user to log in, using a standard Django authentication form. """

    # On initial display of the screen, display the empty login form.
    if request.method == 'GET':
        return render(request, 'users/login.html', {'form':AuthenticationForm()})
    else:
        # Authenticate the user with their username and password.
        user = authenticate(request, username=request.POST['username'],
                                    password=request.POST['password'])
        # Either return an error message if credentials don't match, or login
        # the user if they do match.
        if user == None:
            return render(request, 'users/login.html', {'form':AuthenticationForm(),
                                    'error':'Username and password did not match'})
        else:
            login(request, user)
            return redirect('index')

#------------------------------------------------------------------------------
def logout_user(request):
    """ Log the current user out. """

    logout(request)
    messages.warning(request,'You have been logged out')
    return redirect('login')

#------------------------------------------------------------------------------
