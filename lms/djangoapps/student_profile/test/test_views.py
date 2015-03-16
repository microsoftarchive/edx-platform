# -*- coding: utf-8 -*-
""" Tests for student profile views. """

from django.test import TestCase
from django.core.urlresolvers import reverse

from util.testing import UrlResetMixin
from openedx.core.djangoapps.user_api.api import account as account_api


class LearnerProfileTest(UrlResetMixin, TestCase):
    """ Tests for the student profile views. """

    USERNAME = u"sour.heart"
    PASSWORD = u"forgotten"
    EMAIL = u"sour.heart@useless.com"

    def setUp(self):
        super(LearnerProfileTest, self).setUp("student_profile.urls")

        # Create/activate a new account
        activation_key = account_api.create_account(self.USERNAME, self.PASSWORD, self.EMAIL)
        account_api.activate_account(activation_key)

        # Login
        result = self.client.login(username=self.USERNAME, password=self.PASSWORD)
        self.assertTrue(result)

    def test_learner_profile_view(self):
        """
        Verify that lerner profile view is rendered with correct data.
        """
        profile_path = reverse('learner_profile')
        response = self.client.get(path=profile_path)
        accounts_api_url = reverse("accounts_api", kwargs={'username': self.USERNAME})

        self.assertTrue('href="{}"'.format(profile_path) in response.content)
        self.assertTrue('data-accounts-api-url="{}"'.format(accounts_api_url) in response.content)
