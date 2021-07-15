from django.urls import path
from . import views

urlpatterns = [
    #path('', views.home, name='home'),
    path('students/', views.students_all, name='students_all'),
    path('student/<int:pk>/classes/', views.student_classes, name='student_classes'),
    path('student/<int:pk>/performance/', views.student_performance, name='student_performance'),
    path('classes/', views.all_classes, name='all_classes'),
    path('classes/<int:pk>/', views.student_took_course, name='student_took_course'),
    path('classes/<int:pk>/performance/', views.class_based_performance, name='class_based_performance'),
    path('class/<int:pk>/student/<int:pk_alt>/', views.class_student, name='class_student'),
#     path('customer/<str:pk_test>', views.customer, name='customer'),
#     path('create_order/<str:pk>/', views.createOrder, name='create_order'),
#     path('update_order/<str:pk>/', views.updateOrder, name='update_order'),
#     path('delete_order/<str:pk>/', views.deleteOrder, name='delete_order'),
#     path('register/', views.registerPage, name='register'),
#     path('login/', views.loginPage, name='login'),
]