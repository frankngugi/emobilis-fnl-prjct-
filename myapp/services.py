"""
RGC Notification Services
-  send_email()            — Gmail SMTP (FREE)
-  send_push()             — Expo Push Notifications (FREE, for mobile app)
-  send_push_to_user()     — Send push to all devices of a user
-  send_push_to_all()      — Broadcast to all app users (announcements etc.)
-  send_sms()              — Africa's Talking (paid, optional)
-  send_phone_otp()        — Twilio Verify (optional, email OTP is default)
-  verify_phone_otp()      — Twilio Verify check
-  notify_user()           — Email + Push (free) + SMS (optional)

NOTE: Twilio is NOT required. Email OTP works out of the box.
      Push notifications replace SMS for mobile app users — completely FREE.
      Africa's Talking SMS is available but costs ~KES 1.20/msg.
"""
import logging
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


# ── Email ─────────────────────────────────────────────────────────────────────

def send_email(subject: str, message: str, to: list[str], html_message: str = '') -> bool:
    """Send email via Gmail SMTP (or console in dev). Returns True on success."""
    try:
        if html_message:
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=to,
            )
            email.attach_alternative(html_message, 'text/html')
            email.send()
        else:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=to,
                fail_silently=False,
            )
        logger.info(f'Email sent to {to}: {subject}')
        return True
    except Exception as e:
        logger.error(f'Email failed to {to}: {e}')
        return False


def send_registration_email(user) -> bool:
    subject = f'Welcome to {settings.CHURCH_NAME}!'
    message = (
        f'Dear {user.first_name or user.username},\n\n'
        f'Welcome to {settings.CHURCH_NAME}!\n\n'
        f'Your account has been created successfully.\n'
        f'Username: {user.username}\n\n'
        f'You can now:\n'
        f'- Read the Bible and hymns\n'
        f'- Register for church events\n'
        f'- Give via M-Pesa\n'
        f'- Join a ministry group\n\n'
        f'God bless you!\n{settings.CHURCH_NAME}\n{settings.CHURCH_LOCATION}'
    )
    return send_email(subject, message, [user.email])


def send_event_reminder_email(user, event) -> bool:
    subject = f'Reminder: {event.title} — {settings.CHURCH_SHORT_NAME}'
    message = (
        f'Dear {user.first_name or user.username},\n\n'
        f'This is a reminder that you are registered for:\n\n'
        f'  Event: {event.title}\n'
        f'  Date:  {event.date}\n'
        f'  Time:  {event.time}\n'
        f'  Venue: {event.location}\n\n'
        f'We look forward to seeing you!\n\n'
        f'God bless you,\n{settings.CHURCH_NAME}'
    )
    return send_email(subject, message, [user.email])


def send_payment_confirmation_email(user, payment) -> bool:
    subject = f'Payment Received — {settings.CHURCH_SHORT_NAME}'
    message = (
        f'Dear {user.first_name or user.username},\n\n'
        f'We have received your contribution. Thank you!\n\n'
        f'  Amount:  KES {payment.amount}\n'
        f'  Purpose: {payment.get_purpose_display()}\n'
        f'  Receipt: {payment.mpesa_receipt_number or "Pending"}\n'
        f'  Date:    {payment.created_at.strftime("%d %b %Y, %I:%M %p")}\n\n'
        f'"Each of you should give what you have decided in your heart..."\n'
        f'— 2 Corinthians 9:7\n\n'
        f'God bless you!\n{settings.CHURCH_NAME}'
    )
    return send_email(subject, message, [user.email])


def send_role_approval_email(user, new_role: str) -> bool:
    subject = f'Role Approved — {settings.CHURCH_SHORT_NAME}'
    message = (
        f'Dear {user.first_name or user.username},\n\n'
        f'Your role upgrade request has been approved.\n\n'
        f'You are now a: {new_role.upper()}\n\n'
        f'You can now access the admin dashboard at:\n'
        f'/adminn/\n\n'
        f'God bless you!\n{settings.CHURCH_NAME}'
    )
    return send_email(subject, message, [user.email])


def send_announcement_email(announcement, recipient_emails: list[str]) -> bool:
    subject = f'{"[URGENT] " if announcement.is_urgent else ""}{announcement.title} — {settings.CHURCH_SHORT_NAME}'
    message = (
        f'Church Announcement\n'
        f'{"=" * 40}\n\n'
        f'{announcement.title}\n\n'
        f'{announcement.content}\n\n'
        f'{"=" * 40}\n'
        f'Posted by: {announcement.posted_by.get_full_name() or announcement.posted_by.username}\n'
        f'{settings.CHURCH_NAME} · {settings.CHURCH_LOCATION}'
    )
    return send_email(subject, message, recipient_emails)


# ── Expo Push Notifications (FREE) ───────────────────────────────────────────

