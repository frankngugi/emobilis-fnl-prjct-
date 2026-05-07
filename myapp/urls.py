from django.urls import path
from . import views

urlpatterns = [
    # Core pages
    path('', views.index, name='index'),
    path('base/', views.base, name='base'),

    # Authentication
    path('login', views.login_view, name='login'),
    path('register', views.register_view, name='register'),
    path('logout', views.logout_view, name='logout'),
    path('switch-portal/<str:portal>/', views.switch_portal, name='switch_portal'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('verify-email/notice/', views.verify_email_notice, name='verify_email_notice'),
    path('send-phone-otp/', views.send_phone_otp, name='send_phone_otp'),
    path('verify-phone/', views.verify_phone, name='verify_phone'),

    # Profile
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),

    # Announcements
    path('announcements/', views.announcements, name='announcements'),
    path('announcements/add/', views.add_announcement, name='add_announcement'),
    path('announcements/<int:pk>/delete/', views.delete_announcement, name='delete_announcement'),

    # Hymns
    path('hymns/', views.hymns, name='hymns'),
    path('api/hymns/', views.hymns_api, name='hymns_api'),

    # Bible
    path('bible/', views.bible, name='bible'),

    # Events
    path('events', views.event_list, name='events'),
    path('events/register/<int:event_id>/', views.register_event, name='register_event'),
    path('user-events/', views.user_events, name='user_events'),

    # Groups
    path('groups/', views.group_list, name='groups'),
    path('groups/<int:pk>/', views.group_detail, name='group_detail'),
    path('create-group/', views.create_group, name='create_group'),
    path('join-group/', views.join_group, name='join_group'),
    path('group-change/', views.group_change, name='group_change'),

    # Media
    path('gallery', views.images, name='gallery'),
    path('video', views.video, name='video'),
    path('chats', views.chats, name='chats'),

    # Contributions / M-Pesa
    path('contribute', views.contribute, name='contribute'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),

    # Admin portal
    path('adminn/', views.adminn, name='adminn'),
    path('adminn/uploadimages', views.uploadimages, name='uploadimages'),
    path('adminn/uploadfiles', views.uploadfiles, name='uploadfiles'),
    path('adminn/uploadvideos', views.uploadvideos, name='uploadvideos'),
    path('adminn/addevents', views.addevents, name='addevents'),
    path('adminn/groups', views.group_list, name='group_management'),
    path('adminn/groups/<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('adminn/groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
    path('adminn/userreports', views.user_report, name='user_report'),

    # Community Chat
    path('chats', views.chat_view, name='chats'),
    path('chats/send/<int:room_id>/', views.send_chat_message, name='send_chat_message'),
    path('chats/messages/<int:room_id>/', views.get_chat_messages, name='get_chat_messages'),

    # User role management (admin only)
    path('adminn/manage-users/', views.manage_users, name='manage_users'),
    path('adminn/manage-users/<int:user_id>/change-role/', views.change_user_role, name='change_user_role'),
    path('adminn/role-requests/<int:request_id>/<str:action>/', views.approve_role_request, name='approve_role_request'),

    # User-facing role upgrade request
    path('request-role/', views.request_role_upgrade, name='request_role_upgrade'),
]
