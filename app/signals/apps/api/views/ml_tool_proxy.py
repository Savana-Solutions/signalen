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
            # Ensure the content type is application/json
            request.content_type = 'application/json'
            
            # Print request data for debugging
            print(f"Request data: {request.data}")
            print(f"Request headers: {request.headers}")

            # Ensure text is properly formatted in JSON
            data = json.dumps({'text': request.data.get('text', '')})
            
            response = self.ml_tool_client.predict(text=data)
            
            # Print response data for debugging
            print(f"ML tool response status: {response.status_code}")
            print(f"ML tool response content: {response.content}")

        except DjangoCoreValidationError as e:
            raise ValidationError(e.message, e.code)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
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
                            category_url = self.default_category_url

                        category_urls.append(category_url)
                        probabilities.append(probability)

                    data[key].append(category_urls)
                    data[key].append(probabilities)

                return Response(data)
            except json.JSONDecodeError:
                return Response({'error': 'Invalid JSON in ML tool response'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # Handle non-200 responses
            return Response({'error': f'ML tool prediction failed: {response.content}'}, status=response.status_code)
