# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2018 - 2021 Gemeente Amsterdam
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework import exceptions

from .tokens import JWTAccessToken

USER_NOT_AUTHORIZED = "User {} is not authorized"
USER_DOES_NOT_EXIST = -1


class JWTAuthBackend:
    """
    Retrieve user from backend and cache the result
    """

    @staticmethod  # noqa: C901
    def get_user(user_id):
        user = cache.get(user_id)

        if user == USER_DOES_NOT_EXIST:
            raise exceptions.AuthenticationFailed(USER_NOT_AUTHORIZED.format(user_id))

        if user is None:  # Cache miss
            try:
                user = User.objects.get(username__iexact=user_id)
            except User.DoesNotExist:
                # Instead of raising an exception, create a new user
                user = User.objects.create_user(username=user_id, email=user_id)
                # Optionally set default roles or permissions here
                user.user_permissions.add(Permission.objects.get(codename='sia_read'))

                user.save()
                cache.set(user_id, user, 5 * 60)  # Cache the new user
            else:
                cache.set(user_id, user, 5 * 60)

        if not user.is_active:
            raise exceptions.AuthenticationFailed("User inactive")
        return user

    """
    Authenticate. Check if required scope is present and get user_email from JWT token.
    use ALWAYS_OK = True to skip token verification. Useful for local dev/testing
    """

    @staticmethod  # noqa: C901
    def authenticate(request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        claims, user_id = JWTAccessToken.token_data(auth_header)
        if user_id == "ALWAYS_OK":
            user_id = settings.TEST_LOGIN

        auth_user = JWTAuthBackend.get_user(user_id)
        # We return only when we have correct scope, and user is known to `signals`.
        # TODO remove default empty scope
        return auth_user, ""

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return 'Bearer realm="signals"'
