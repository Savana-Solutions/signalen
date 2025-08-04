# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021 - 2022 Gemeente Amsterdam
from signals.apps.email_integrations.rules.abstract import AbstractRule
from signals.apps.signals.models import Status
from signals.apps.signals.workflow import COMPLETED, REQUEST_TO_REOPEN


class SignalHandledRule(AbstractRule):
    def _validate_status(self, status):
        """
        Run status validations for the Rule

        - The status is COMPLETED
        - The previous state is not REQUEST_TO_REOPEN
        """
        return self._validate_status_state(status) and self._validate_previous_state_not_VERZOEK_TOT_HEROPENEN(status)

    def _validate_status_state(self, status):
        """
        Validate that the status is COMPLETED
        """
        return status.state == COMPLETED

    def _validate_previous_state_not_VERZOEK_TOT_HEROPENEN(self, status):
        """
        Validate that the previous state is not REQUEST_TO_REOPEN
        """
        return Status.objects.filter(
            _signal_id=status._signal_id
        ).exclude(
            id=status.id
        ).order_by('-created_at').values_list(
            'state',
            flat=True
        ).first() != REQUEST_TO_REOPEN
