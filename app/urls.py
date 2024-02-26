from django.http import HttpResponse
from django.contrib import admin
from django.urls import include, path
import os

# Define the view at the project level
def security_txt_view():
    canonical_url = os.getenv('SIGNALEN_CANONICAL_URL')
    content = f"""
    Contact: mailto:support@mycleancity.nl
    Expires: 2025-12-31T23:00:00.000Z
    Canonical: {canonical_url}
    """
    return HttpResponse(content, content_type='text/plain')

# Include this pattern before including app URLs
urlpatterns = [
    path('security.txt', security_txt_view),
    path('signals/', include('app.signals.urls')),  # This line includes your app-specific URLs
]
