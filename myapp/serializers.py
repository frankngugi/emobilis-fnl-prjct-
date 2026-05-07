from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    CustomUser, Events, Attendee, Announcement, Hymn,
    Group, Member, Images, Video, Payment, RoleRequest, UserProfile
)

User = get_user_model()


# ── Auth ─────────────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return data

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already taken.')
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            password=validated_data['password'],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'phone', 'role', 'is_staff', 'is_superuser',
            'is_verified', 'is_phone_verified', 'is_email_verified',
            'date_joined', 'profile_picture',
        ]
        read_only_fields = ['id', 'date_joined', 'is_staff', 'is_superuser', 'role']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        try:
            profile = obj.userprofile
            if profile.profile_picture and request:
                return request.build_absolute_uri(profile.profile_picture.url)
        except Exception:
            pass
        return None


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone']


# ── Announcements ─────────────────────────────────────────────────────────────

class AnnouncementSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'posted_by_name', 'date_posted', 'is_urgent', 'image_url']

    def get_posted_by_name(self, obj):
        return obj.posted_by.get_full_name() or obj.posted_by.username

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class AnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'is_urgent', 'image']


# ── Events ────────────────────────────────────────────────────────────────────

class EventSerializer(serializers.ModelSerializer):
    organizer_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    attendee_count = serializers.SerializerMethodField()
    is_registered = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()

    class Meta:
        model = Events
        fields = [
            'id', 'title', 'description', 'date', 'time', 'location',
            'category', 'category_display', 'organizer_name',
            'image_url', 'attendee_count', 'is_registered',
        ]

    def get_organizer_name(self, obj):
        return obj.organizer.get_full_name() or obj.organizer.username

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_attendee_count(self, obj):
        return obj.attendee_set.count()

    def get_is_registered(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.attendee_set.filter(user=request.user).exists()
        return False

    def get_category_display(self, obj):
        return obj.get_category_display()


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Events
        fields = ['title', 'description', 'date', 'time', 'location', 'category', 'image']


# ── Hymns ─────────────────────────────────────────────────────────────────────

class HymnListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hymn
        fields = ['id', 'number', 'title', 'author', 'category', 'language']


class HymnDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hymn
        fields = ['id', 'number', 'title', 'author', 'category', 'language', 'lyrics']


# ── Groups ────────────────────────────────────────────────────────────────────

class GroupSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    leader_name = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            'id', 'name', 'description', 'category', 'category_display',
            'leader_name', 'member_count', 'is_member', 'created_at',
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_leader_name(self, obj):
        if obj.leader:
            return obj.leader.get_full_name() or obj.leader.username
        return None

    def get_category_display(self, obj):
        return obj.get_category_display()

    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.members.filter(user=request.user).exists()
        return False


# ── Gallery ───────────────────────────────────────────────────────────────────

class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()

    class Meta:
        model = Images
        fields = ['id', 'title', 'category', 'category_display', 'image_url', 'uploaded_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_category_display(self, obj):
        return obj.get_category_display()


# ── Videos ───────────────────────────────────────────────────────────────────

class VideoSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'category', 'category_display',
            'video_url', 'youtube_url', 'uploaded_at',
        ]

    def get_video_url(self, obj):
        request = self.context.get('request')
        if obj.video and request:
            try:
                return request.build_absolute_uri(obj.video.url)
            except Exception:
                pass
        return None

    def get_category_display(self, obj):
        return obj.get_category_display()


# ── Payments ──────────────────────────────────────────────────────────────────

class PaymentSerializer(serializers.ModelSerializer):
    purpose_display = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'phone_number', 'purpose', 'purpose_display',
            'status', 'mpesa_receipt_number', 'created_at',
        ]
        read_only_fields = ['id', 'status', 'mpesa_receipt_number', 'created_at']

    def get_purpose_display(self, obj):
        return obj.get_purpose_display()


class PaymentInitiateSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=10)
    purpose = serializers.ChoiceField(choices=['tithe', 'offering', 'project', 'other'])


# ── Dashboard Stats ───────────────────────────────────────────────────────────

class DashboardStatsSerializer(serializers.Serializer):
    total_members = serializers.IntegerField()
    total_events = serializers.IntegerField()
    total_groups = serializers.IntegerField()
    total_payments = serializers.IntegerField()
    recent_payments = PaymentSerializer(many=True)
    recent_members = UserSerializer(many=True)
