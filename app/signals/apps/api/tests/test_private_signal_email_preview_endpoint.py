# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2022 Gemeente Amsterdam
from unittest.mock import patch

from django.contrib.auth.models import Permission

from signals.apps.email_integrations.models import EmailTemplate
from signals.apps.feedback.models import Feedback
from signals.apps.questionnaires.models import Questionnaire
from signals.apps.signals import workflow
from signals.apps.signals.factories import SignalFactoryValidLocation, StatusFactory
from signals.test.utils import SIAReadUserMixin, SIAReadWriteUserMixin, SignalsBaseApiTestCase


class TestPrivateSignalEmailPreview(SIAReadUserMixin, SIAReadWriteUserMixin, SignalsBaseApiTestCase):
    def setUp(self):
        self.signal = SignalFactoryValidLocation.create()

        self.sia_read_write_user.user_permissions.add(Permission.objects.get(codename='sia_can_view_all_categories'))
        self.client.force_authenticate(user=self.sia_read_write_user)

        # 2 templates for the special cases where there are URL's in the body. All other templates will use the fallback
        EmailTemplate.objects.create(key=EmailTemplate.SIGNAL_STATUS_CHANGED_AFGEHANDELD,
                                     title='Uw melding {{ signal_id }}'
                                           f' {EmailTemplate.SIGNAL_STATUS_CHANGED_AFGEHANDELD}',
                                     body='{{ text }} {{ created_at }} {{ status_text }} {{ positive_feedback_url }} '
                                          '{{ negative_feedback_url }}{{ ORGANIZATION_NAME }}')
        EmailTemplate.objects.create(key=EmailTemplate.SIGNAL_STATUS_CHANGED_REACTIE_GEVRAAGD,
                                     title='Uw melding {{ signal_id }}'
                                           f' {EmailTemplate.SIGNAL_STATUS_CHANGED_REACTIE_GEVRAAGD}',
                                     body='{{ text }} {{ created_at }} {{ status_text }} {{ reaction_url }} '
                                          '{{ ORGANIZATION_NAME }}')

    def test_get_email_preview_status_reactie_gevraagd(self):
        # Make sure there are no questionnaire objects in the database
        self.assertEqual(Questionnaire.objects.count(), 0)

        currently_set_status = self.signal.status
        status_count = self.signal.statuses.count()

        text = f'Lorem ipsum {workflow.REACTION_REQUESTED} ...'
        endpoint = f'/signals/v1/private/signals/{self.signal.id}/email/preview/'

        response = self.client.post(endpoint, data={'status': workflow.REACTION_REQUESTED, 'text': text}, format='json')
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertEqual(f'Uw melding {self.signal.id} {EmailTemplate.SIGNAL_STATUS_CHANGED_REACTIE_GEVRAAGD}',
                         response_data['subject'])
        self.assertIn(text, response_data['html'])

        # assert that the reactie gevraagd link is in the preview
        self.assertIn('incident/reactie/00000000-0000-0000-0000-000000000000', response_data['html'])

        # Refresh the Signal
        self.signal.refresh_from_db()

        # The same status should be set as before
        self.assertEqual(currently_set_status.id, self.signal.status.id)
        self.assertEqual(currently_set_status.state, self.signal.status.state)
        self.assertEqual(currently_set_status.text, self.signal.status.text)
        self.assertEqual(currently_set_status.send_email, self.signal.status.send_email)

        # no new notes are added to the signal
        self.assertEqual(self.signal.statuses.count(), status_count)

        # no questionnaire object should have been made
        self.assertEqual(Questionnaire.objects.count(), 0)

    def test_get_email_preview_status_handled(self):
        # Make sure there are no feedback objects in the database
        self.assertEqual(Feedback.objects.count(), 0)

        currently_set_status = self.signal.status
        status_count = self.signal.statuses.count()

        text = f'Lorem ipsum {workflow.COMPLETED} ...'
        endpoint = f'/signals/v1/private/signals/{self.signal.id}/email/preview/'

        response = self.client.post(endpoint, data={'status': workflow.COMPLETED, 'text': text}, format='json')
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertEqual(f'Uw melding {self.signal.id} {EmailTemplate.SIGNAL_STATUS_CHANGED_AFGEHANDELD}',
                         response_data['subject'])
        self.assertIn(text, response_data['html'])

        # assert that the KTO links are in the preview
        self.assertIn('kto/ja/00000000-0000-0000-0000-000000000000', response_data['html'])
        self.assertIn('kto/nee/00000000-0000-0000-0000-000000000000', response_data['html'])

        # Refresh the Signal
        self.signal.refresh_from_db()

        # The same status should be set as before
        self.assertEqual(currently_set_status.id, self.signal.status.id)
        self.assertEqual(currently_set_status.state, self.signal.status.state)
        self.assertEqual(currently_set_status.text, self.signal.status.text)
        self.assertEqual(currently_set_status.send_email, self.signal.status.send_email)

        # no new notes are added to the signal
        self.assertEqual(self.signal.statuses.count(), status_count)

        # no feedback object should have been made
        self.assertEqual(Feedback.objects.count(), 0)

    def test_get_email_preview_status(self):
        currently_set_status = self.signal.status
        status_count = self.signal.statuses.count()

        for new_status in [workflow.REPORTED, workflow.AWAITING, workflow.IN_PROGRESS, workflow.CANCELLED, ]:
            text = f'Lorem ipsum {new_status} ...'
            endpoint = f'/signals/v1/private/signals/{self.signal.id}/email/preview/'

            response = self.client.post(endpoint, data={'status': new_status, 'text': text}, format='json')
            self.assertEqual(response.status_code, 200)

            response_data = response.json()
            self.assertEqual(f'Meer over uw melding {self.signal.get_id_display()}', response_data['subject'])
            self.assertIn(text, response_data['html'])

            # Refresh the Signal
            self.signal.refresh_from_db()

            # The same status should be set as before
            self.assertEqual(currently_set_status.id, self.signal.status.id)
            self.assertEqual(currently_set_status.state, self.signal.status.state)
            self.assertEqual(currently_set_status.text, self.signal.status.text)
            self.assertEqual(currently_set_status.send_email, self.signal.status.send_email)

            # no new notes are added to the signal
            self.assertEqual(self.signal.statuses.count(), status_count)

        # We need to test workflow.CLOSURE_REQUESTED seperatly because we cannot transition to this state from
        # the state REPORTED

        status = StatusFactory.create(_signal=self.signal, state=workflow.AWAITING)
        self.signal.status = status
        self.signal.save()

        status_count = self.signal.statuses.count()

        text = f'Lorem ipsum {workflow.CLOSURE_REQUESTED} ...'
        endpoint = f'/signals/v1/private/signals/{self.signal.id}/email/preview/'

        response = self.client.post(endpoint, data={'status': workflow.CLOSURE_REQUESTED, 'text': text},
                                    format='json')
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertEqual(f'Meer over uw melding {self.signal.get_id_display()}', response_data['subject'])
        self.assertIn(text, response_data['html'])

        # Refresh the Signal
        self.signal.refresh_from_db()

        # The same status should be set as before
        self.assertEqual(status.id, self.signal.status.id)
        self.assertEqual(status.state, self.signal.status.state)
        self.assertEqual(status.text, self.signal.status.text)
        self.assertEqual(status.send_email, self.signal.status.send_email)

        # no new notes are added to the signal
        self.assertEqual(self.signal.statuses.count(), status_count)

    @patch('signals.apps.email_integrations.services.MailService')
    def test_no_email_preview_missing_email_actions(self, patched):
        # Test handling of missing email rules.
        patched.actions = []

        text = f'Lorem ipsum {workflow.IN_PROGRESS} ...'
        endpoint = f'/signals/v1/private/signals/{self.signal.id}/email/preview/'

        response = self.client.post(endpoint, data={'status': workflow.IN_PROGRESS, 'text': text}, format='json')
        self.assertEqual(response.status_code, 404)

    def test_no_email_preview_for_forbidden_state_transition(self):
        # For a forbidden state transition (see workflow.py) we want the same
        # error message for email previews and (failed) state transitions.
        text = f'Lorem ipsum {workflow.REACTION_RECEIVED} ...'
        endpoint = f'/signals/v1/private/signals/{self.signal.id}/email/preview/'
        signals_endpoint = f'/signals/v1/private/signals/{self.signal.id}'

        response = self.client.post(endpoint, data={'status': workflow.REACTION_RECEIVED, 'text': text}, format='json')
        self.assertEqual(response.status_code, 400)
        preview_response_json = response.json()

        response = self.client.patch(
            signals_endpoint, data={'status': {'state': workflow.REACTION_RECEIVED, 'text': text}}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), preview_response_json)  # matching error message

    def test_no_email_preview_state_te_verzenden(self):
        # Test documenting edge case. The workflow.TO_SEND state has no
        # email rule and requires the `target_api` property that cannot be set
        # through the email preview viewset/serializer. In this case we want
        # an HTTP 400.
        text = f'Lorem ipsum {workflow.TO_SEND} ...'
        endpoint = f'/signals/v1/private/signals/{self.signal.id}/email/preview/'

        response = self.client.post(endpoint, data={'status': workflow.TO_SEND, 'text': text}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_missing_required_query_parameter(self):
        # The status query parameter is required
        endpoint = f'/signals/v1/private/signals/{self.signal.id}/email/preview/'
        response = self.client.post(endpoint, format='json')
        self.assertEqual(response.status_code, 400)

    def test_not_authenticated(self):
        self.client.logout()

        endpoint = f'/signals/v1/private/signals/{self.signal.id}/email/preview/'
        response = self.client.post(endpoint)
        self.assertEqual(response.status_code, 401)

        self.client.force_authenticate(user=self.sia_read_write_user)

    def test_no_object_permission(self):
        # The sia_read_user should not be able to access the signal and therefore also not the email preview
        self.client.logout()
        self.client.force_authenticate(user=self.sia_read_user)

        endpoint = f'/signals/v1/private/signals/{self.signal.id}/email/preview/'
        response = self.client.post(endpoint)
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        self.client.force_authenticate(user=self.sia_read_write_user)
