"""
URL configuration for weather project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from restapp.views import *
from rest_framework_jwt.views import obtain_jwt_token,refresh_jwt_token,verify_jwt_token
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/weather/',weatherapi.as_view(),name='api'),
    path('weather/',weather,name="weather"),
    path('sendotp/',send_otp),
    path('',register),
    path('usersapi/',usersapi.as_view()),
    path('get-jwt-token/',obtain_jwt_token),
    path('verify-jwt-token/',verify_jwt_token),
    path('login/',login_view,name='login'),
    path('weatheruser/',weatheruser,name='weatheruser'),
    path('logout/',logout_view,name='logout'),
    path('update/',update,name='update'),
    path('userweatherdata/',userweatherdata,name='userweatherdata')
]
