# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2018 - 2023 Gemeente Amsterdam
import os
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from signals.apps.api.generics.routers import BaseSignalsAPIRootView

# Remove "view website" button in the Django admin
admin.site.site_url = None

urlpatterns = [
    # Used to determine API health when deploying
    path('status/', include('signals.apps.health.urls')),
    
    # The Signals application is routed behind the HAproxy with `/signals/` as path.
    path('', BaseSignalsAPIRootView.as_view()),
    path('', include('signals.apps.api.urls')),

    # The Django admin
    path('admin/', admin.site.urls),
    re_path(r'^markdownx/', include('markdownx.urls')),

    # SOAP stand-in endpoints
    path('sigmax/', include('signals.apps.sigmax.urls')),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    media_root = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += media_root

if settings.OIDC_RP_CLIENT_ID:
    urlpatterns += [
        path('oidc/login_failure/', TemplateView.as_view(template_name='admin/oidc/login_failure.html')),
        path('oidc/', include('mozilla_django_oidc.urls')),
    ]

if settings.SILK_ENABLED:
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]

# DRF Spectacular
urlpatterns += [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
