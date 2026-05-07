from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    CustomUser, UserProfile, Events, Attendee, Group, Member,
    Announcement, Hymn, OTPCode, Payment, Media, Images, Video, RoleRequest
)

# ── Admin site branding ─────────────────────────────────────────────────────
admin.site.site_header = "Redeemed Gospel Church Nyahururu - Admin"
admin.site.site_title = "RGC CMS Admin"
admin.site.index_title = "Church Management System"


# ── Custom User ─────────────────────────────────────────────────────────────
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'get_full_name', 'phone', 'role', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'is_verified', 'is_phone_verified', 'is_email_verified')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    list_editable = ('role', 'is_staff', 'is_active')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (_('Role & Access'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Verification'), {'fields': ('is_verified', 'is_phone_verified', 'is_email_verified')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions')

    def get_full_name(self, obj):
        return obj.get_full_name() or '-'
    get_full_name.short_description = 'Full Name'


# ── User Profile ─────────────────────────────────────────────────────────────
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location')
    search_fields = ('user__username',)


# ── Groups / Ministries ──────────────────────────────────────────────────────
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'leader', 'get_member_count', 'created_at')
    list_filter = ('category',)
    search_fields = ('name',)

    def get_member_count(self, obj):
        return obj.members.count()
    get_member_count.short_description = 'Members'


# ── Members ──────────────────────────────────────────────────────────────────
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phonenumber', 'group', 'date_joined')
    list_filter = ('group',)
    search_fields = ('name', 'email', 'phonenumber')


# ── Events ───────────────────────────────────────────────────────────────────
@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'location', 'organizer')
    list_filter = ('date',)
    search_fields = ('title', 'location')
    date_hierarchy = 'date'


@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'phonenumber', 'registered_at')
    list_filter = ('event',)


# ── Announcements ─────────────────────────────────────────────────────────────
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_by', 'date_posted', 'is_published', 'is_urgent')
    list_filter = ('is_published', 'is_urgent')
    search_fields = ('title', 'content')
    list_editable = ('is_published', 'is_urgent')


# ── Hymns ─────────────────────────────────────────────────────────────────────
@admin.register(Hymn)
class HymnAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'author', 'category', 'language')
    search_fields = ('title', 'author')
    list_filter = ('category', 'language')


# ── OTP Codes ─────────────────────────────────────────────────────────────────
@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'email', 'purpose', 'is_used', 'created_at')
    list_filter = ('purpose', 'is_used')
    readonly_fields = ('created_at',)


# ── Payments ──────────────────────────────────────────────────────────────────
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'amount_display', 'purpose', 'status', 'mpesa_receipt_number', 'created_at')
    list_filter = ('status', 'purpose')
    search_fields = ('phone_number', 'mpesa_receipt_number')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

    def amount_display(self, obj):
        return format_html('KES <strong>{}</strong>', obj.amount)
    amount_display.short_description = 'Amount'


# ── Media ─────────────────────────────────────────────────────────────────────
@admin.register(Images)
class ImagesAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at')

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploader', 'uploaded_at', 'youtube_url')

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at')


# ── Role Requests ──────────────────────────────────────────────────────────────
@admin.register(RoleRequest)
class RoleRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'requested_role', 'status', 'reviewed_by', 'created_at')
    list_filter = ('status', 'requested_role')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'reviewed_at')
    list_editable = ('status',)
