from django.urls import path
from . import api
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('test/', views.test),
    path('list/', api.Dlist, name='dht-list'),
    path('post/', api.dht_post, name='dht-post'),
]