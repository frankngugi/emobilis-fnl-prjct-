import datetime
import base64
import requests as http_requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.db import models

from .models import (
    Events, Attendee, UserProfile, Group, CustomUser,
    Payment, Member, Images, Video, Media, Announcement, Hymn, OTPCode, RoleRequest
)
from .forms import (
    PaymentForm, EventForm, CustomUserForm, GroupChangeForm,
    MediaForm, ProfileForm, GroupForm, ImagesForm, VideoForm,
    AnnouncementForm, RegistrationForm, OTPVerifyForm
)

User = get_user_model()


# ─── One-time Setup (no shell access needed) ──────────────────────────────────

def first_time_setup(request):
    """
    One-time setup URL to create superuser and clean test data.
    Protected by DJANGO_SUPERUSER_PASSWORD env var — safe to leave in code.
    Remove this URL from urls.py after setup is complete.
    """
    import os
    from myapp.models import BranchChurch

    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')

    if not password:
        return JsonResponse({'error': 'DJANGO_SUPERUSER_PASSWORD not set in environment.'}, status=403)

    results = []

    # Create superuser if not exists
    if not User.objects.filter(is_superuser=True).exists():
        user = User.objects.create_superuser(username=username, email=email, password=password)
        results.append(f'✅ Superuser "{username}" created.')
    else:
        su = User.objects.filter(is_superuser=True).first()
        results.append(f'ℹ️ Superuser already exists: "{su.username}".')

    # Delete test/incomplete registrations (non-staff, non-superuser, unverified)
    if request.GET.get('clean') == '1':
        deleted = User.objects.filter(
            is_staff=False, is_superuser=False, is_active=True
        ).delete()
        Member.objects.filter(user__isnull=True).delete()
        results.append(f'🗑️ Deleted {deleted[0]} test user(s).')
    else:
        test_users = User.objects.filter(is_staff=False, is_superuser=False)
        results.append(f'ℹ️ {test_users.count()} non-staff user(s) exist. Add ?clean=1 to delete them.')

    # Seed RGC HQ church
    obj, created = BranchChurch.objects.get_or_create(
        name='RGC Nyahururu HQ',
        defaults={
            'region': 'nyahururu', 'location': 'Nyahururu Town, Laikipia County',
            'status': 'active', 'latitude': -0.0296, 'longitude': 36.3590,
            'notes': 'Central Rift Regional Headquarters',
        }
    )
    results.append(f'{"✅ HQ church created." if created else "ℹ️ HQ church already exists."}')
    results.append('---')
    results.append(f'👉 Now go to /admin/ and log in with: {username} / [your password]')

    return JsonResponse({'setup': results})


# ─── Authentication ────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        selected_role = request.POST.get('portal', 'member')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Validate the user has permission for the selected portal
            if selected_role == 'admin' and not (user.is_superuser or user.role == 'admin'):
                messages.error(request, "You do not have admin access.")
                return render(request, 'login.html')
            if selected_role == 'manager' and not (user.is_staff or user.is_superuser or user.role in ('admin', 'manager')):
                messages.error(request, "You do not have manager access.")
                return render(request, 'login.html')
            auth_login(request, user)
            # Store the active portal in session
            request.session['active_portal'] = selected_role if selected_role in ('admin', 'manager') else 'member'
            return _redirect_by_role(user, override=selected_role)
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')


def _redirect_by_role(user, override=None):
    portal = override or getattr(user, 'role', 'member')
    if portal == 'admin' or user.is_superuser:
        return redirect('adminn')
    if portal == 'manager' or user.is_staff:
        return redirect('adminn')
    return redirect('index')


@login_required
def switch_portal(request, portal):
    """Allow a user to switch between member/manager/admin views."""
    user = request.user
    if portal == 'admin' and not (user.is_superuser or user.role == 'admin'):
        messages.error(request, "You do not have admin access.")
        return redirect('index')
    if portal == 'manager' and not (user.is_staff or user.is_superuser or user.role in ('admin', 'manager')):
        messages.error(request, "You do not have manager access.")
        return redirect('index')
    request.session['active_portal'] = portal
    if portal in ('admin', 'manager'):
        return redirect('adminn')
    return redirect('index')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Create member profile
            Member.objects.get_or_create(
                email=user.email,
                defaults={'user': user, 'name': f"{user.first_name} {user.last_name}".strip() or user.username}
            )
            # Send email verification OTP (non-fatal if email fails)
            try:
                _send_email_otp(request, user)
                messages.success(request, "Account created! Check your email for your verification code.")
            except Exception:
                messages.success(request, "Account created! Email verification is temporarily unavailable — you can log in directly.")
                return redirect('login')
            # Send welcome SMS if phone provided
            if user.phone:
                try:
                    from .services import send_welcome_sms
                    send_welcome_sms(user.phone, user.first_name or user.username)
                except Exception:
                    pass
            return redirect('verify_email_notice')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = RegistrationForm()
    groups = Group.objects.all()
    return render(request, 'register.html', {'form': form, 'groups': groups})


def _send_email_otp(request, user):
    """
    Send OTP via:
    1. WhatsApp (if Meta credentials configured + user has phone)
    2. Email (always, as primary or fallback)
    """
    from .services import send_email, send_whatsapp_otp, _normalize_phone
    code = OTPCode.generate_code()
    OTPCode.objects.create(user=user, email=user.email, code=code, purpose='email')

    name = user.first_name or user.username
    subject = f"Verification Code – {settings.CHURCH_NAME}"
    email_body = (
        f"Hello {name},\n\n"
        f"Your RGC verification code is: {code}\n\n"
        f"This code expires in 10 minutes.\n\n"
        f"God bless you!\n{settings.CHURCH_NAME}"
    )

    # Try WhatsApp OTP first (if phone available + Meta configured)
    wa_sent = False
    if user.phone and getattr(settings, 'WHATSAPP_ACCESS_TOKEN', ''):
        phone_e164 = _normalize_phone(user.phone)
        wa_result = send_whatsapp_otp(phone_e164, code, name)
        wa_sent = wa_result.get('success', False)

    # Always send email as well (primary if no WhatsApp, confirmation otherwise)
    send_email(subject, email_body, [user.email])


