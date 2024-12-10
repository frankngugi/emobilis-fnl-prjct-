import datetime
from django.db import models

# Create your models here.
from django.contrib.auth.models import User, AbstractUser, Group, Permission  # Assuming user model
from django.conf import settings
from django.utils.functional import cached_property
# from .custom_group import CustomGroup 
# from .custom_group_members import CustomGroup_members

# clerk.set_frontend_api_key('https://loved-orca-3.clerk.accounts.dev')
class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=False)
    is_verified = models.BooleanField(default=False)
    # groups = models.ManyToManyField(Group, related_name='custom_users', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_users', blank=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures')
    bio = models.TextField(max_length=500, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    groups = models.ManyToManyField(Group, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    
class Events(models.Model):
    title = models.CharField(max_length=200, default='')
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField(null=False, default=datetime.time(hour=0, minute=0))
    location = models.CharField(max_length=200, null=False, default='')
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.title

class Attendee(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    phonenumber = models.CharField(default="", max_length=13, blank=False)

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
    
class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    my_members = models.ManyToManyField('Member', related_name='groups')  # rename the field

    def __str__(self):
        members = ', '.join([member.user.username for member in self.my_members.all()])
        return f'{members} - {self.name}'

class Member(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    phonenumber = models.CharField(default="", max_length=13, blank=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE,default='', related_name='members')
    date_joined = models.DateTimeField(auto_now_add=True, null=True)
    events = models.ManyToManyField('Events', blank=True)
    membership_started = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    address = models.TextField()

    def __str__(self):
        return f'{self.user.username} - {self.group.name if self.group else "No Group"}'
    def get_registered_events(self):
        return self.events.all()
    
 
class RegisteredEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)

    @cached_property
    def default_event(self):
        return Events.objects.get_or_create(name='Default Event', description='Default event description')[0]

    def save(self, *args, **kwargs):
        if not self.event_id:
            self.event = self.default_event
        super().save(*args, **kwargs)




class Payment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('compeleted', 'Completed'),
        ('failed', 'Failed'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # id = models.IntegerField(null=False)
    event = models.ForeignKey(Events, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)
    mpesa_sender_phone = models.IntegerField(default=0)
    purpose = models.CharField(max_length=100, blank=True, null=True)
    mpesa_transaction_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Payment ID: {self.pk}, Amount: {self.amount}"


class Media(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField(max_length=500)
    details = models.TextField()
    file = models.FileField(upload_to='media/%y')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} ({self.description[:50]}) - Details: {self.details[:100]}"

class Images(models.Model):
    title = models.CharField(max_length=30)
    image = models.ImageField(upload_to='image/%y', default='Default image')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    

    def __str__(self):
        return f"{self.title}"


class Video(models.Model):
    title = models.CharField(max_length=30, default='Default title')
    description = models.TextField(max_length=500, default='Default description')
    
    details = models.TextField(default='Default details')
    video=models.FileField(upload_to="videos/%y", default='Default video')
    uploader=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    

    def __str__(self):
        return f"{self.title} ({self.description[:50]}) - Details: {self.details[:100]}"


class EventMedia(models.Model):
    media_files = models.ManyToManyField('EventMedia', related_name='event_media')
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

