import datetime
from django.shortcuts import render
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, login as auth_login
from django.urls import include
from .models import Events, Attendee, UserProfile, Group, CustomUser, Payment, Member, Images, Video, Media, RegisteredEvent
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
import requests
import os
from datetime import datetime
from typing import Any, List

from django.shortcuts import redirect
# from intasend import IntaSend
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required  # For authentication check
from django.contrib import admin
from django.utils import timezone
from django.contrib.auth import get_user_model
# from intasend import IntaSend
from django.shortcuts import render
from .forms import PaymentForm, EventForm, CustomUserForm, GroupChangeForm, MediaForm, CustomUser, ProfileForm, GroupForm, ImagesForm, VideoForm
from intasend import APIService
# from intasend_python import IntaSend

# publishable_key = "ISPubKey_live_aef19549-0327-451a-830a-74031f96cf7d"
# service = APIService(token=ISSecretKey_live_0d4a4729-20c0-4bd5-90c7-f4d81745fa7a, publishable_key=publishable_key, test=True)

# Create your views here.
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        phone = request.POST.get('phone', '')
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        group_id = request.POST.get('group', '')

        try:
            if group_id:

                group = Group.objects.get(id=group_id)
            else:
                group = None
        except Group.DoesNotExist:
            group = None

        try:
            CustomUser.objects.get(username=username)
            messages.error(request, "Username already exists.")
        except CustomUser.DoesNotExist:
            try:
                CustomUser.objects.get(email=email)
                messages.error(request, "Email already exists.")
            except CustomUser.DoesNotExist:
                if len(username) < 5 or len(password) < 8:
                    messages.error(request, "Username must be at least 5 characters and Password must be at least 8 characters")
                    messages.error(request, "Username and Password must be at least 5 characters long.")
                    return redirect('register')

                elif password != confirm_password:
                    messages.error(request, "Passwords do not match.")
                    return redirect('register')

                else:
                    if phone:
                        phone_number = int(phone)
                    else:
                        phone_number = None
                    user = CustomUser.objects.create_user(username=username, password=password, email=email, phone=phone_number)
                    user.save()
                    member = Member(user=user, name=username, email=email)
                    member.save()
                    if group:
                        member.groups.add(group)
                    return redirect('login')
        return render(request, 'register.html')

    else:
        groups = Group.objects.all()
        return render(request, 'register.html', {'groups': groups})  

def login(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        if user_type == 'admin':
            return render(request, 'adminlogin.html')
        else:
            return render(request, 'userlogin.html')
    else:
        return render(request, 'login.html')

def adminlogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request,user)
            if user.is_superuser:
                return redirect('adminn')
            else:
                return redirect('/')
            
        else:
            messages.error(request,"Invalid username or password")
    return render(request,'login.html')

def userlogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else:
            messages.error(request,"Invalid username or password")
    return render(request,'login.html')

@login_required
def logout(request):
    auth.logout(request);
    return redirect('/');

