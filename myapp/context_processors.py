from .models import SiteSettings


def site_settings(request):
    try:
        s = SiteSettings.get()
        return {'mpesa_enabled': s.mpesa_enabled}
    except Exception:
        return {'mpesa_enabled': False}
