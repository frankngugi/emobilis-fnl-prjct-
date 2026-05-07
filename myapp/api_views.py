import requests as http_req
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from django.conf import settings

from .models import (
    Events, Attendee, Announcement, Hymn, Group, Member,
    Images, Video, Payment, RoleRequest, CustomUser, MEDIA_CATEGORY_CHOICES, EVENT_CATEGORY_CHOICES
)
from .serializers import (
    RegisterSerializer, UserSerializer, ProfileUpdateSerializer,
    AnnouncementSerializer, AnnouncementCreateSerializer,
    EventSerializer, EventCreateSerializer,
    HymnListSerializer, HymnDetailSerializer,
    GroupSerializer,
    ImageSerializer, VideoSerializer,
    PaymentSerializer, PaymentInitiateSerializer,
)
from .views import _mpesa_stk_push

User = get_user_model()


# ── Auth ─────────────────────────────────────────────────────────────────────

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        if not username or not password:
            return Response({'error': 'Username and password required.'}, status=400)
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials.'}, status=401)
        if not user.is_active:
            return Response({'error': 'Account is disabled.'}, status=403)
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user, context={'request': request}).data,
        })


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            Member.objects.get_or_create(
                email=user.email,
                defaults={'user': user, 'name': user.get_full_name() or user.username}
            )
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user, context={'request': request}).data,
            }, status=201)
        return Response(serializer.errors, status=400)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user, context={'request': request}).data)

    def patch(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user, context={'request': request}).data)
        return Response(serializer.errors, status=400)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        old_pw = request.data.get('old_password', '')
        new_pw = request.data.get('new_password', '')
        if not request.user.check_password(old_pw):
            return Response({'error': 'Current password is incorrect.'}, status=400)
        if len(new_pw) < 8:
            return Response({'error': 'New password must be at least 8 characters.'}, status=400)
        request.user.set_password(new_pw)
        request.user.save()
        return Response({'message': 'Password changed successfully.'})


# ── Announcements ─────────────────────────────────────────────────────────────

class AnnouncementListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AnnouncementSerializer

    def get_queryset(self):
        return Announcement.objects.filter(is_published=True).order_by('-date_posted')


class AnnouncementCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = AnnouncementCreateSerializer

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

    def create(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser or request.user.role in ('admin', 'manager')):
            return Response({'error': 'Permission denied.'}, status=403)
        return super().create(request, *args, **kwargs)


# ── Events ────────────────────────────────────────────────────────────────────

class EventListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = EventSerializer

    def get_queryset(self):
        qs = Events.objects.filter(date__gte=timezone.now().date())
        cat = self.request.query_params.get('cat', '')
        if cat:
            qs = qs.filter(category=cat)
        return qs

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data['categories'] = EVENT_CATEGORY_CHOICES
        return response


class EventCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EventCreateSerializer

    def perform_create(self, serializer):
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only staff can create events.')
        serializer.save(organizer=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def register_for_event(request, event_id):
    try:
        event = Events.objects.get(pk=event_id)
    except Events.DoesNotExist:
        return Response({'error': 'Event not found.'}, status=404)
    _, created = Attendee.objects.get_or_create(
        user=request.user, event=event,
        defaults={'phonenumber': request.user.phone or ''}
    )
    if created:
        return Response({'message': f'Registered for {event.title}!'})
    return Response({'message': 'Already registered for this event.'})


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def unregister_from_event(request, event_id):
    Attendee.objects.filter(user=request.user, event_id=event_id).delete()
    return Response({'message': 'Unregistered from event.'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_events(request):
    attendees = Attendee.objects.filter(user=request.user).select_related('event')
    events = [a.event for a in attendees]
    return Response(EventSerializer(events, many=True, context={'request': request}).data)


# ── Hymns ─────────────────────────────────────────────────────────────────────

class HymnListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = HymnListSerializer

    def get_queryset(self):
        qs = Hymn.objects.all()
        q = self.request.query_params.get('q', '')
        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(author__icontains=q)
        return qs


class HymnDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = HymnDetailSerializer
    queryset = Hymn.objects.all()


# ── Bible proxy ───────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def bible_verse(request):
    ref = request.query_params.get('ref', 'John 3:16')
    try:
        resp = http_req.get(
            f"https://bible-api.com/{ref.replace(' ', '%20')}",
            timeout=10
        )
        if resp.status_code == 200:
            return Response(resp.json())
        return Response({'error': 'Verse not found.'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=503)


# ── Groups ────────────────────────────────────────────────────────────────────

class GroupListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = GroupSerializer
    queryset = Group.objects.all()


class GroupDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = GroupSerializer
    queryset = Group.objects.all()


class GroupCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not (request.user.is_staff or request.user.is_superuser or request.user.role in ('admin', 'manager')):
            return Response({'error': 'Permission denied.'}, status=403)
        name = request.data.get('name', '').strip()
        description = request.data.get('description', '').strip()
        category = request.data.get('category', 'other')
        if not name or not description:
            return Response({'error': 'Name and description required.'}, status=400)
        if Group.objects.filter(name__iexact=name).exists():
            return Response({'error': f"Group '{name}' already exists."}, status=400)
        group = Group.objects.create(name=name, description=description, category=category, leader=request.user)
        return Response(GroupSerializer(group, context={'request': request}).data, status=201)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def join_group(request, group_id):
    try:
        group = Group.objects.get(pk=group_id)
    except Group.DoesNotExist:
        return Response({'error': 'Group not found.'}, status=404)
    member, _ = Member.objects.get_or_create(
        user=request.user,
        defaults={'email': request.user.email, 'name': request.user.get_full_name() or request.user.username}
    )
    member.group = group
    member.save()
    return Response({'message': f'Joined {group.name}!'})


# ── Gallery ───────────────────────────────────────────────────────────────────

class ImageListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ImageSerializer

    def get_queryset(self):
        qs = Images.objects.all()
        cat = self.request.query_params.get('cat', '')
        if cat:
            qs = qs.filter(category=cat)
        return qs

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data['categories'] = MEDIA_CATEGORY_CHOICES
        return response


# ── Videos ───────────────────────────────────────────────────────────────────

class VideoListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = VideoSerializer

    def get_queryset(self):
        qs = Video.objects.all()
        cat = self.request.query_params.get('cat', '')
        if cat:
            qs = qs.filter(category=cat)
        return qs


# ── Contributions / M-Pesa ────────────────────────────────────────────────────

class PaymentListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')[:20]


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def initiate_payment(request):
    serializer = PaymentInitiateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    data = serializer.validated_data
    phone = str(data['phone_number']).lstrip('+').lstrip('0')
    if not phone.startswith('254'):
        phone = '254' + phone
    payment = Payment.objects.create(
        user=request.user if request.user.is_authenticated else None,
        amount=data['amount'],
        phone_number=phone,
        purpose=data['purpose'],
    )
    result = _mpesa_stk_push(phone, float(data['amount']), data['purpose'], payment.id)
    # Also send SMS confirmation if payment succeeded
    if result.get('success'):
        payment.checkout_request_id = result.get('checkout_request_id', '')
        payment.save()
        return Response({
            'message': 'STK Push sent! Check your phone to complete payment.',
            'payment_id': payment.id,
            'checkout_request_id': payment.checkout_request_id,
        })
    else:
        return Response({
            'message': result.get('error', 'Payment initiation failed.'),
            'payment_id': payment.id,
        }, status=400)


# ── Admin Dashboard ───────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def admin_dashboard(request):
    if not (request.user.is_staff or request.user.is_superuser or request.user.role in ('admin', 'manager')):
        return Response({'error': 'Admin access required.'}, status=403)

    from .models import RoleRequest
    pending_role_requests = RoleRequest.objects.filter(status='pending').count()

    return Response({
        'total_members': Member.objects.count(),
        'total_events': Events.objects.count(),
        'total_groups': Group.objects.count(),
        'total_payments': Payment.objects.filter(status='completed').count(),
        'total_hymns': Hymn.objects.count(),
        'pending_role_requests': pending_role_requests,
        'recent_payments': PaymentSerializer(
            Payment.objects.order_by('-created_at')[:5], many=True
        ).data,
        'recent_members': UserSerializer(
            User.objects.order_by('-date_joined')[:5],
            many=True, context={'request': request}
        ).data,
        'upcoming_events': EventSerializer(
            Events.objects.filter(date__gte=timezone.now().date()).order_by('date')[:5],
            many=True, context={'request': request}
        ).data,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def all_members(request):
    if not (request.user.is_staff or request.user.is_superuser or request.user.role in ('admin', 'manager')):
        return Response({'error': 'Admin access required.'}, status=403)
    users = User.objects.all().order_by('-date_joined')
    return Response(UserSerializer(users, many=True, context={'request': request}).data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_user_role(request, user_id):
    if not (request.user.is_superuser or request.user.role == 'admin'):
        return Response({'error': 'Only admins can change roles.'}, status=403)
    try:
        target = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)
    new_role = request.data.get('role', 'member')
    target.role = new_role
    target.is_staff = new_role in ('admin', 'manager')
    target.save()
    return Response({'message': f'{target.username} is now {new_role}.'})


# ── Categories (metadata) ─────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def categories_meta(request):
    return Response({
        'media_categories': MEDIA_CATEGORY_CHOICES,
        'event_categories': EVENT_CATEGORY_CHOICES,
        'group_categories': [c for c in Group.CATEGORY_CHOICES],
    })
