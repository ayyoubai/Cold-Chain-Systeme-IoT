from django.urls import path
from . import api, views
urlpatterns = [
    path('', views.dashboard, name='incidents-dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('incidents/create/', views.incident_create, name='incident-create'),
    path('incidents/<int:pk>/', views.incident_detail, name='incident-detail'),
    path('incidents/<int:pk>/acknowledge/', views.acknowledge_incident, name='incident-acknowledge'),
    path('incidents/<int:pk>/status/', views.update_status, name='incident-status'),
    path('incidents/<int:pk>/archive/', views.archive_incident, name='incident-archive'),
    path('archives/', views.archives, name='incident-archives'),
    path('operators/', views.operators, name='operators'),
    path('operators/<int:pk>/toggle/', views.operator_toggle, name='operator-toggle'),
    path('operators/<int:pk>/edit/', views.operator_edit, name='operator-edit'),
    path('incidents/<int:pk>/summary/', views.summary_api, name='incident-summary'),
    path('monitoring/', views.sensor_dashboard, name='sensor-dashboard'),
    path('test/', views.test, name='test'),
    path('list/', api.Dlist, name='dht-list'),
    path('post/', api.dht_post, name='dht-post'),
]
