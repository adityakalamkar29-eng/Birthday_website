from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_page, name='create_page'),
    path('admin-portal/', views.admin_portal, name='admin_portal'),
    path('<str:dob>/manage/', views.manage_page, name='manage_page'),
    path('<str:dob>/', views.birthday_page, name='birthday_page'),
]