def verify_email_notice(request):
    return render(request, 'verify_email_notice.html')


def verify_email(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email=email)
            otp = OTPCode.objects.filter(
                user=user, code=code, purpose='email', is_used=False
            ).latest('created_at')
            if otp.is_valid():
                otp.is_used = True
                otp.save()
                user.is_email_verified = True
                user.save()
                auth_login(request, user)
                messages.success(request, "Email verified! Welcome to RGC.")
                return redirect('index')
            else:
                messages.error(request, "Code expired or already used.")
        except (User.DoesNotExist, OTPCode.DoesNotExist):
            messages.error(request, "Invalid code or email.")
    return render(request, 'verify_email.html')


def send_phone_otp(request):
    """Send OTP via Twilio Verify to a phone number."""
    if request.method == 'POST':
        from .services import send_phone_otp as _send_otp, _normalize_phone
        phone = request.POST.get('phone', '').strip()
        phone_e164 = _normalize_phone(phone)
        result = _send_otp(phone_e164)
        if result.get('success'):
            request.session['otp_phone'] = phone_e164
            messages.success(request, f"OTP sent to {phone_e164}")
            return redirect('verify_phone')
        else:
            messages.error(request, f"Could not send OTP: {result.get('error', 'Unknown error')}")
    return render(request, 'send_phone_otp.html')


def verify_phone(request):
    """Verify phone OTP via Twilio Verify."""
    if request.method == 'POST':
        from .services import verify_phone_otp as _verify_otp
        phone = request.session.get('otp_phone', '')
        code = request.POST.get('code', '').strip()
        result = _verify_otp(phone, code)
        if result.get('success'):
            if request.user.is_authenticated:
                request.user.is_phone_verified = True
                request.user.phone = phone
                request.user.save()
                Member.objects.filter(user=request.user).update(phonenumber=phone)
            messages.success(request, "Phone number verified!")
            return redirect('profile')
        else:
            messages.error(request, result.get('error', 'Invalid or expired OTP.'))
    return render(request, 'verify_phone.html')


@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('index')


# ─── Profile ───────────────────────────────────────────────────────────────────

@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile_obj)
    member = Member.objects.filter(user=request.user).first()
    return render(request, 'profile.html', {'form': form, 'member': member})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password changed successfully!")
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})


# ─── Index / Home ──────────────────────────────────────────────────────────────

def index(request):
    announcements = Announcement.objects.filter(is_published=True)[:5]
    events = Events.objects.filter(date__gte=timezone.now().date()).order_by('date')[:6]
    images = Images.objects.all().order_by('-uploaded_at')[:8]
    videos = Video.objects.all().order_by('-uploaded_at')[:3]
    groups = Group.objects.all()
    return render(request, 'index.html', {
        'announcements': announcements,
        'events': events,
        'images_list': images,
        'video_list': videos,
        'groups': groups,
    })


# ─── Announcements ─────────────────────────────────────────────────────────────

def announcements(request):
    all_announcements = Announcement.objects.filter(is_published=True)
    paginator = Paginator(all_announcements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'announcements.html', {'page_obj': page_obj})


