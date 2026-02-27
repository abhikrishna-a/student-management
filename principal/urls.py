from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',                    views.principal_dashboard, name='principal_dashboard'),
    path('students/',                     views.view_students,       name='view_students'),
    path('students/<int:pk>/',            views.student_detail,      name='student_detail'),
    path('courses/',                      views.view_courses,        name='view_courses'),
    path('courses/add/',                  views.add_course,          name='add_course'),
    path('courses/delete/<int:pk>/',      views.delete_course,       name='delete_course'),
    path('courses/approve/<int:pk>/',     views.approve_course,      name='approve_course'),
    path('courses/reject/<int:pk>/',      views.reject_course,       name='reject_course'),
]