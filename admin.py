from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Events, Payment, Media, Member, RegisteredEvent

# Register your models here.
admin.site.register(Events)
admin.site.register(Member)

admin.site.register(Payment)
admin.site.register(Media)
# admin.site.register(CustomUser)
admin.site.register(RegisteredEvent)