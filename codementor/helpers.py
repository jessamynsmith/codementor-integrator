from django.conf import settings
from django.contrib.sites.models import Site


def get_full_domain():
    scheme = 'https'
    if not settings.SSL_ENABLED:
        scheme = 'http'
    return '%s://%s' % (scheme, Site.objects.get_current().domain)
