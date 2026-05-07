from django import forms
from django.contrib.auth import get_user_model
from .models import CustomUser, Group, Events, Media, Images, Member, UserProfile, Video, Announcement

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone (e.g. 0712345678)'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone']

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 4:
            raise forms.ValidationError("Username must be at least 4 characters.")
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        pw2 = cleaned.get('confirm_password')
        if pw and pw2 and pw != pw2:
            raise forms.ValidationError("Passwords do not match.")
        if pw and len(pw) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        return cleaned


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class OTPVerifyForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}))
    code = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '6-digit OTP'}))


class PhoneOTPForm(forms.Form):
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone (e.g. 0712345678)'}))


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'is_urgent', 'image', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Announcement Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_urgent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }


class GroupChangeForm(forms.Form):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['title', 'description', 'details', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ImagesForm(forms.ModelForm):
    class Meta:
        model = Images
        fields = ['title', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Photo title'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'category', 'description', 'video', 'youtube_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'YouTube URL (paste link here, no file needed)'}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = ['title', 'category', 'description', 'date', 'time', 'location', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PaymentForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0712345678'}))
    amount = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount (KES)'}))
    purpose = forms.ChoiceField(
        choices=[('tithe', 'Tithe'), ('offering', 'Offering'), ('project', 'Project/Harambee'), ('other', 'Other')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_picture', 'bio', 'website', 'location')
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }
