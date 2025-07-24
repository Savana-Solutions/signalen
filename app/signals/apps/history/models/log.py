# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021 - 2023 Gemeente Amsterdam
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from signals.apps.questionnaires.models import Questionnaire
from signals.apps.signals.models.signal_departments import SignalDepartments
from signals.apps.signals.models.type import _history_translated_action
from signals.apps.signals.workflow import STATUS_CHOICES


class Log(models.Model):
    ACTION_UNKNOWN = 'UNKNOWN'
    ACTION_CREATE = 'CREATE'
    ACTION_UPDATE = 'UPDATE'
    ACTION_DELETE = 'DELETE'
    ACTION_RECEIVE = 'RECEIVE'
    ACTION_NOT_RECEIVED = 'NOT_RECEIVED'

    ACTION_CHOICES = (
        (ACTION_UNKNOWN, 'Unknown'),
        (ACTION_CREATE, 'Created'),
        (ACTION_UPDATE, 'Updated'),
        (ACTION_DELETE, 'Deleted'),
        (ACTION_RECEIVE, 'Received'),
        (ACTION_NOT_RECEIVED, 'Not received'),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING, related_name='+')
    object_pk = models.CharField(max_length=128, db_index=True)
    object = GenericForeignKey('content_type', 'object_pk')

    action = models.CharField(editable=False, max_length=20, choices=ACTION_CHOICES, default=ACTION_UNKNOWN)
    description = models.TextField(max_length=3000, null=True, blank=True)
    extra = models.TextField(max_length=255, null=True, blank=True)
    data = models.JSONField(null=True)

    created_by = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(editable=False)

    # This is a reference to a specific Signal. It can be blank if the object does not have a relation to a Signal.
    #
    # We want this to be here so that for the Signal history endpoint we can easily select all history for that specific
    # Signal.
    #
    # When creating history log for any changes on a Signal make sure to use the SignalLogService. In the future more
    # LogService classes can and will be created to facilitate the history logging of other objects.
    _signal = models.ForeignKey('signals.Signal', on_delete=models.CASCADE, related_name='history_log',
                                blank=True, null=True)

    class Meta:
        ordering = ('-created_at', )
        indexes = [
            models.Index(fields=['content_type', 'object_pk', ])
        ]

    def __str__(self) -> str:
        representation = f'{self.action} on {self.content_type.name} #{self.object_pk}'
        if self._signal:
            representation = f'{representation}, on signal #{self._signal_id}'
        return representation

    # START - Backwards compatibility functions
    #
    # To keep the history endpoint intact the following functions are defined to mimic the history view in the database

    def translate_content_type(self, content_type_name) -> str:
        """
        Present for backwards compatibility
        """
        content_type_translations = {
            'category assignment': 'category_assignment',
            'service level objective': 'sla',
            'type': 'type_assignment',
            'signal user': 'user_assignment',
        }

        if content_type_name in content_type_translations:
            return content_type_translations[content_type_name]
        elif content_type_name == 'signal departments':
            assert self.object

            if self.object.relation_type == SignalDepartments.REL_ROUTING:
                content_type_name = 'routing_assignment'
            elif self.object.relation_type == SignalDepartments.REL_DIRECTING:
                content_type_name = 'directing_departments_assignment'

        return content_type_name

    @staticmethod
    def translate_what_to_action(what) -> str:
        """
        Present for backwards compatibility
        """
        return what[:what.find('_')]

    @staticmethod
    def translate_what_to_content_type(what) -> str:
        """
        Present for backwards compatibility
        """
        # Note: this should produce a content_type.model not .name
        translations = {
            'category_assignment': 'categoryassignment',
            'sla': 'servicelevelobjective',
            'type_assignment': 'type',
            'user_assignment': 'signaluser',
            'routing_assignment': 'signaldepartments',
            'directing_departments_assignment': 'signaldepartments',
        }

        content_type = what[what.find('_') + 1:].lower()
        if content_type in translations:
            content_type = translations[content_type]
        return content_type

    @property
    def identifier(self) -> str:
        """
        "identifier" in the style of the signals_history_view
        Present for backwards compatibility
        """
        return f'{self.what}_{self.object_pk}'

    @property
    def what(self) -> str:
        """
        "what" in the style of the signals_history_view
        Present for backwards compatibility
        """
        translated_content_type = self.translate_content_type(self.content_type.name)
        return f'{self.action}_{translated_content_type}'.upper()

    @property
    def who(self) -> str:
        """
        "who" in the style of the signals_history_view
        Present for backwards compatibility
        """
        return self.created_by or 'SEDA System'

    def get_action(self) -> str:  # noqa C901
        """
        "get_action" copied from History
        Present for backwards compatibility
        """
        action = 'Action unknown.'
        what = self.what
        if what == 'UPDATE_STATUS':
            _status_choice = 'Unknown'
            if self.extra:
                _status_choice = dict(STATUS_CHOICES).get(self.extra, 'Unknown')

            action = f'Status changed to: {_status_choice}'
        elif what == 'UPDATE_PRIORITY':
            _priority = 'Unknown'
            if self.extra:
                _priority = {'high': 'High', 'normal': 'Normal', 'low': 'Low'}.get(self.extra, 'Unknown')
            action = f'Changed urgency to: {_priority}'
        elif what == 'UPDATE_CATEGORY_ASSIGNMENT':
            action = f'Category changed to: {self.extra}'
        elif what == 'UPDATE_LOCATION':
            action = 'Location changed to:'
        elif what == 'CREATE_NOTE':
            action = 'Added note:'
        elif what == 'RECEIVE_FEEDBACK' or what == 'CREATE_FEEDBACK':
            action = 'Received feedback from reporter'
        elif what == 'UPDATE_TYPE_ASSIGNMENT':
            action = f'Type changed to: {_history_translated_action(self.extra)}'
        elif what == 'UPDATE_DIRECTING_DEPARTMENTS_ASSIGNMENT':
            action = f'Region changed to: {self.extra or "Responsible department"}'
        elif what == 'UPDATE_ROUTING_ASSIGNMENT':
            _route_assignment = self.extra or 'Responsible department (routing)'
            action = f'Routing: afdeling/afdelingen gewijzigd naar: {_route_assignment}'
        elif what == 'UPDATE_USER_ASSIGNMENT':
            if self.extra:
                action = f'Report assignment changed to: {self.extra}'
            else:
                action = 'Report no longer assigned to reporter.'
        elif what == 'CREATE_SIGNAL' and self.object_pk != self._signal_id:
            action = 'Split report added'
        elif what == 'UPDATE_SLA':
            action = 'Service promise:'
        elif what == 'RECEIVE_SESSION':
            assert self.object
            assert self.object.questionnaire

            if self.object.questionnaire.flow == Questionnaire.FORWARD_TO_EXTERNAL:
                action = 'Receive clarification'
        elif what == 'NOT_RECEIVED_SESSION':
            assert self.object
            assert self.object.questionnaire

            if self.object.questionnaire.flow == Questionnaire.FORWARD_TO_EXTERNAL:
                action = 'No clarification received'
        elif what == 'UPDATE_REPORTER':
            action = 'Contact information of reporter:'

        return action

    def get_description(self) -> str | None:
        """
        "get_description" copied from History
        Present for backwards compatibility
        """
        description = self.description
        what = self.what
        if what == 'UPDATE_LOCATION' or what == 'RECEIVE_FEEDBACK':
            assert self.object

            description = self.object.get_description()
        elif what == 'CHILD_SIGNAL_CREATED':
            description = f'Report {self.extra}'
        elif what == 'UPDATE_SLA' and self.description is None:
            description = 'Service promise unknown'

        return description

    # END - Backwards compatibility functions