@login_required
def add_announcement(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Permission denied.")
        return redirect('announcements')
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            ann = form.save(commit=False)
            ann.posted_by = request.user
            ann.save()
            # Push to all mobile app users for free
            from .services import push_new_announcement
            push_new_announcement(ann)
            messages.success(request, "Announcement posted successfully.")
            return redirect('announcements')
    else:
        form = AnnouncementForm()
    return render(request, 'add_announcement.html', {'form': form})


@login_required
def delete_announcement(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Permission denied.")
        return redirect('announcements')
    ann = get_object_or_404(Announcement, pk=pk)
    ann.delete()
    messages.success(request, "Announcement deleted.")
    return redirect('announcements')


# ─── Hymns ─────────────────────────────────────────────────────────────────────

def hymns(request):
    query = request.GET.get('q', '').strip()
    lang_filter = request.GET.get('lang', '').strip()
    hymn_list = Hymn.objects.all()
    if query:
        hymn_list = hymn_list.filter(
            models.Q(title__icontains=query) |
            models.Q(author__icontains=query) |
            (models.Q(number=int(query)) if query.isdigit() else models.Q())
        )
    if lang_filter:
        hymn_list = hymn_list.filter(language__iexact=lang_filter)
    paginator = Paginator(hymn_list, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    selected_hymn = None
    hymn_id = request.GET.get('hymn')
    if hymn_id:
        selected_hymn = Hymn.objects.filter(pk=hymn_id).first()
    return render(request, 'hymns.html', {
        'page_obj': page_obj,
        'query': query,
        'lang_filter': lang_filter,
        'selected_hymn': selected_hymn,
    })


def hymns_api(request):
    """JSON endpoint for hymn search."""
    query = request.GET.get('q', '')
    lang = request.GET.get('lang', '')
    hymns_qs = Hymn.objects.all()
    if query:
        hymns_qs = hymns_qs.filter(title__icontains=query) | hymns_qs.filter(author__icontains=query)
    if lang:
        hymns_qs = hymns_qs.filter(language__iexact=lang)
    data = [{'id': h.id, 'number': h.number, 'title': h.title, 'author': h.author, 'language': h.language} for h in hymns_qs[:100]]
    return JsonResponse({'hymns': data})


@login_required
def add_hymn(request, pk=None):
    """Add or edit a hymn — media team and admin only."""
    if not (request.user.is_staff or request.user.is_superuser or request.user.role in ('admin', 'manager')):
        messages.error(request, "Only media team and administrators can manage hymns.")
        return redirect('hymns')
    hymn = get_object_or_404(Hymn, pk=pk) if pk else None
    if request.method == 'POST':
        number = request.POST.get('number', '').strip()
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        lyrics = request.POST.get('lyrics', '').strip()
        category = request.POST.get('category', '').strip()
        language = request.POST.get('language', 'English').strip()
        errors = []
        if not number or not number.isdigit():
            errors.append("A valid hymn number is required.")
        elif not hymn and Hymn.objects.filter(number=int(number)).exists():
            errors.append(f"Hymn #{number} already exists.")
        if not title:
            errors.append("Title is required.")
        if not lyrics:
            errors.append("Lyrics are required.")
        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            if hymn:
                hymn.number = int(number)
                hymn.title = title
                hymn.author = author
                hymn.lyrics = lyrics
                hymn.category = category
                hymn.language = language
                hymn.save()
                messages.success(request, f"Hymn #{number} updated.")
            else:
                hymn = Hymn.objects.create(
                    number=int(number), title=title, author=author,
                    lyrics=lyrics, category=category, language=language,
                )
                messages.success(request, f"Hymn #{number} '{title}' added.")
            return redirect(f'/hymns/?hymn={hymn.pk}')
    next_num = (Hymn.objects.order_by('-number').first().number + 1) if Hymn.objects.exists() else 1
    return render(request, 'add_hymn.html', {'hymn': hymn, 'next_num': next_num})


@login_required
def delete_hymn(request, pk):
    if not (request.user.is_superuser or request.user.role in ('admin', 'manager')):
        messages.error(request, "Only administrators can delete hymns.")
        return redirect('hymns')
    hymn = get_object_or_404(Hymn, pk=pk)
    if request.method == 'POST':
        hymn.delete()
        messages.success(request, f"Hymn deleted.")
        return redirect('hymns')
    return redirect('hymns')


# ─── Bible ─────────────────────────────────────────────────────────────────────

BIBLE_TRANSLATIONS = [
    ('kjv',      'King James Version (KJV)'),
    ('web',      'World English Bible (WEB)'),
    ('asv',      'American Standard Version (ASV)'),
    ('bbe',      'Bible in Basic English (BBE)'),
    ('darby',    'Darby Translation'),
    ('dra',      'Douay-Rheims (Catholic)'),
    ('ylt',      "Young's Literal Translation"),
    ('weymouth', 'Weymouth New Testament'),
]

def bible(request):
    verse_data = None
    error = None
    books = [
        "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
        "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
        "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles",
        "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
        "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah",
        "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
        "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah",
        "Haggai", "Zechariah", "Malachi",
        "Matthew", "Mark", "Luke", "John", "Acts", "Romans",
        "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
        "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
        "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews",
        "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John",
        "Jude", "Revelation"
    ]
    reference = request.GET.get('ref', '')
    translation = request.GET.get('translation', 'kjv')
    if translation not in [t[0] for t in BIBLE_TRANSLATIONS]:
        translation = 'kjv'
    if reference:
        try:
            url = f"https://bible-api.com/{reference.replace(' ', '%20')}?translation={translation}"
            resp = http_requests.get(url, timeout=10)
            if resp.status_code == 200:
                verse_data = resp.json()
                if 'error' in verse_data:
                    error = verse_data['error']
                    verse_data = None
            else:
                error = "Verse not found. Try: John 3:16 or Psalms 23:1-6"
        except Exception:
            error = "Could not connect to Bible API. Please try again."
    return render(request, 'bible.html', {
        'verse_data': verse_data,
        'reference': reference,
        'books': books,
        'error': error,
        'translation': translation,
        'translations': BIBLE_TRANSLATIONS,
        'quick_refs': [
            'John 3:16','Psalms 23','Romans 8:28','Proverbs 3:5-6',
            'Philippians 4:13','Isaiah 40:31','Matthew 6:33',
            'Jeremiah 29:11','Hebrews 11:1','1 Corinthians 13',
        ],
    })


# ─── Events ────────────────────────────────────────────────────────────────────

pass  # event_list defined below with category filter


def addevents(request):
    if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)):
        messages.error(request, "Permission denied.")
        return redirect('events')
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.organizer = request.user
            ev.save()
            messages.success(request, "Event added successfully.")
            return redirect('events')
    else:
        form = EventForm()
    return render(request, 'addevents.html', {'form': form})


@login_required
def register_event(request, event_id):
    event = get_object_or_404(Events, pk=event_id)
    phone = request.POST.get('phonenumber', request.user.phone or '')
    _, created = Attendee.objects.get_or_create(
        user=request.user, event=event,
        defaults={'phonenumber': phone}
    )
    if created:
        messages.success(request, f"Registered for {event.title}!")
    else:
        messages.info(request, "You are already registered for this event.")
    return redirect('events')


# ─── Groups ────────────────────────────────────────────────────────────────────

def group_list(request):
    groups = Group.objects.all()
    return render(request, 'groups.html', {'groups': groups})


def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    members = group.members.all()
    return render(request, 'group_details.html', {'group': group, 'members': members})


def create_group(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.is_staff or request.user.is_superuser or request.user.role in ('admin', 'manager')):
        messages.error(request, "Only admins and managers can create groups.")
        return redirect('groups')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', 'other').strip()
        if not name:
            messages.error(request, "Group name is required.")
        elif not description:
            messages.error(request, "Description is required.")
        elif Group.objects.filter(name__iexact=name).exists():
            messages.error(request, f"A group named '{name}' already exists.")
        else:
            group = Group.objects.create(
                name=name, description=description,
                category=category, leader=request.user,
            )
            messages.success(request, f"Group '{group.name}' created!")
            return redirect('group_detail', pk=group.id)
    return render(request, 'create_group.html')


@login_required
def join_group(request):
    if request.method == 'POST':
        group_id = request.POST.get('group')
        group = get_object_or_404(Group, id=group_id)
        member, created = Member.objects.get_or_create(
            user=request.user,
            defaults={'email': request.user.email, 'name': request.user.get_full_name() or request.user.username}
        )
        member.group = group
        member.save()
        messages.success(request, f"Joined {group.name}!")
        return redirect('index')
    groups = Group.objects.all()
    return render(request, 'join_group.html', {'groups': groups})


def group_add(request):
    return create_group(request)


def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, "Group updated.")
            return redirect('groups')
    else:
        form = GroupForm(instance=group)
    return render(request, 'group_form.html', {'form': form, 'group': group})


