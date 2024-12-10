from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Events, Group, Attendee, Images, CustomUser, Video, Payment, Media, Member, RegisteredEvent

# Register your models here.
admin.site.register(Events)
admin.site.register(Member)
admin.site.register(CustomUser)

admin.site.register(Images)
admin.site.register(Payment)
admin.site.register(Media)
admin.site.register(Video)
admin.site.register(Attendee)
admin.site.register(Group)
admin.site.register(RegisteredEvent)

# registered_events = admin.TabularInline(model=RegisteredEvent, readonly_fields=('event',), can_delete=False)
# fields = (
    
#     'registered_events',
# )
# class UserAdmin(admin.ModelAdmin):
#     inlines = [registered_events]
    
# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     list_display = ('username', 'email', 'first_name', 'last_name')
#     search_fields = ['username']

# @admin.register(Images)
# class ImageAdmin(admin.ModelAdmin):
#     def has_add_permission(self, request):
#         return False
        
#     fieldsets = (
#             ("Image Information", {"fields": ("image","caption")}),  # A tuple of tuples where each tuple contains a group of fields.
#     )
