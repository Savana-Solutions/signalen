# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2018 - 2024 Gemeente Amsterdam
import os
from typing import Callable

import json
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse
from django.urls import resolve

from signals import __version__

class SecureURLMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def secure_url(self, url: str) -> str:
        """Convert HTTP URLs to HTTPS except for localhost"""
        if url and isinstance(url, str) and url.startswith('http://') and 'localhost' not in url:
            return url.replace('http://', 'https://')
        return url

    def secure_data(self, data):
        """Recursively secure URLs in data structure"""
        if isinstance(data, dict):
            return {k: self.secure_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.secure_data(item) for item in data]
        elif isinstance(data, str):
            return self.secure_url(data)
        return data

    def __call__(self, request):
        # Patch request.build_absolute_uri to use HTTPS
        original_build_absolute_uri = request.build_absolute_uri

        def secure_build_absolute_uri(location=None):
            return self.secure_url(original_build_absolute_uri(location))

        request.build_absolute_uri = secure_build_absolute_uri
        
        # Get response with secured request
        response = self.get_response(request)
        
        # Handle JSON responses
        if getattr(response, 'content_type', None) and 'application/json' in response.content_type:
            try:
                content = response.content.decode('utf-8')
                json_data = json.loads(content)
                
                # Recursively secure all URLs in the JSON structure
                secured_data = self.secure_data(json_data)
                
                # Convert back to JSON string
                secured_content = json.dumps(secured_data)
                response.content = secured_content.encode('utf-8')
                response['Content-Length'] = len(response.content)
            except Exception as e:
                print(f"Error in SecureURLMiddleware JSON handling: {e}")

        # Handle redirects
        if hasattr(response, 'url'):
            secure_url = self.secure_url(response.url)
            if secure_url != response.url:
                from django.http import HttpResponseRedirect
                return HttpResponseRedirect(secure_url)

        # Ensure secure headers
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response

class APIVersionHeaderMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Versioning
        # ==========
        # SIA / Signalen follows the semantic versioning standard. Previously we had
        # separate version numbers for the V0 (now defunct) and V1 versions of the API.
        # We now no longer separately version these, as their releases were always
        # tied to the backend. For backwards compatibility, and to not break external
        # systems that rely on SIA / Signalen we still expose all the separate version
        # numbers, but they are now all the same.

        response = self.get_response(request)
        response['X-API-Version'] = __version__
        return response


class SessionLoginMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        if request.user and not isinstance(request.user, AnonymousUser):
            if request.path.startswith('/signals/v1/private'):
                login(request, request.user, settings.AUTHENTICATION_BACKENDS[0])

        return response


class MaintenanceModeMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        maintenance_mode: bool = os.getenv('MAINTENANCE_MODE', False) in settings.TRUE_VALUES
        if maintenance_mode and not resolve(request.path_info).url_name == 'health_check':
            response = HttpResponse('API in maintenance mode', status=503)
        else:
            response = self.get_response(request)

        return response
