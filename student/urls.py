from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('course/', views.course, name='course'),
    path('addcourse/', views.add_course, name='add_course'),
    path('purchasecourse/', views.purchase_course, name='purchase_course'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'), 
]

