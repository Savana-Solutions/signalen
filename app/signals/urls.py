# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2018 - 2023 Gemeente Amsterdam
import os
from django.http import HttpResponse
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from signals.apps.api.generics.routers import BaseSignalsAPIRootView

# Remove "view website" button in the Django admin
admin.site.site_url = None

# Define the view at the project level
def security_txt_view(request):
    canonical_url = os.getenv('SIGNALEN_CANONICAL_URL')
    # Use string concatenation or formatting to control whitespace
    content_lines = [
        "Contact: mailto:support@mycleancity.nl",
        "Expires: 2024-12-31T23:00:00.000Z",
        f"Canonical: {canonical_url}",
    ]
    content = "\n".join(content_lines) + "\n"  # Ensure the file ends with a newline character
    return HttpResponse(content, content_type='text/plain')

def robots_txt_view(request):
    lines = [
        "User-agent: *",
        "Disallow: /",
        # Allow or disallow paths as needed
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

urlpatterns = [
    # Used to determine API health when deploying
    path('status/', include('signals.apps.health.urls')),
    
    # The Signals application is routed with `/signals/` as path.
    path('signals/', BaseSignalsAPIRootView.as_view()),
    path('signals/', include('signals.apps.api.urls')),

    # The Django admin
    path('signals/admin/', admin.site.urls),
    re_path(r'^signals/markdownx/', include('markdownx.urls')),

    # SOAP stand-in endpoints
    path('signals/sigmax/', include('signals.apps.sigmax.urls')),

    # Add the path for security.txt
    re_path(r'^.well-known/security.txt$', security_txt_view, name='security_txt'),

    # Add the path for robots.txt
    re_path(r'^robots.txt$', robots_txt_view, name='robots_txt'),

]

if settings.DEBUG:
    from django.conf.urls.static import static

    media_root = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += media_root

if settings.OIDC_RP_CLIENT_ID:
    urlpatterns += [
        path('signals/oidc/login_failure/', TemplateView.as_view(template_name='admin/oidc/login_failure.html')),
        path('signals/oidc/', include('mozilla_django_oidc.urls')),
    ]

if settings.SILK_ENABLED:
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]

# DRF Spectacular
urlpatterns += [
    path('signals/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('signals/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