EXPO_PUSH_URL = 'https://exp.host/--/api/v2/push/send'


def send_push(token: str, title: str, body: str, data: dict = None, sound: str = 'default') -> bool:
    """
    Send a single push notification via Expo's free push service.
    Token format: 'ExponentPushToken[xxxx]'
    Returns True on success.
    """
    import requests as _req
    payload = {
        'to': token,
        'title': title,
        'body': body,
        'sound': sound,
        'data': data or {},
    }
    try:
        resp = _req.post(
            EXPO_PUSH_URL,
            json=payload,
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
            timeout=10,
        )
        result = resp.json()
        status = result.get('data', {}).get('status', '')
        if status == 'error':
            details = result.get('data', {}).get('details', {})
            error = details.get('error', 'unknown')
            if error == 'DeviceNotRegistered':
                # Token is stale — remove it
                from .models import PushToken
                PushToken.objects.filter(token=token).delete()
                logger.info(f'Removed stale push token: {token[:20]}...')
            else:
                logger.warning(f'Push notification error for {token[:20]}...: {error}')
            return False
        logger.info(f'Push sent to {token[:20]}...: {title}')
        return True
    except Exception as e:
        logger.error(f'Push failed: {e}')
        return False


def send_push_batch(tokens: list[str], title: str, body: str, data: dict = None) -> int:
    """Send push to multiple tokens in one request. Returns count of successes."""
    if not tokens:
        return 0
    import requests as _req
    messages = [{'to': t, 'title': title, 'body': body, 'sound': 'default', 'data': data or {}} for t in tokens]
    try:
        resp = _req.post(
            EXPO_PUSH_URL,
            json=messages,
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
            timeout=15,
        )
        results = resp.json().get('data', [])
        ok = sum(1 for r in results if r.get('status') == 'ok')
        # Clean up stale tokens
        stale = [messages[i]['to'] for i, r in enumerate(results)
                 if r.get('details', {}).get('error') == 'DeviceNotRegistered']
        if stale:
            from .models import PushToken
            PushToken.objects.filter(token__in=stale).delete()
        return ok
    except Exception as e:
        logger.error(f'Batch push failed: {e}')
        return 0


def send_push_to_user(user, title: str, body: str, data: dict = None) -> int:
    """Send push notification to all devices registered for a user. Returns count sent."""
    from .models import PushToken
    tokens = list(PushToken.objects.filter(user=user).values_list('token', flat=True))
    if not tokens:
        return 0
    return send_push_batch(tokens, title, body, data)


def send_push_to_all(title: str, body: str, data: dict = None) -> int:
    """Broadcast push notification to ALL app users (e.g. for announcements)."""
    from .models import PushToken
    tokens = list(PushToken.objects.values_list('token', flat=True))
    if not tokens:
        logger.info('No push tokens registered yet — no push notifications sent')
        return 0
    sent = 0
    chunk_size = 100  # Expo recommends max 100 per request
    for i in range(0, len(tokens), chunk_size):
        sent += send_push_batch(tokens[i:i + chunk_size], title, body, data)
    logger.info(f'Broadcast push sent to {sent}/{len(tokens)} devices')
    return sent


def push_new_announcement(announcement) -> int:
    """Push notification when a new announcement is posted."""
    title = f'{"🚨 " if announcement.is_urgent else "📢 "}{announcement.title}'
    body = announcement.content[:120] + ('...' if len(announcement.content) > 120 else '')
    return send_push_to_all(title, body, data={'screen': 'announcements', 'id': announcement.id})


def push_event_reminder(user, event) -> int:
    """Push reminder for an event the user is registered for."""
    title = f'📅 Reminder: {event.title}'
    body = f'{event.date} at {str(event.time)[:5]} — {event.location}'
    return send_push_to_user(user, title, body, data={'screen': 'events', 'id': event.id})


def push_payment_confirmed(user, payment) -> int:
    """Push payment confirmation."""
    title = '✅ Payment Received — RGC Nyahururu'
    body = f'KES {payment.amount} ({payment.get_purpose_display()}) confirmed. Receipt: {payment.mpesa_receipt_number or "pending"}'
    return send_push_to_user(user, title, body, data={'screen': 'give'})


# ── Twilio Phone OTP (optional — skip if not configured) ─────────────────────

def send_phone_otp(phone: str) -> dict:
    """
    Send OTP to phone via Twilio Verify.
    Phone must be in E.164 format: +254712345678
    Returns {'success': True} or {'success': False, 'error': '...'}
    """
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_VERIFY_SERVICE_SID]):
        return {'success': False, 'error': 'Twilio not configured. Check TWILIO_* in msys/.env'}
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        # Normalize phone to E.164
        phone_e164 = _normalize_phone(phone)
        client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID) \
            .verifications.create(to=phone_e164, channel='sms')
        logger.info(f'OTP sent to {phone_e164}')
        return {'success': True, 'phone': phone_e164}
    except Exception as e:
        logger.error(f'OTP send failed: {e}')
        return {'success': False, 'error': str(e)}


