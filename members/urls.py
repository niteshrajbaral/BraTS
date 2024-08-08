# members/urls.py
from django.urls import path
from .views import home, result, signup_view, login_view, logout_view,success_view
from . import views

urlpatterns = [
    path('', home, name='home'),
    path('result/', result, name='result'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('success/', success_view, name='success'),
    path('success_page/', views.success_page, name='success_page'),
]
