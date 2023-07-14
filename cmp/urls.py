"""
URL configuration for cmp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('api/create_template/', views.create_template, name='create_template'),
    path('api/create_container/', views.create_container, name='create_container'),
    path('api/update_bolehkan_container/', views.update_bolehkan, name='update_bolehkan'),
    path('api/delete_template/', views.delete_template, name='delete_template'),
    path('api/delete_kontainer/', views.delete_kontainer, name='delete_kontainer'),
    path('api/executeCommand/', views.execute_command, name='execute_command'),
]