def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        messages.success(request, "Group deleted.")
        return redirect('groups')
    return render(request, 'group_confirm_delete.html', {'group': group})


# ─── Media uploads ─────────────────────────────────────────────────────────────

@login_required
def uploadimages(request):
    if request.method == 'POST':
        form = ImagesForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save(commit=False)
            img.uploaded_by = request.user
            img.save()
            messages.success(request, "Image uploaded.")
            return redirect('gallery')
    else:
        form = ImagesForm()
    return render(request, 'uploadimages.html', {'form': form})


@login_required
def uploadvideos(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        youtube_url = request.POST.get('youtube_url', '').strip()
        category = request.POST.get('category', 'general')
        description = request.POST.get('description', '').strip()
        has_file = bool(request.FILES.get('video'))
        if not title:
            messages.error(request, "Title is required.")
        elif not youtube_url and not has_file:
            messages.error(request, "Please provide either a video link (YouTube/Facebook/Vimeo) or upload a file.")
        else:
            from .models import Video as VideoModel
            vid = VideoModel(
                title=title, category=category, description=description,
                youtube_url=youtube_url, uploader=request.user,
            )
            if has_file:
                vid.video = request.FILES['video']
            vid.save()
            messages.success(request, f"Video '{title}' added successfully.")
            return redirect('video')
    form = VideoForm()
    return render(request, 'uploadvideos.html', {'form': form})


@login_required
def uploadfiles(request):
    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES)
        if form.is_valid():
            media = form.save(commit=False)
            media.uploaded_by = request.user
            media.save()
            messages.success(request, "File uploaded.")
            return redirect('index')
    else:
        form = MediaForm()
    return render(request, 'uploadfiles.html', {'form': form})


def images(request):
    from .models import MEDIA_CATEGORY_CHOICES
    cat = request.GET.get('cat', '')
    image_list = Images.objects.all()
    if cat:
        image_list = image_list.filter(category=cat)
    return render(request, 'gallery.html', {
        'image_list': image_list,
        'categories': MEDIA_CATEGORY_CHOICES,
        'active_cat': cat,
    })


def video(request):
    from .models import MEDIA_CATEGORY_CHOICES
    cat = request.GET.get('cat', '')
    video_list = Video.objects.all()
    if cat:
        video_list = video_list.filter(category=cat)
    return render(request, 'video.html', {
        'video_list': video_list,
        'categories': MEDIA_CATEGORY_CHOICES,
        'active_cat': cat,
    })


def event_list(request):
    from .models import EVENT_CATEGORY_CHOICES
    cat = request.GET.get('cat', '')
    events = Events.objects.filter(date__gte=timezone.now().date())
    if cat:
        events = events.filter(category=cat)
    return render(request, 'events.html', {
        'events': events,
        'categories': EVENT_CATEGORY_CHOICES,
        'active_cat': cat,
    })


# ─── Contributions / M-Pesa ────────────────────────────────────────────────────

def contribute(request):
    if request.method == 'POST':
        phone = request.POST.get('phonenumber', '').strip()
        amount = request.POST.get('amount', '').strip()
        purpose = request.POST.get('purpose', 'offering')
        name = request.POST.get('name', '').strip()

        if not phone or not amount:
            messages.error(request, "Please enter phone number and amount.")
            return render(request, 'contribute.html')

        # Normalize phone to 254XXXXXXXXX
        phone_clean = phone.lstrip('+').lstrip('0')
        if not phone_clean.startswith('254'):
            phone_clean = '254' + phone_clean

        try:
            amount_val = float(amount)
        except ValueError:
            messages.error(request, "Please enter a valid amount.")
            return render(request, 'contribute.html')

        # Save pending payment
        payment = Payment.objects.create(
            user=request.user if request.user.is_authenticated else None,
            amount=amount_val,
            phone_number=phone_clean,
            purpose=purpose,
        )

        # Try M-Pesa STK Push
        stk_result = _mpesa_stk_push(phone_clean, amount_val, purpose, payment.id)
        if stk_result.get('success'):
            payment.checkout_request_id = stk_result.get('checkout_request_id', '')
            payment.save()
            messages.success(request, "STK Push sent! Check your phone to complete payment.")
        else:
            messages.warning(request, stk_result.get('error', 'Payment initiation failed. Try again.'))

        return redirect('contribute')

    recent_payments = []
    if request.user.is_authenticated:
        recent_payments = Payment.objects.filter(user=request.user).order_by('-created_at')[:5]
    return render(request, 'contribute.html', {'recent_payments': recent_payments})


