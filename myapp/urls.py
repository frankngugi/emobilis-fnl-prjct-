from django import urls
from django.urls import path, include
from . import views
from django.contrib import admin
from django.contrib.auth.views import LogoutView, LoginView



 
urlpatterns = [
    
    path('base', views.base, name= 'base'),
    path('', views.index, name= 'index'),
    path('gallery', views.images, name= 'gallery'),
    path('chats', views.chats, name= 'chats'),
    path('register', views.register, name='register' ),
    path('login', views.login, name='login' ),
    path('adminlogin', views.adminlogin, name='adminlogin' ),
    path('userlogin', views.userlogin, name='userlogin' ),
    path('logout', views.logout, name='logout'),
    path('adminn/logout', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('group_change/', views.group_change, name='group_change'),    
    path('user_events/', views.user_events, name='user_events'),
    path('adminn/events', views.events, name='events_list'),
    #for user profile update
    # path('update_profile/', views.UserUpdateFormView.as_view(),name="update_profile"),  
    # path('uploadprofimage/', views.uploadprofimage, name='uploadprofimage'),
    path('video', views.video, name='video'),
    path('events', views.event, name='events'),
    path('adminn/', views.adminn, name='adminn'),
    path('adminn/uploadimages', views.uploadimages, name='uploadimages'),
    path('adminn/uploadfiles', views.uploadfiles, name='uploadfiles'),
    path('adminn/uploadvideos', views.uploadvideos, name='uploadvideos'),
    path('contribute', views.contribute, name='contribute'),
    path('change_password', views.change_password, name='change_password'),
    path('adminn/addevents', views.addevents, name='addevents'),
    path('adminn/events/', views.events, name='events'),
    path('adminn/events/', views.event, name='events'),
    path('adminn/group', views.group_management, name='group_management'),
    path('adminn/groups', views.group_list, name='group'),
    path('adminn/groups', views.group_add, name='group_add'),
    path('adminn/groups/<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('adminn/groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
    
    path('create_group', views.create_group, name='create_group'),
    path('join_group', views.join_group, name='join_group'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),

    path('adminn/userreports', views.user_report, name='user_report'),

    path('register_event/<int:event_id>/', views.register_event, name='register_event'),

    # path('payment_form', views.intasend_view, name='payment_form'),


]