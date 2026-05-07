from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views

urlpatterns = [
    # Auth
    path('auth/login/', api_views.LoginView.as_view(), name='api_login'),
    path('auth/register/', api_views.RegisterView.as_view(), name='api_register'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('auth/profile/', api_views.ProfileView.as_view(), name='api_profile'),
    path('auth/change-password/', api_views.ChangePasswordView.as_view(), name='api_change_password'),

    # Announcements
    path('announcements/', api_views.AnnouncementListView.as_view(), name='api_announcements'),
    path('announcements/create/', api_views.AnnouncementCreateView.as_view(), name='api_announcement_create'),

    # Events
    path('events/', api_views.EventListView.as_view(), name='api_events'),
    path('events/create/', api_views.EventCreateView.as_view(), name='api_event_create'),
    path('events/<int:event_id>/register/', api_views.register_for_event, name='api_register_event'),
    path('events/<int:event_id>/unregister/', api_views.unregister_from_event, name='api_unregister_event'),
    path('events/my/', api_views.my_events, name='api_my_events'),

    # Hymns
    path('hymns/', api_views.HymnListView.as_view(), name='api_hymns'),
    path('hymns/<int:pk>/', api_views.HymnDetailView.as_view(), name='api_hymn_detail'),

    # Bible
    path('bible/', api_views.bible_verse, name='api_bible'),

    # Groups
    path('groups/', api_views.GroupListView.as_view(), name='api_groups'),
    path('groups/create/', api_views.GroupCreateView.as_view(), name='api_group_create'),
    path('groups/<int:pk>/', api_views.GroupDetailView.as_view(), name='api_group_detail'),
    path('groups/<int:group_id>/join/', api_views.join_group, name='api_join_group'),

    # Gallery & Videos
    path('gallery/', api_views.ImageListView.as_view(), name='api_gallery'),
    path('videos/', api_views.VideoListView.as_view(), name='api_videos'),

    # Payments
    path('payments/', api_views.PaymentListView.as_view(), name='api_payments'),
    path('payments/initiate/', api_views.initiate_payment, name='api_initiate_payment'),

    # Admin
    path('admin/dashboard/', api_views.admin_dashboard, name='api_dashboard'),
    path('admin/members/', api_views.all_members, name='api_all_members'),
    path('admin/members/<int:user_id>/role/', api_views.update_user_role, name='api_update_role'),

    # Metadata
    path('categories/', api_views.categories_meta, name='api_categories'),
]
