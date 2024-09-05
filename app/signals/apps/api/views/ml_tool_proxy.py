# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2019 - 2023 Gemeente Amsterdam
from django.core.exceptions import ValidationError as DjangoCoreValidationError
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from signals.apps.api.ml_tool.client import MLToolClient
from signals.apps.signals.models import Category


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
            response = self.ml_tool_client.predict(text=request.data['text'])
        except DjangoCoreValidationError as e:
            raise ValidationError(e.message, e.code)

        if response.status_code == 200:
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
                        category_url = self.default_category_url

                    category_urls.append(category_url)
                    probabilities.append(probability)

                data[key].append(category_urls)
                data[key].append(probabilities)

            return Response(data)
        else:
            # Handle non-200 responses
            return Response({'error': 'ML tool prediction failed'}, status=response.status_code)
