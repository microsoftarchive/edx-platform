""" Views for a student's account information. """

import logging

from django.conf import settings
from django_countries import countries

from django.core.urlresolvers import reverse, resolve
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from dark_lang.models import DarkLangConfig
from edxmako.shortcuts import render_to_response, render_to_string

from student.models import UserProfile


@login_required
@require_http_methods(['GET'])
def learner_profile(request, username):
    """Render the students profile page.
    Args:
        request (HttpRequest)
    Returns:
        HttpResponse: 200 if the page was sent successfully
        HttpResponse: 302 if not logged in (redirect to login page)
        HttpResponse: 405 if using an unsupported HTTP method
    Example usage:
        GET /account/profile
    """

    released_languages = DarkLangConfig.current().released_languages_list

    # add in the default language if it's not in the list of released languages
    if settings.LANGUAGE_CODE not in released_languages:
        released_languages.append(settings.LANGUAGE_CODE)
        # Re-alphabetize language options
        released_languages.sort()

    language_options = [language for language in settings.LANGUAGES if language[0] in released_languages]

    country_options = [
        (country_code, unicode(country_name))
        for country_code, country_name in sorted(
            countries.countries, key=lambda(__, name): unicode(name)
        )
    ]

    context = {
        # TODO! Replace with profile API url once available
        'profile_api_url': reverse("accounts_api", kwargs={'username': request.user.username}),
        'account_settings_page_url': 'path/to/account/settings',
        # TODO! Remove/Update (keys,values) once profile API url is available
        'profile_data': {
            'show_visibility_section': request.user.username == username,
            'show_limited_profile_message': True,
            'profile_visibility': True,           # True: Full Profile, False: Limited Profile
            'username': request.user.username,
            'country_options': country_options,
            'language_options': language_options,
            'bio': "Let's not get into details :)"
        }
    }
    return render_to_response('student_profile/learner_profile.html', context)