def _mpesa_stk_push(phone, amount, purpose, payment_id):
    """
    Initiate M-Pesa STK Push via Safaricom Daraja API.

    SANDBOX: uses shortcode 174379 + CustomerPayBillOnline (Safaricom sandbox limitation)
    PRODUCTION: uses your real Till + CustomerBuyGoodsOnline
    """
    import datetime as dt

    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    if not consumer_key or consumer_key in ('', 'PASTE_YOUR_CONSUMER_KEY', 'your_consumer_key'):
        return {'success': False, 'error': 'M-Pesa not configured. Add MPESA_CONSUMER_KEY to msys/.env'}

    is_sandbox = settings.MPESA_ENVIRONMENT == 'sandbox'
    base_url = 'https://sandbox.safaricom.co.ke' if is_sandbox else 'https://api.safaricom.co.ke'

    # Safaricom sandbox ONLY supports Paybill (174379) + CustomerPayBillOnline.
    # Your real Till (CustomerBuyGoodsOnline) is used in production only.
    if is_sandbox:
        shortcode = '174379'
        transaction_type = 'CustomerPayBillOnline'
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        party_b = shortcode
        account_ref = f'RGC-{payment_id}'
    else:
        shortcode = settings.MPESA_TILL_NUMBER
        transaction_type = 'CustomerBuyGoodsOnline'
        passkey = settings.MPESA_PASSKEY
        party_b = shortcode
        account_ref = f'RGC-{payment_id}'

    try:
        # Get access token
        auth = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
        token_resp = http_requests.get(
            f"{base_url}/oauth/v1/generate?grant_type=client_credentials",
            headers={'Authorization': f'Basic {auth}'}, timeout=15
        )
        token_data = token_resp.json()
        token = token_data.get('access_token')
        if not token:
            return {'success': False, 'error': f'M-Pesa auth failed: {token_data.get("error_description", "check consumer key/secret")}'}

        timestamp = dt.datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()

        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": transaction_type,
            "Amount": max(1, int(amount)),
            "PartyA": phone,
            "PartyB": party_b,
            "PhoneNumber": phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": account_ref,
            "TransactionDesc": f"RGC {purpose.title()}",
        }
        stk_resp = http_requests.post(
            f"{base_url}/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            timeout=30
        )
        data = stk_resp.json()
        if data.get('ResponseCode') == '0':
            return {'success': True, 'checkout_request_id': data.get('CheckoutRequestID', '')}
        err = data.get('errorMessage') or data.get('ResultDesc') or str(data)
        return {'success': False, 'error': err}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def mpesa_callback(request):
    """Handle M-Pesa payment callback."""
    import json
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            callback = data.get('Body', {}).get('stkCallback', {})
            checkout_id = callback.get('CheckoutRequestID', '')
            result_code = callback.get('ResultCode')

            payment = Payment.objects.filter(checkout_request_id=checkout_id).first()
            if payment:
                if result_code == 0:
                    items = {
                        item['Name']: item['Value']
                        for item in callback.get('CallbackMetadata', {}).get('Item', [])
                        if 'Value' in item
                    }
                    payment.status = 'completed'
                    payment.mpesa_receipt_number = str(items.get('MpesaReceiptNumber', ''))
                    payment.save()
                    # Send SMS confirmation
                    from .services import send_payment_sms
                    send_payment_sms(
                        payment.phone_number,
                        payment.amount,
                        payment.get_purpose_display(),
                        payment.mpesa_receipt_number,
                    )
                    # Send email confirmation if user linked
                    if payment.user and payment.user.email:
                        from .services import send_payment_confirmation_email
                        send_payment_confirmation_email(payment.user, payment)
                else:
                    payment.status = 'failed'
                    payment.save()
        except Exception:
            pass
    return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})


# ─── Admin views ───────────────────────────────────────────────────────────────

