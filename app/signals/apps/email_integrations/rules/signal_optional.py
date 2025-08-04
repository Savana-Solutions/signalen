# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021 - 2022 Gemeente Amsterdam
from signals.apps.email_integrations.rules.abstract import AbstractRule
from signals.apps.signals import workflow


class SignalOptionalRule(AbstractRule):
    def _validate_status(self, status):
        """
        Run status validations for the Rule

        - The status is REPORTED, AWAITING, IN_PROGRESS, ON_HOLD, CLOSURE_REQUESTED, CANCELLED or PLANNED
        - send_mail must be True
        """
        return self._validate_status_state(status) and self._validate_status_send_mail(status)

    def _validate_status_state(self, status):
        """
        Validate that the status is one of:
         - REPORTED
         - AWAITING
         - IN_PROGRESS
         - ON_HOLD
         - CLOSURE_REQUESTED
         - CANCELLED
         - PLANNED
        """
        return status.state in [
            workflow.REPORTED,
            workflow.AWAITING,
            workflow.IN_PROGRESS,
            workflow.ON_HOLD,
            workflow.CLOSURE_REQUESTED,
            workflow.CANCELLED,
            workflow.PLANNED,
        ]

    def _validate_status_send_mail(self, status):
        return status.send_email
