# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2019 - 2023 Gemeente Amsterdam
from django.core.exceptions import ValidationError as DjangoCoreValidationError
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from signals.apps.api.ml_tool.client import MLToolClient
from signals.apps.signals.models import Category

import json
import logging

logger = logging.getLogger(__name__)

@extend_schema(exclude=True)
class LegacyMlPredictCategoryView(APIView):
    ml_tool_client = MLToolClient()

    _default_category_url = None
    default_category = None

    def __init__(self, *args, **kwargs):
        # When we cannot translate we return the 'overig-overig' category url
        self.default_category = Category.objects.get(slug='overig', parent__isnull=False, parent__slug='overig')

        super().__init__(*args, **kwargs)

    @property
    def default_category_url(self):
        if not self._default_category_url and self.default_category:
            request = self.request if self.request else None
            self._default_category_url = self.default_category.get_absolute_url(request=request)
        return self._default_category_url

    def post(self, request, *args, **kwargs):
        try:
            logger.info(f"Request data: {request.data}")
            logger.info(f"Request headers: {request.headers}")

            text = request.data.get('text', '')
            if not text:
                return Response({'error': 'Text is required'}, status=status.HTTP_400_BAD_REQUEST)

            response = self.ml_tool_client.predict(text=text)
            
            logger.info(f"ML tool response status: {response.status_code}")
            logger.info(f"ML tool response content: {response.content}")

        except DjangoCoreValidationError as e:
            raise ValidationError(e.message, e.code)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if response.status_code == 200:
            try:
                response_data = response.json()
                data = {'hoofdrubriek': [], 'subrubriek': []}

                for key in ['hoofdrubriek', 'subrubriek']:
                    category_urls = []
                    probabilities = []

                    for url, probability in zip(response_data[key][0], response_data[key][1]):
                        try:
                            category = Category.objects.get_from_url(url=url)
                            category_url = category.get_absolute_url(request=request)
                        except Category.DoesNotExist:
                            logger.warning(f"Category not found for URL: {url}")
                            category_url = self.default_category_url

                        category_urls.append(category_url)
                        probabilities.append(probability)

                    data[key].append(category_urls)
                    data[key].append(probabilities)

                # Ensure the protocol is consistent
                data = self.normalize_urls(data, request)

                return Response(data)
            except json.JSONDecodeError:
                logger.error("Invalid JSON in ML tool response")
                return Response({'error': 'Invalid JSON in ML tool response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error(f"ML tool prediction failed: {response.content}")
            return Response({'error': f'ML tool prediction failed: {response.content}'}, status=response.status_code)

    def normalize_urls(self, data, request):
        scheme = 'https' if request.is_secure() else 'http'
        host = request.get_host()

        for key in ['hoofdrubriek', 'subrubriek']:
            data[key][0] = [
                f"{scheme}://{host}{url[url.index('/signals'):] if '/signals' in url else url}"
                for url in data[key][0]
            ]

        return data