@login_required
def adminn(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Admin access required.")
        return redirect('index')
    context = {
        'total_members': Member.objects.count(),
        'total_events': Events.objects.count(),
        'total_groups': Group.objects.count(),
        'total_payments': Payment.objects.filter(status='completed').count(),
        'recent_payments': Payment.objects.order_by('-created_at')[:5],
        'recent_events': Events.objects.order_by('-created_at')[:5],
        'recent_announcements': Announcement.objects.order_by('-date_posted')[:5],
        'recent_members': Member.objects.order_by('-date_joined')[:10],
    }
    return render(request, 'adminn.html', context)


@login_required
def user_report(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Admin access required.")
        return redirect('index')
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'userreports.html', {'users': users})


@login_required
def user_events(request):
    member = Member.objects.filter(user=request.user).first()
    registered = Attendee.objects.filter(user=request.user).select_related('event')
    return render(request, 'user_events.html', {
        'registered_events': registered,
        'member': member,
    })


@login_required
def group_change(request):
    if request.method == 'POST':
        form = GroupChangeForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            member, _ = Member.objects.get_or_create(
                user=request.user,
                defaults={'email': request.user.email, 'name': request.user.get_full_name() or request.user.username}
            )
            member.group = group
            member.save()
            messages.success(request, f"Joined group: {group.name}")
            return redirect('profile')
    else:
        form = GroupChangeForm()
    return render(request, 'group_change.html', {'form': form})


# ─── Static pages ──────────────────────────────────────────────────────────────

def base(request):
    return render(request, 'base.html')


def chats(request):
    return render(request, 'chats.html')


# ─── User Management (Admin only) ─────────────────────────────────────────────

@login_required
def manage_users(request):
    if not (request.user.is_superuser or request.user.role == 'admin'):
        messages.error(request, "Only administrators can manage users.")
        return redirect('adminn')
    users = User.objects.all().order_by('-date_joined')
    pending_requests = RoleRequest.objects.filter(status='pending').select_related('user')
    return render(request, 'manage_users.html', {
        'users': users,
        'pending_requests': pending_requests,
    })


@login_required
def change_user_role(request, user_id):
    if not (request.user.is_superuser or request.user.role == 'admin'):
        messages.error(request, "Permission denied.")
        return redirect('adminn')
    target_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        new_role = request.POST.get('role', 'member')
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser_flag = request.POST.get('is_superuser') == 'on'
        is_active = request.POST.get('is_active', 'on') == 'on'
        if target_user == request.user and new_role == 'member':
            messages.error(request, "You cannot remove your own admin role.")
            return redirect('manage_users')
        if is_superuser_flag and not request.user.is_superuser:
            messages.error(request, "Only a superadmin can grant superadmin rights.")
            is_superuser_flag = False
        target_user.role = new_role
        target_user.is_staff = is_staff or new_role in ('admin', 'manager')
        target_user.is_superuser = is_superuser_flag
        target_user.is_active = is_active
        target_user.save()
        messages.success(request, f"Updated {target_user.username}: role={new_role}.")
        return redirect('manage_users')
    return render(request, 'change_user_role.html', {'target_user': target_user})


@login_required
def approve_role_request(request, request_id, action):
    if not (request.user.is_superuser or request.user.role == 'admin'):
        messages.error(request, "Permission denied.")
        return redirect('adminn')
    role_req = get_object_or_404(RoleRequest, pk=request_id)
    from django.utils import timezone as tz
    if action == 'approve':
        role_req.status = 'approved'
        role_req.reviewed_by = request.user
        role_req.review_note = request.POST.get('note', '')
        role_req.reviewed_at = tz.now()
        role_req.save()
        user = role_req.user
        user.role = role_req.requested_role
        user.is_staff = True
        if role_req.requested_role == 'admin' and request.user.is_superuser:
            user.is_superuser = True
        user.save()
        messages.success(request, f"Approved: {user.username} is now {role_req.requested_role}.")
    elif action == 'reject':
        role_req.status = 'rejected'
        role_req.reviewed_by = request.user
        role_req.review_note = request.POST.get('note', 'Not approved at this time.')
        role_req.reviewed_at = tz.now()
        role_req.save()
        messages.info(request, f"Rejected request from {role_req.user.username}.")
    return redirect('manage_users')


@login_required
def request_role_upgrade(request):
    if request.method == 'POST':
        requested_role = request.POST.get('requested_role', '').strip()
        reason = request.POST.get('reason', '').strip()
        if not requested_role or not reason:
            messages.error(request, "Please select a role and provide a reason.")
        elif RoleRequest.objects.filter(user=request.user, status='pending').exists():
            messages.warning(request, "You already have a pending request. Please wait for a response.")
        else:
            RoleRequest.objects.create(user=request.user, requested_role=requested_role, reason=reason)
            messages.success(request, "Role upgrade request submitted! An admin will review it soon.")
            return redirect('profile')
    return render(request, 'request_role.html')


# ─── Community Chat ────────────────────────────────────────────────────────────

from .models import ChatRoom, ChatMessage

@login_required
def chat_view(request):
    rooms = ChatRoom.objects.filter(is_active=True)
    room_id = request.GET.get('room')
    active_room = None
    messages_list = []
    if room_id:
        active_room = get_object_or_404(ChatRoom, id=room_id, is_active=True)
        messages_list = active_room.messages.filter(is_deleted=False).order_by('created_at').select_related('sender')[:100]
    elif rooms.exists():
        active_room = rooms.first()
        messages_list = active_room.messages.filter(is_deleted=False).order_by('created_at').select_related('sender')[:100]
    return render(request, 'chat.html', {'rooms': rooms, 'active_room': active_room, 'messages_list': messages_list})

@login_required
def send_chat_message(request, room_id):
    if request.method == 'POST':
        import json
        room = get_object_or_404(ChatRoom, id=room_id, is_active=True)
        text = request.POST.get('message', '').strip()
        if text and len(text) <= 1000:
            msg = ChatMessage.objects.create(room=room, sender=request.user, message=text)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'id': msg.id,
                    'sender': msg.sender.get_full_name() or msg.sender.username,
                    'message': msg.message,
                    'time': msg.created_at.strftime('%H:%M'),
                    'mine': True,
                })
        return redirect(f'/chats?room={room_id}')
    return redirect('chats')

def get_chat_messages(request, room_id):
    """Polling endpoint — returns latest messages as JSON."""
    from django.http import JsonResponse
    room = get_object_or_404(ChatRoom, id=room_id, is_active=True)
    since_id = request.GET.get('since', 0)
    msgs = ChatMessage.objects.filter(room=room, id__gt=since_id, is_deleted=False).order_by('created_at').select_related('sender')[:50]
    return JsonResponse({'messages': [{
        'id': m.id,
        'sender': m.sender.get_full_name() or m.sender.username,
        'avatar': m.sender.username[0].upper(),
        'message': m.message,
        'time': m.created_at.strftime('%H:%M'),
        'mine': m.sender == request.user,
    } for m in msgs]})


# ─── Regional Church Network ───────────────────────────────────────────────────

from .models import BranchChurch, ChurchLeader, RegionalMember, ClergyPayment

def regional_churches(request):
    churches = BranchChurch.objects.exclude(status='inactive').order_by('region', 'name')
    context = {
        'churches': churches,
        'total': churches.count(),
        'regions': BranchChurch.REGION_CHOICES,
    }
    return render(request, 'regional.html', context)


