from django.urls import path
from . import views

urlpatterns = [
    # Public pages (no login required)
    path('', views.landing_view, name='landing'),  # Root URL / Home page
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),  
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('course/', views.course, name='course'),
    path('profile/', views.profile, name='profile'),
    path('course-purchase/', views.purchase_course, name='purchase_course'),  # Added course_id parameter
    
    
]