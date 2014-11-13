"""OLI analytics service event tracker backend."""

from __future__ import absolute_import

import json
import logging

import requests
from requests.exceptions import RequestException

from django.contrib.auth.models import User

from student.models import anonymous_id_for_user
from track.backends import BaseBackend


log = logging.getLogger(__name__)


class OLIAnalyticsBackend(BaseBackend):

    def __init__(self, **kwargs):
        """
        Connect to an OLI analytics service.

        :Parameters:

          - `endpoint`: endpoint to put events
          - `timeout_seconds`: timeout in seconds

        """

        super(OLIAnalyticsBackend, self).__init__(**kwargs)

        self.endpoint = kwargs.get('endpoint')
        self.timeout_seconds = kwargs.get('timeout_seconds', 0.100)
        self.secret = kwargs.get('secret')


    def send(self, event):
        """Forward the event to the OLI analytics server"""

        if not self.endpoint or not self.secret:
            return

        if event.get('event_type', '') != 'problem_check':
            return

        if event.get('event_source', '') != 'server':
            return

        context = event.get('context')
        if not context:
            return

        course_id = context.get('course_id')
        if not course_id:
            return

        user_id = context.get('user_id')
        if not user_id:
            return

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return

        event_data = event.get('event', {})
        if not event_data:
            return

        problem_id = event_data.get('problem_id')
        if not problem_id:
            return

        success = event_data.get('success')
        if not success:
            return

        is_correct = success == 'correct'

        payload = {
            'course_id': course_id,
            'resource_id': problem_id,
            'student_id': self._get_student_id(user),
            'result': is_correct
        }
        headers = {
            'Authorization': self._get_authorization_header()
        }

        request_payload = {'request': json.dumps({'payload': json.dumps(payload)})}
        try:
            response = requests.put(
                self.endpoint,
                data=request_payload,
                timeout=self.timeout_seconds,
                headers=headers
            )
            response.raise_for_status()
            log.info(response.text)
        except RequestException:
            log.warning('Unable to send event to OLI analytics service', exc_info=True)

    def _get_student_id(self, user):
        return anonymous_id_for_user(user, None)

    def _get_authorization_header(self):
        return self.secret