@login_required
def profile(request):
    profile = get_object_or_404(profile, user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profile.html', {'form': form})

User = get_user_model()



def group_detail(request, pk):
    group = Group.objects.get(pk=pk)
    members = group.my_members.all()
    return render(request, 'group_detail.html', {'group': group, 'embers': members})

def create_group(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']

        group = Group.objects.create(name=name, description=description)
        group.save()

        return redirect('group_detail', group_id=group.id)
    else:
        return render(request, 'create_group.html')

def join_group(request):
    if request.method == 'POST':
        group_id = request.POST['group']
        user = request.user

        try:
            group = Group.objects.get(id=group_id)  # Use the custom 'CustomGroup' model
        except Group.DoesNotExist:
            group = None

        if group:
            member, _ = Member.objects.get_or_create(user=user)
            if not member.group:
                member.group = group
                member.save()
                return redirect('/')
            else:
                messages.error(request, "User is already in a group.")
                return redirect('/')
        else:
            messages.error(request, "Group not found.")
            return redirect('/')
    else:
        groups = Group.objects.all()  # Use the custom 'CustomGroup' model
        return render(request, 'join_group.html', {'groups': groups})
    
User = get_user_model()

def get_event_attendees(event_id):
    event = Events.objects.get(id=event_id)
    attendees = Attendee.objects.filter(event=event)
    users = [attendee.user for attendee in attendees]
    return users

@login_required
def user_events(request):
    user = request.user
    member = Member.objects.get(user=user)
    events = member.events.all()
    return render(request, 'user_events.html', {'events': events})

User = get_user_model()

@login_required
def group_change(request):
    user = request.user
    groups = user.groups.all()
    if request.method == 'POST':
        form = GroupChangeForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            user.groups.remove(*user.groups.all())
            user.groups.add(group)
            return redirect('group_change')
    else:
        form = GroupChangeForm(initial={'group': user.groups.first()})
    return render(request, 'group_change.html', {'groups': groups, 'form': form})

def group_management(request):
    groups = Group.objects.all()
    members = Member.objects.all()
    context = {'groups': groups, 'members': members}
    return render(request, 'groups.html', context)

def group_list(request):
    groups = Group.objects.all()
    return render(request, 'groups.html', {'groups': groups})

def group_add(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('groups')
    else:
        form = GroupForm()
    return render(request, 'group_form.html', {'form': form})

def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('groups')
    else:
        form = GroupForm(instance=group)
    return render(request, 'group_form.html', {'form': form})

def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        return redirect('groups')
    return render(request, 'group_confirm_delete.html', {'group': group})

@login_required
def uploadfiles(request):
    if request.method == 'POST':
        title = request.POST.get['title']
        description = request.POST.get['description']
        details = request.POST.get['details']
        file = request.FILES.get['file']

        if title and description and details and file:
            media_obj = Media.objects.create(title=title, description=description, details=details, file=file, uploader=request.user)
            media_obj.save()
            return redirect('index')
        else:
            messages.error(request, "Please make sure to enter a title, description, details and select a file to upload.")
    return render(request, 'uploadfiles.html')

def uploadvideos(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        details = request.POST.get('details', '')
        video = request.FILES.get('video')

        if title and video:
            video_obj = Video.objects.create(title=title, description=description, details=details, video=video, uploader=request.user)
            video_obj.save()
            return redirect('index')
        else:
            messages.error(request, "Please make sure to enter a title and select a video to upload.")
    return render(request, 'uploadvideos.html')


def addevents(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        location = request.POST.get('location', '')
        date_time_str = request.POST.get('date')

        if title and location and date_time_str:
            date_time_obj = datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M")
            date = date_time_obj.date()
            time = date_time_obj.time()

            event_obj = Events.objects.create(title=title, description=description, date=date, time=time, location=location, organizer=request.user)
            event_obj.save()
            return redirect('index')
        else:
            messages.error(request, "Please make sure to enter a title, location, and date before submitting.")
    return render(request, 'addevents.html')


@login_required
def register_event(request):
    event = get_object_or_404(Events)
    Attendee.objects.get_or_create(user=request.user, event=event)
    return redirect('events')

def events(request):
    event = get_object_or_404(Events)
    attendees = Attendee.objects.filter(event=event)
    users = [attendee.user for attendee in attendees]
    return render(request, 'events.html', {'event': event, 'attendees': attendees, 'users': users})

def event(request):
    events = Events.objects.all()
    return render(request, 'events.html', {'events': events})

def uploadimages(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')

        if title and image:
            image_obj = Images.objects.create(title=title, image=image, uploaded_by=request.user)
            image_obj.save()
            return redirect('index')
        else:
            messages.error(request, "Please make sure to enter a title and select an image to upload.")
    return render(request, 'uploadimages.html')

def index(request):
    media_list = Media.objects.all()
    images_list = Images.objects.all()
    video_list = Video.objects.all()
    event = Events.objects.all()
    return render(request, 'index.html', {'media_list': media_list, 'video_list':video_list, 'images_list': images_list, 'event':event})

CustomUser = get_user_model()
def user_report(request):
    users = CustomUser.objects.all()
    context =  {'users' : users} 
    return render(request,'userreports.html',context)
  
# def upload_media(request):
#     if request.method == 'POST':
#         media_form = MediaForm(request.POST, request.FILES)
#         images_form = ImagesForm(request.POST, request.FILES)
#         video_form = VideoForm(request.POST, request.FILES)

#         if media_form.is_valid() and images_form.is_valid() and video_form.is_valid():
#             media_form.save()
#             images_form.save()
#             video_form.save()
#             return render(request, 'index.html')
#     else:
#         media_form = MediaForm()
#         images_form = ImagesForm()
#         video_form = VideoForm()

#     return render(request, 'admins.html', {'media_form': media_form, 'images_form': images_form, 'video_form': video_form})

# Create your views here.
def change_password(request):
    """View for changing the password of the current logged in user."""
    user = request.user
    form = PasswordChangeForm(user=user)  # Create form based on user

    if request.method == 'GET':
        return render(request, "account/change_password.html", {"form": form})

    elif request.method == 'POST':
        form = PasswordChangeForm(user=user, data=request.POST)  # Bind submitted data
        if form.is_valid():
            form.save()  # Save the updated password
            logout(request)  # Log the user out for security
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('login')  # Redirect to login page after success
        else:
            return render(request, "change_password.html", {"form": form})



    return render(request, 'register.html' )

def base(request):
    # View for the home page of the website
    
    return render(request, 'base.html')


def video(request):
    # View for the home page of the website
    video = Video.objects.all()
    return render(request, 'video.html', {'video': video})

def images(request):
    image = Images.objects.all()
    return render(request, 'gallery.html', {'image': image})

def adminn(request):
    # View for the home page of the website
    event = Events.objects.all()
    return render(request, 'adminn.html')

def contribute(request):
    # View for the home page of the website
    return render(request, 'contribute.html')




def chats(request):
    return render(request, 'chats.html' )







# @login_required
# def register_for_events(request):
#     events = Events.objects.all()
#     registered_events = RegisteredEvent.objects.filter(user=request.user)
#     if request.method == 'POST':
#         event_ids = request.POST.getlist('events')
#         for event_id in event_ids:
#             event = Events.objects.get(id=event_id)
#             RegisteredEvent.objects.get_or_create(user=request.user, event=event)
#         return redirect('events')
#     return render(request, 'events.html', {'events': events, 'registered_events': registered_events})

# def initiate_payment(request):
#     if request.method == 'POST':
#         form = PaymentForm(request.POST)
#         if form.is_valid():
#             # Initialize IntaSend client
#             intasend = IntaSend(api_key=os.environ.get('ISSecretKey_live_509fc401-9e36-4d1f-800e-d0df429ba3fa'))

#             # Set payment details
#             payment_data = {
#                 "amount": int(form.cleaned_data['amount'] * 100),  # Amount in cents
#                 "currency": "KES",
#                 "description": form.cleaned_data['purpose'],
#                 "callback_url": "https://127.0.0.1:8000/",
#                 "customer": {
#                     "first_name": "John",
#                     "last_name": "Doe",
#                     "email": "john.doe@example.com",
#                     "phone": "254712345678",
#                     "address": "Nairobi, Kenya"
#                 },
#                 "metadata": {
#                     "order_id": "12345",
#                     "user_id": "67890"
#                 }
#             }

#             if form.cleaned_data['payment_method'] == 'mpesa':
#                 # Add M-Pesa specific details to payment_data
#                 payment_data['channel'] = 'mpesa'
#                 payment_data['command'] = 'paybill'
#                 payment_data['bill_number'] = 'your_bill_number'
#                 payment_data['account_number'] = 'your_account_number'

#             elif form.cleaned_data['payment_method'] == 'bank':
#                 # Add bank transfer specific details to payment_data
#                 payment_data['channel'] = 'bank'
#                 payment_data['command'] = 'transfer'
#                 payment_data['account_number'] = 'your_account_number'
#                 payment_data['bank_code'] = 'your_bank_code'

#             elif form.cleaned_data['payment_method'] == 'bitcoin':
#                 # Add Bitcoin specific details to payment_data
#                 payment_data['channel'] = 'bitcoin'
#                 payment_data['command'] = 'send'
#                 payment_data['address'] = 'your_bitcoin_address'

#             # Send payment request to IntaSend
#             response = intasend.payments.create(payment_data)

#             # Redirect user to IntaSend payment page
#             return redirect(response["payment_url"])
#     else:
#         form = PaymentForm()

#     return render(request, 'payment_form.html', {'form': form})
# def my_view(request):
#     """
#     Handles user requests and retrieves user information with Clerk integration.
#     """

#     if request.method == 'POST':
#         # Replace with your form processing logic here (if applicable)
#         # ...

#     # Check if user is authenticated
#      if not request.user.is_authenticated:
#         # Redirect to Clerk authentication page using Clerk's recommended API endpoint
#         clerk_session_url = requests.post(
#             'https://api.clerk.dev/v1/sessions/start',
#             json={
#                 'api_key': 'YOUR_CLERK_API_KEY',  # Replace with your frontend API key
#                 'redirect_uri': 'https://127.0.0.1:8000/callback',  # Replace with your callback URL
#             },
#         ).json()['url']
#         return redirect(clerk_session_url)

#     # Retrieve user information from Clerk (consider error handling)
#     try:
#         clerk_user_url = f'https://api.clerk.dev/v1/users/{request.user.clerk_id}'
#         clerk_user_response = requests.get(
#             clerk_user_url,
#             headers={
#                 'Authorization': f'Bearer {request.user.clerk_session.token}',
#             },
#         ).json()
#         user_name = clerk_user_response['email']
#         phonenumber = clerk_user_response['phonenumber']
#         user_email = clerk_user_response['email']
#         password = clerk_user_response['password']

#     except requests.exceptions.RequestException as e:
#         print(f"Error retrieving user information: {e}")
#         # Consider redirecting to an error page or displaying an error message to the user

#     # Render template with user data (optional)
#     context = {
#         'user_name': user_name,
#         'phonenumber': phonenumber,
#         'user_email': user_email,
#         'password': password,
#                }
#     # Add other context data as needed
#     return render(request, 'index.html', context)


# def my_view(request):
#     if request.method == 'POST':
#         # Handle form submission
#         pass

#     # Check if user is authenticated
#     if not request.user.is_authenticated:
#         # Redirect to Clerk authentication page
#         clerk_session_url = requests.post(
#             'https://api.clerk.dev/v2/sessions',
#             json={
#                 'api_key': 'YOUR_CLERK_API_KEY',
#                 'strategy': 'session',
#             },
#         ).json()['url']
#         return redirect(clerk_session_url)

#     # Retrieve user information from Clerk
#     clerk_user_url = f'https://api.clerk.dev/v2/users/{request.user.clerk_id}'
#     clerk_user_response = requests.get(
#         clerk_user_url,
#         headers={
#             'Authorization': f'Bearer {request.user.clerk_session.token}',
#         },
#     ).json()
#     user_email = clerk_user_response['email']
#     # ...

#     # Render template
#     return render(request, 'my_template.html', {
#         'user_email': user_email,
#         # ...
#     })

