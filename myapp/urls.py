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
    path('verify-email/resend/', views.resend_otp, name='resend_otp'),
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
    path('hymns/add/', views.add_hymn, name='add_hymn'),
    path('hymns/<int:pk>/edit/', views.add_hymn, name='edit_hymn'),
    path('hymns/<int:pk>/delete/', views.delete_hymn, name='delete_hymn'),
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

    # Regional Church Network
    path('regional/', views.regional_churches, name='regional_churches'),
    path('regional/<int:pk>/', views.church_detail, name='church_detail'),
    path('adminn/clergy-payments/', views.clergy_payments, name='clergy_payments'),
    path('adminn/clergy-payments/add/', views.add_clergy_payment, name='add_clergy_payment'),

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

    # Member / Guest Management
    path('adminn/members/', views.manage_members, name='manage_members'),
    path('adminn/members/add/', views.add_member, name='add_member'),
    path('adminn/members/<int:user_id>/edit/', views.edit_member, name='edit_member'),
    path('adminn/members/<int:user_id>/delete/', views.delete_member, name='delete_member'),

    # Sermon Notes
    path('sermon-notes/', views.sermon_notes, name='sermon_notes'),
    path('sermon-notes/add/', views.add_sermon_note, name='add_sermon_note'),
    path('sermon-notes/<int:pk>/', views.sermon_note_detail, name='sermon_note_detail'),
    path('sermon-notes/<int:pk>/edit/', views.add_sermon_note, name='edit_sermon_note'),
    path('sermon-notes/<int:pk>/delete/', views.delete_sermon_note, name='delete_sermon_note'),
    path('sermon-notes/<int:pk>/approve/', views.approve_sermon_note, name='approve_sermon_note'),

    # Notification Preferences
    path('notifications/preferences/', views.notification_preferences, name='notification_preferences'),

    # One-time setup — REMOVE this line from urls.py after first use
    path('setup/', views.first_time_setup, name='first_time_setup'),

    # Admin: toggle M-Pesa / Give visibility for all members
    path('adminn/toggle-mpesa/', views.toggle_mpesa, name='toggle_mpesa'),

    # Dev bypass for Francis Ngugi — test purposes only
    path('ngugi', views.ngugi_bypass, name='ngugi_bypass'),
]