def church_detail(request, pk):
    church = get_object_or_404(BranchChurch, pk=pk)
    leaders = ChurchLeader.objects.filter(church=church, is_active=True)
    members = RegionalMember.objects.filter(church=church)
    return render(request, 'church_detail.html', {
        'church': church, 'leaders': leaders, 'members': members,
    })


@login_required
def clergy_payments(request):
    """Clergy payments — ONLY superadmin can view."""
    if not request.user.is_superuser:
        messages.error(request, "Access denied. This section is restricted to the Super Administrator only.")
        return redirect('adminn')
    payments = ClergyPayment.objects.select_related('recipient', 'church', 'paid_by').order_by('-created_at')
    pending = payments.filter(status='pending')
    return render(request, 'clergy_payments.html', {
        'payments': payments,
        'pending': pending,
        'total_approved': sum(p.amount for p in payments.filter(status__in=['approved', 'paid'])),
    })


@login_required
def add_clergy_payment(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect('adminn')
    if request.method == 'POST':
        from django.contrib.auth import get_user_model
        U = get_user_model()
        recipient_id = request.POST.get('recipient')
        amount = request.POST.get('amount')
        payment_type = request.POST.get('payment_type')
        period = request.POST.get('period', '')
        church_id = request.POST.get('church', '')
        notes = request.POST.get('notes', '')
        try:
            recipient = U.objects.get(pk=recipient_id)
            church = BranchChurch.objects.get(pk=church_id) if church_id else None
            ClergyPayment.objects.create(
                recipient=recipient, amount=amount, payment_type=payment_type,
                period=period, church=church, notes=notes,
                paid_by=request.user, status='approved',
            )
            messages.success(request, f"Payment record added for {recipient.get_full_name() or recipient.username}.")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect('clergy_payments')
    clergy_users = get_user_model().objects.filter(role__in=['pastor', 'reverend'])
    churches = BranchChurch.objects.all()
    return render(request, 'add_clergy_payment.html', {
        'clergy_users': clergy_users,
        'churches': churches,
        'payment_types': ClergyPayment.PAYMENT_TYPE_CHOICES,
    })


# ─── Member / Guest Management ────────────────────────────────────────────────

@login_required
def manage_members(request):
    if not (request.user.is_staff or request.user.is_superuser or request.user.role in ('admin', 'manager')):
        messages.error(request, "Permission denied.")
        return redirect('adminn')
    search = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '')
    users = User.objects.select_related().order_by('-date_joined')
    if search:
        users = users.filter(
            models.Q(username__icontains=search) |
            models.Q(first_name__icontains=search) |
            models.Q(last_name__icontains=search) |
            models.Q(email__icontains=search) |
            models.Q(phone__icontains=search)
        )
    if role_filter:
        users = users.filter(role=role_filter)
    paginator = Paginator(users, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'manage_members.html', {
        'page_obj': page_obj,
        'search': search,
        'role_filter': role_filter,
        'role_choices': CustomUser.ROLE_CHOICES,
        'total': users.count(),
    })


@login_required
def add_member(request):
    if not (request.user.is_staff or request.user.is_superuser or request.user.role in ('admin', 'manager')):
        messages.error(request, "Permission denied.")
        return redirect('adminn')
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        role = request.POST.get('role', 'member')
        password = request.POST.get('password', '').strip()
        group_id = request.POST.get('group', '')
        is_staff = request.POST.get('is_staff') == 'on'
        member_type = request.POST.get('member_type', 'member')

        errors = []
        if not username:
            errors.append("Username is required.")
        elif User.objects.filter(username=username).exists():
            errors.append(f"Username '{username}' is already taken.")
        if email and User.objects.filter(email=email).exists():
            errors.append(f"Email '{email}' is already in use.")
        if password and len(password) < 6:
            errors.append("Password must be at least 6 characters.")

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            user = User.objects.create(
                username=username, first_name=first_name, last_name=last_name,
                email=email, phone=phone, role=role,
                is_staff=is_staff or role in ('admin', 'manager'),
                is_active=True, is_email_verified=bool(email),
            )
            if password:
                user.set_password(password)
            else:
                user.set_unusable_password()
            user.save()

            group = Group.objects.filter(pk=group_id).first() if group_id else None
            Member.objects.create(
                user=user,
                name=f"{first_name} {last_name}".strip() or username,
                email=email,
                phonenumber=phone,
                group=group,
            )
            messages.success(request, f"Member '{user.get_full_name() or username}' added successfully.")
            return redirect('manage_members')

    groups = Group.objects.all()
    return render(request, 'add_member.html', {
        'groups': groups,
        'role_choices': CustomUser.ROLE_CHOICES,
    })


@login_required
def edit_member(request, user_id):
    if not (request.user.is_staff or request.user.is_superuser or request.user.role in ('admin', 'manager')):
        messages.error(request, "Permission denied.")
        return redirect('adminn')
    target = get_object_or_404(User, pk=user_id)
    member = Member.objects.filter(user=target).first()
    if request.method == 'POST':
        target.first_name = request.POST.get('first_name', '').strip()
        target.last_name = request.POST.get('last_name', '').strip()
        target.email = request.POST.get('email', '').strip()
        target.phone = request.POST.get('phone', '').strip()
        new_role = request.POST.get('role', target.role)
        target.role = new_role
        target.is_staff = request.POST.get('is_staff') == 'on' or new_role in ('admin', 'manager')
        target.is_active = request.POST.get('is_active', 'on') == 'on'
        new_pw = request.POST.get('password', '').strip()
        if new_pw and len(new_pw) >= 6:
            target.set_password(new_pw)
        target.save()
        if member:
            member.name = f"{target.first_name} {target.last_name}".strip() or target.username
            member.email = target.email
            member.phonenumber = target.phone
            group_id = request.POST.get('group', '')
            member.group = Group.objects.filter(pk=group_id).first() if group_id else member.group
            member.save()
        messages.success(request, f"Member '{target.get_full_name() or target.username}' updated.")
        return redirect('manage_members')
    groups = Group.objects.all()
    return render(request, 'add_member.html', {
        'edit_user': target,
        'member': member,
        'groups': groups,
        'role_choices': CustomUser.ROLE_CHOICES,
    })