def verify_phone_otp(phone: str, code: str) -> dict:
    """
    Verify OTP code via Twilio Verify.
    Returns {'success': True, 'status': 'approved'} or {'success': False, ...}
    """
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_VERIFY_SERVICE_SID]):
        return {'success': False, 'error': 'Twilio not configured'}
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        phone_e164 = _normalize_phone(phone)
        result = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID) \
            .verification_checks.create(to=phone_e164, code=code)
        if result.status == 'approved':
            logger.info(f'Phone {phone_e164} verified successfully')
            return {'success': True, 'status': 'approved'}
        return {'success': False, 'status': result.status, 'error': 'Invalid or expired OTP'}
    except Exception as e:
        logger.error(f'OTP verify failed: {e}')
        return {'success': False, 'error': str(e)}


# ── Africa's Talking SMS ──────────────────────────────────────────────────────

def send_sms(phone: str, message: str) -> dict:
    """
    Send SMS via Africa's Talking.
    Phone: '0712345678' or '+254712345678'
    Returns {'success': True, 'recipients': [...]} or {'success': False, 'error': '...'}
    """
    api_key = settings.AT_API_KEY
    username = settings.AT_USERNAME

    if not api_key or api_key == 'PASTE_YOUR_AT_API_KEY_HERE':
        logger.warning('Africa\'s Talking not configured. SMS not sent.')
        return {'success': False, 'error': 'Africa\'s Talking API key not set in msys/.env'}

    try:
        import africastalking
        africastalking.initialize(username, api_key)
        sms = africastalking.SMS
        phone_e164 = _normalize_phone(phone)
        response = sms.send(message, [phone_e164])
        recipients = response.get('SMSMessageData', {}).get('Recipients', [])
        success_count = sum(1 for r in recipients if r.get('status') == 'Success')
        logger.info(f'SMS sent to {phone_e164}: {success_count} success')
        return {'success': success_count > 0, 'recipients': recipients}
    except Exception as e:
        logger.error(f'SMS failed: {e}')
        return {'success': False, 'error': str(e)}


def send_payment_sms(phone: str, amount, purpose: str, receipt: str = '') -> bool:
    message = (
        f'RGC Nyahururu: Payment received!\n'
        f'Amount: KES {amount}\n'
        f'Purpose: {purpose}\n'
        f'{f"Receipt: {receipt}" if receipt else "Processing..."}\n'
        f'God bless you!'
    )
    result = send_sms(phone, message)
    return result.get('success', False)


def send_event_reminder_sms(phone: str, event_title: str, event_date, event_time) -> bool:
    message = (
        f'RGC Nyahururu: Reminder!\n'
        f'{event_title}\n'
        f'Date: {event_date}\n'
        f'Time: {event_time}\n'
        f'See you there!'
    )
    result = send_sms(phone, message)
    return result.get('success', False)


def send_welcome_sms(phone: str, name: str) -> bool:
    message = (
        f'Welcome to Redeemed Gospel Church Nyahururu, {name}!\n'
        f'Your account is ready.\n'
        f'"Where everybody is somebody"'
    )
    result = send_sms(phone, message)
    return result.get('success', False)


# ── Combined notifier ─────────────────────────────────────────────────────────

def notify_user(user, subject: str, email_body: str, push_body: str = '', sms_body: str = '') -> dict:
    """
    Send notification to user via all available free channels first, then paid.
    Priority: Email (free) → Push notification (free) → SMS (paid, optional)
    """
    results = {'email': False, 'push': 0, 'sms': False}
    # Email (always free)
    if user.email:
        results['email'] = send_email(subject, email_body, [user.email])
    # Push notification (free for app users)
    if push_body:
        results['push'] = send_push_to_user(user, subject, push_body)
    # SMS (optional, costs money — only if AT is configured and sms_body given)
    if sms_body and settings.AT_API_KEY and settings.AT_API_KEY != 'PASTE_YOUR_AT_API_KEY_HERE':
        if user.phone:
            result = send_sms(user.phone, sms_body)
            results['sms'] = result.get('success', False)
    return results


# ── Helpers ───────────────────────────────────────────────────────────────────

def _normalize_phone(phone: str) -> str:
    """Convert 0712345678 or 254712345678 to +254712345678"""
    phone = str(phone).strip().replace(' ', '').replace('-', '')
    if phone.startswith('+'):
        return phone
    if phone.startswith('254'):
        return '+' + phone
    if phone.startswith('0'):
        return '+254' + phone[1:]
    return '+254' + phone
