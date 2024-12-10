from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser, Group, Events, Media, Group, Images, Member, UserProfile, Video


class PaymentForm(forms.Form):
    payment_method = forms.ChoiceField(choices=[('mpesa', 'M-Pesa'), ('bank', 'Bank Transfer'), ('bitcoin', 'Bitcoin')])
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    purpose = forms.CharField(max_length=100)
     
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description']

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ["title", "description", "details", "file"]

class ImagesForm(forms.ModelForm):
    class Meta:
        model = Images
        fields = ["title", "image"]

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ["title", "description", "details", "video"]

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'is_verified')

class ProfileForm(UserCreationForm):
    class Meta:
        
        model = UserProfile
        fields = ('profile_picture', 'bio', 'website', 'location', 'groups')
    
    # group = forms.ModelChoiceField(queryset=Group.objects.all(), required=False)
    profile_picture = forms.ImageField(required=False)

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['profile_picture']:
            user.profile_picture = self.cleaned_data['profile_picture']
        if commit:
            user.save()
            self.save_m2m()
        return user

class EventForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = ['title', 'description', 'date', 'time', 'location']

class GroupChangeForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all())
# from django import forms
# from django.contrib.auth.models import User  # Use User if not using custom user model
# from .models import CustomUser, Member

# class RegistrationForm(forms.ModelForm):
#     class Meta:
#         model = CustomUser
#         fields = ('username', 'email', 'password', 'phone', 'is_verified')  # Add custom fields

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data['password'])  # Set password securely
#         if commit:
#             user.save()
#             member = Member.objects.create(user=user,
#                                             name=self.cleaned_data['name'],  # Assuming you have a 'name' field
#                                             phonenumber=self.cleaned_data['phone'],
#                                             is_phone_verified=self.cleaned_data['is_verified']  # Adjust as needed
#                                             )
#         return user
