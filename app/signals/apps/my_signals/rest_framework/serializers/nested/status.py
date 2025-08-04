# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2022 Gemeente Amsterdam
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from signals.apps.signals import workflow
from signals.apps.signals.models import Status


class _NestedMySignalStatusSerializer(ModelSerializer):
    state = SerializerMethodField(method_name='get_public_state')
    state_display = SerializerMethodField(method_name='get_public_state_display')

    class Meta:
        model = Status
        fields = (
            'state',
            'state_display',
        )

    def get_public_state(self, obj):

        if obj.state in [workflow.REOPENED, workflow.REACTION_REQUESTED, workflow.REACTION_RECEIVED, ]:
            return obj.state.upper()
        elif obj.state in [workflow.COMPLETED, workflow.CANCELLED, workflow.SPLIT, ]:
            return 'CLOSED'
        else:
            return 'OPEN'

    def get_public_state_display(self, obj):
        _status_state_translations = {workflow.REOPENED: 'Reopened',
                                      workflow.CANCELLED: 'Afgesloten',
                                      workflow.COMPLETED: 'Afgesloten',
                                      workflow.SPLIT: 'Afgesloten',
                                      workflow.REACTION_REQUESTED: 'Vraag aan u verstuurd',
                                      workflow.REACTION_RECEIVED: 'Antwoord van u ontvangen'}
        return _status_state_translations.get(obj.state, 'Open')