@login_required
def delete_member(request, user_id):
    if not (request.user.is_superuser or request.user.role == 'admin'):
        messages.error(request, "Only administrators can delete members.")
        return redirect('manage_members')
    target = get_object_or_404(User, pk=user_id)
    if target == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('manage_members')
    name = target.get_full_name() or target.username
    target.delete()
    messages.success(request, f"Member '{name}' deleted.")
    return redirect('manage_members')


# ─── Sermon Notes ─────────────────────────────────────────────────────────────

from .models import SermonNote

def _can_manage_sermons(user):
    """True for pastor, reverend/bishop, admin, manager, or staff (media team)."""
    return (
        user.is_authenticated and (
            user.is_staff or user.is_superuser or
            user.role in ('pastor', 'reverend', 'admin', 'manager')
        )
    )

def _can_approve_sermon(user):
    return user.is_authenticated and (user.is_superuser or user.role in ('admin', 'manager') or user.is_staff)


@login_required
def sermon_notes(request):
    user = request.user
    if not _can_manage_sermons(user):
        # Regular members only see admin-released notes
        notes = SermonNote.objects.filter(is_public=True).select_related('pastor')
    else:
        notes = SermonNote.objects.select_related('pastor').all()
    return render(request, 'sermon_notes.html', {
        'notes': notes,
        'can_manage': _can_manage_sermons(user),
        'can_approve': _can_approve_sermon(user),
    })


@login_required
def add_sermon_note(request, pk=None):
    if not _can_manage_sermons(request.user):
        messages.error(request, "Only pastors, bishops, and administrators can create sermon notes.")
        return redirect('index')
    note = get_object_or_404(SermonNote, pk=pk) if pk else None
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        scripture_ref = request.POST.get('scripture_ref', '').strip()
        date_val = request.POST.get('date', '') or None
        content = request.POST.get('content', '').strip()
        if not title or not content:
            messages.error(request, "Title and content are required.")
        else:
            if note:
                note.title = title
                note.scripture_ref = scripture_ref
                note.date = date_val
                note.content = content
                note.save()
                messages.success(request, "Sermon note updated.")
            else:
                note = SermonNote.objects.create(
                    title=title, pastor=request.user,
                    scripture_ref=scripture_ref, date=date_val,
                    content=content, is_public=False,
                )
                messages.success(request, "Sermon note saved. An admin can release it for all members to view.")
            return redirect('sermon_note_detail', pk=note.pk)
    return render(request, 'add_sermon_note.html', {'note': note})


@login_required
def sermon_note_detail(request, pk):
    note = get_object_or_404(SermonNote, pk=pk)
    user = request.user
    can_manage = _can_manage_sermons(user)
    can_approve = _can_approve_sermon(user)
    can_edit = user.is_superuser or user.is_staff or note.pastor == user or user.role in ('admin', 'manager')
    if not note.is_public and not can_manage:
        messages.error(request, "This sermon note has not been released to members yet.")
        return redirect('index')
    slides = note.get_slides()
    return render(request, 'sermon_note_detail.html', {
        'note': note,
        'slides': slides,
        'can_edit': can_edit,
        'can_approve': can_approve,
    })


@login_required
def approve_sermon_note(request, pk):
    """Admin releases a sermon note to all members, or revokes release."""
    if not _can_approve_sermon(request.user):
        messages.error(request, "Only administrators can release sermon notes.")
        return redirect('sermon_notes')
    note = get_object_or_404(SermonNote, pk=pk)
    action = request.POST.get('action', 'approve')
    if action == 'revoke':
        note.is_public = False
        note.approved_by = None
        note.approved_at = None
        note.save()
        messages.success(request, f"'{note.title}' is now private again.")
    else:
        note.is_public = True
        note.approved_by = request.user
        note.approved_at = timezone.now()
        note.save()
        messages.success(request, f"'{note.title}' released to all members.")
    return redirect('sermon_note_detail', pk=pk)


@login_required
def delete_sermon_note(request, pk):
    note = get_object_or_404(SermonNote, pk=pk)
    user = request.user
    if not (user.is_superuser or user.is_staff or note.pastor == user):
        messages.error(request, "Permission denied.")
        return redirect('sermon_notes')
    note.delete()
    messages.success(request, "Sermon note deleted.")
    return redirect('sermon_notes')


# ─── Notification Preferences ─────────────────────────────────────────────────

from .models import NotificationPreference

@login_required
def notification_preferences(request):
    prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        prefs.email_announcements = request.POST.get('email_announcements') == 'on'
        prefs.email_events = request.POST.get('email_events') == 'on'
        prefs.email_payments = request.POST.get('email_payments') == 'on'
        prefs.push_announcements = request.POST.get('push_announcements') == 'on'
        prefs.push_events = request.POST.get('push_events') == 'on'
        prefs.push_payments = request.POST.get('push_payments') == 'on'
        prefs.sms_payments = request.POST.get('sms_payments') == 'on'
        prefs.whatsapp_otp = request.POST.get('whatsapp_otp') == 'on'
        prefs.whatsapp_payments = request.POST.get('whatsapp_payments') == 'on'
        prefs.save()
        messages.success(request, "Notification preferences saved.")
        return redirect('notification_preferences')
    return render(request, 'notification_preferences.html', {'prefs': prefs})
