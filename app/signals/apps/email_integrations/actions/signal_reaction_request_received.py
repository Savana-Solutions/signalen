# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021 - 2023 Gemeente Amsterdam
from signals.apps.email_integrations.actions.abstract import AbstractSignalStatusAction
from signals.apps.email_integrations.models import EmailTemplate
from signals.apps.email_integrations.rules import SignalReactionRequestReceivedRule
from signals.apps.email_integrations.rules.abstract import AbstractRule
from signals.apps.signals.models import Signal


class SignalReactionRequestReceivedAction(AbstractSignalStatusAction):
    rule: AbstractRule = SignalReactionRequestReceivedRule()

    key: str = EmailTemplate.SIGNAL_STATUS_CHANGED_REACTIE_ONTVANGEN
    subject: str = 'More about your report {formatted_signal_id}'

    note: str = 'Automatic email for Response received has been sent to the reporter.'

    def get_additional_context(self, signal: Signal, dry_run: bool = False) -> dict:
        assert signal.status is not None

        return {'reaction_request_answer': signal.status.text}
