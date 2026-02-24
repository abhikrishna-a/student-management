from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views( here.
def student_dashboard(request):
    return render(request, 'student/student_dashboard.html')
def profile(request):
    return render(request, 'student/profile.html')
def course(request):
    return render(request, 'student/course.html')

def add_course(request):
    return render(request, 'student/addcourse.html')

def login_view(request):
    return render(request, 'student/login.html')

def purchase_course(request):
    return render(request, 'student/purchasecourse.html')
def logout_view(request):
    """
    Log out the user and redirect to login page with a success message
    """
    logout(request)
    messages.success(request, 'You have been successfully logged out!')
    return redirect('login')  # Make sure you have a login URL named 'login'