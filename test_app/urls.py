from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home_page'),
    path('students/', views.students_all, name='students_all'),
    path('student/<int:pk>/classes/', views.student_classes, name='student_classes'),
    path('student/<int:pk>/performance/', views.student_performance, name='student_performance'),
    path('classes/', views.all_classes, name='all_classes'),
    path('class/<int:pk>/students/', views.student_took_course, name='student_took_course'),
    path('class/<int:pk>/performance/', views.class_based_performance, name='class_based_performance'),
    path('class/<int:pk>/student/<int:pk_alt>/', views.class_student, name='class_student'),
    path('student/<int:pk>/class/<int:pk_alt>/', views.class_student, name='class_student'),
    path('class/<int:pk>/final-grade-sheet/', views.final_grade_sheet, name='final_grade_sheet'),
]