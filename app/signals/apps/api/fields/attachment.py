# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2019 - 2023 Gemeente Amsterdam
from collections import OrderedDict

from signals.apps.signals.utils.links import HTTPSLinksField
from django.db.models import Model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.reverse import reverse

from signals.apps.api.generics.exceptions import UnsupportedModelTypeException
from signals.apps.signals.models import Attachment


class PublicSignalAttachmentLinksField(HTTPSLinksField):
    lookup_field = 'uuid'

    def to_representation(self, value: Attachment) -> OrderedDict:
        request = self.context.get('request')
        assert isinstance(request, Request)

        result = OrderedDict([
            ('self',
             {'href': self.get_url(value._signal, "public-signals-attachments", request, None)}),
        ])

        return result


@extend_schema_field({
    'type': 'object',
    'properties': {
        'self': {
            'type': 'object',
            'properties': {
                'href': {
                    'type': 'string',
                    'format': 'uri',
                    'example': 'https://api.example.com/signals/v1/private/signals/1/attachments/1'
                }
            }
        }
    }
})
class PrivateSignalAttachmentLinksField(HTTPSLinksField):
    def to_representation(self, value: Attachment) -> OrderedDict:
        request = self.context.get('request')
        assert isinstance(request, Request)

        # Set the kwargs before calling get_url
        self.kwargs = {
            'parent_lookup__signal__pk': value._signal_id,
            'pk': value.pk
        }

        result = OrderedDict([
            ('self', {
                'href': self.get_url(
                    value,
                    'private-signals-attachments-detail',
                    request,
                    None
                ) if value.pk else None
            }),
        ])

        # Reset kwargs after use
        self.kwargs = None

        return result

@extend_schema_field({
    'type': 'string',
    'format': 'uri',
    'example': 'https://api.example.com/signals/v1/private/signals/1/attachments/1'
})
class PrivateSignalAttachmentRelatedField(serializers.HyperlinkedRelatedField):
    def get_url(self, obj: Model, view_name: str, request: Request, format: str | None) -> str:
        if not isinstance(obj, Attachment):
            raise UnsupportedModelTypeException('Only Attachment type models are supported!')

        kwargs = {
            'parent_lookup__signal__pk': obj._signal_id,
            'pk': obj.pk
        }
        
        return reverse(view_name, kwargs=kwargs, request=request, format=format)