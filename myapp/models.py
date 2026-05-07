import datetime
import random
import string
from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from django.conf import settings
from django.utils import timezone


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    ]
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    is_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    user_permissions = models.ManyToManyField(
        Permission, related_name='custom_users', blank=True
    )
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.username

    def get_role_display_label(self):
        return dict(self.ROLE_CHOICES).get(self.role, 'Member')

    def is_admin_role(self):
        return self.role == 'admin' or self.is_superuser

    def is_manager_role(self):
        return self.role in ('admin', 'manager') or self.is_staff or self.is_superuser


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'


class Group(models.Model):
    CATEGORY_CHOICES = [
        ('ministry', 'Ministry'),
        ('fellowship', 'Fellowship'),
        ('youth', 'Youth'),
        ('women', "Women's Ministry"),
        ('men', "Men's Ministry"),
        ('children', 'Sunday School / Children'),
        ('choir', 'Choir'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='led_groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def member_count(self):
        return self.members.count()


class Member(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    phonenumber = models.CharField(max_length=15, blank=True)
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='members'
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f'{self.name or self.user.username}'

    def get_registered_events(self):
        return Events.objects.filter(attendee__user=self.user)


EVENT_CATEGORY_CHOICES = [
    ('service', 'Sunday Service'),
    ('revival', 'Revival / Crusade'),
    ('wedding', 'Wedding'),
    ('youth', 'Youth Event'),
    ('outreach', 'Community Outreach'),
    ('fundraiser', 'Fundraiser / Harambee'),
    ('seminar', 'Seminar / Conference'),
    ('anniversary', 'Church Anniversary'),
    ('baptism', 'Baptism / Communion'),
    ('prayer', 'Prayer Meeting / Vigil'),
    ('bible_study', 'Bible Study'),
    ('social', 'Social / Get-together'),
    ('other', 'Other'),
]


class Events(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField(default=datetime.time(9, 0))
    location = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=EVENT_CATEGORY_CHOICES, default='service')
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='events/', blank=True, null=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return self.title


class Attendee(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    phonenumber = models.CharField(max_length=15, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    is_urgent = models.BooleanField(default=False)
    image = models.ImageField(upload_to='announcements/', blank=True, null=True)

    class Meta:
        ordering = ['-date_posted']

    def __str__(self):
        return self.title


class Hymn(models.Model):
    number = models.IntegerField(unique=True)
    title = models.CharField(max_length=200)
    lyrics = models.TextField()
    author = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=20, default='English')

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"#{self.number} - {self.title}"


class ChatRoom(models.Model):
    ROOM_TYPES = [
        ('general', 'General Chat'),
        ('prayer', 'Prayer Requests'),
        ('announcements', 'Announcements'),
        ('group', 'Group Chat'),
    ]
    name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='general')
    description = models.CharField(max_length=200, blank=True)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def latest_messages(self, n=50):
        return self.messages.order_by('-created_at')[:n]


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]}"


class PushToken(models.Model):
    """Expo push notification token for mobile app users."""
    PLATFORM_CHOICES = [('android', 'Android'), ('ios', 'iOS')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='push_tokens')
    token = models.CharField(max_length=200, unique=True)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES, default='android')
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.platform})"


class RoleRequest(models.Model):
    """A user requesting a role upgrade (member → manager → admin)."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='role_requests')
    requested_role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    reason = models.TextField(help_text='Why do you need this access level?')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_requests'
    )
    review_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.requested_role} ({self.status})"


class OTPCode(models.Model):
    PURPOSE_CHOICES = [
        ('phone', 'Phone Verification'),
        ('email', 'Email Verification'),
        ('login', 'Login OTP'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True
    )
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES, default='phone')
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        expiry = self.created_at + datetime.timedelta(minutes=10)
        return not self.is_used and timezone.now() < expiry

    @classmethod
    def generate_code(cls):
        return ''.join(random.choices(string.digits, k=6))

    def __str__(self):
        return f"OTP {self.code} for {self.phone or self.email}"


class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    PAYMENT_PURPOSE = [
        ('tithe', 'Tithe'),
        ('offering', 'Offering'),
        ('project', 'Project'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    purpose = models.CharField(max_length=20, choices=PAYMENT_PURPOSE, default='offering')
    mpesa_receipt_number = models.CharField(max_length=50, blank=True)
    mpesa_transaction_id = models.CharField(max_length=50, blank=True)
    checkout_request_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment KES {self.amount} - {self.purpose} ({self.status})"


class Media(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    details = models.TextField(blank=True)
    file = models.FileField(upload_to='media/%Y/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


MEDIA_CATEGORY_CHOICES = [
    ('service', 'Sunday Service'),
    ('sermon', 'Sermon'),
    ('wedding', 'Wedding'),
    ('youth', 'Youth Event'),
    ('outreach', 'Community Outreach'),
    ('fundraiser', 'Fundraiser / Harambee'),
    ('choir', 'Choir / Music'),
    ('anniversary', 'Church Anniversary'),
    ('baptism', 'Baptism / Communion'),
    ('prayer', 'Prayer Meeting'),
    ('bible_study', 'Bible Study'),
    ('celebration', 'Celebration / Party'),
    ('general', 'General'),
]


class Images(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/%Y/')
    category = models.CharField(max_length=20, choices=MEDIA_CATEGORY_CHOICES, default='general')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Images'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title


class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    details = models.TextField(blank=True)
    video = models.FileField(upload_to='videos/%Y/', blank=True)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=20, choices=MEDIA_CATEGORY_CHOICES, default='sermon')
    youtube_url = models.URLField(blank=True, help_text='YouTube/streaming URL (alternative to file upload)')

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title
