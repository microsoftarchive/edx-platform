"""
Utility functions for validating forms
"""
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.hashers import UNUSABLE_PASSWORD
from django.contrib.auth.tokens import default_token_generator

from django.utils.http import int_to_base36
from django.utils.translation import ugettext as _
from django.template import loader

from django.conf import settings
from microsite_configuration import microsite


class PasswordResetFormNoActive(PasswordResetForm):
    def clean_email(self):
        """
        This is a literal copy from Django 1.4.5's django.contrib.auth.forms.PasswordResetForm
        Except removing the requirement of active users
        Validates that a user exists with the given email address.
        """
        email = self.cleaned_data["email"]
        #The line below contains the only change, removing is_active=True
        self.users_cache = User.objects.filter(email__iexact=email)
        if not len(self.users_cache):
            raise forms.ValidationError(self.error_messages['unknown'])
        if any((user.password == UNUSABLE_PASSWORD)
               for user in self.users_cache):
            raise forms.ValidationError(self.error_messages['unusable'])
        return email

    def save(
            self,
            domain_override=None,
            subject_template_name='registration/password_reset_subject.txt',
            email_template_name='registration/password_reset_email.html',
            use_https=False,
            token_generator=default_token_generator,
            from_email=settings.DEFAULT_FROM_EMAIL,
            request=None
    ):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        # This import is here because we are copying and modifying the .save from Django 1.4.5's
        # django.contrib.auth.forms.PasswordResetForm directly, which has this import in this place.
        from django.core.mail import send_mail
        for user in self.users_cache:
            if not domain_override:
                site_name = microsite.get_value(
                    'SITE_NAME',
                    settings.SITE_NAME
                )
            else:
                site_name = domain_override
            context = {
                'email': user.email,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                'platform_name': microsite.get_value('platform_name', settings.PLATFORM_NAME)
            }
            subject = loader.render_to_string(subject_template_name, context)
            # Email subject *must not* contain newlines
            subject = subject.replace('\n', '')
            email = loader.render_to_string(email_template_name, context)
            send_mail(subject, email, from_email, [user.email])


class NullableCharField(forms.CharField):
    """
    Like a CharField but distinguishes between None and the empty string
    """
    def to_python(self, value):
        return None if value is None else super(NullableCharField, self).to_python(value)


def _make_true_field(error_message):
    """
    Returns a required field that only accepts the string "true"
    """
    return forms.RegexField(
        regex="true",
        error_messages={
            "required": error_message,
            "invalid": error_message
        }
    )


class AccountCreationForm(forms.Form):
    """
    A form to for account creation data. It is currently only used for
    validation, not rendering.
    """
    # TODO: Resolve repetition
    username = forms.SlugField(
        min_length=2,
        max_length=30,
        error_messages={
            "required": _("Username must be minimum of two characters long"),
            "invalid": _("Username should only consist of A-Z and 0-9, with no spaces."),
            "min_length": _("Username must be minimum of two characters long"),
            "max_length": _("Username cannot be more than %(limit_value)s characters long"),
        }
    )
    email = forms.EmailField(
        max_length=75,  # Limit per RFCs is 254, but User's email field in django 1.4 only takes 75
        error_messages={
            "required": _("A properly formatted e-mail is required"),
            "invalid": _("A properly formatted e-mail is required"),
            "max_length": _("Email cannot be more than %(limit_value)s characters long"),
        }
    )
    password = forms.CharField(
        min_length=2,
        error_messages={
            "required": _("A valid password is required"),
            "min_length": _("A valid password is required"),
        }
    )
    name = forms.CharField(
        min_length=2,
        error_messages={
            "required": _("Your legal name must be a minimum of two characters long"),
            "min_length": _("Your legal name must be a minimum of two characters long"),
        }
    )

    def __init__(
            self,
            data=None,
            extra_fields={},
            extended_profile_fields={},
            enforce_password_policy=False,
            tos_required=True
    ):
        super(AccountCreationForm, self).__init__(data)

        self.extended_profile_fields = extended_profile_fields
        self.enforce_password_policy = enforce_password_policy
        if tos_required:
            self.fields["terms_of_service"] = _make_true_field(
                _("You must accept the terms of service.")
            )

        # TODO: These messages don't say anything about minimum length
        error_message_dict = {
            "level_of_education": _("A level of education is required"),
            "gender": _("Your gender is required"),
            "year_of_birth": _("Your year of birth is required"),
            "mailing_address": _("Your mailing address is required"),
            "goals": _("A description of your goals is required"),
            "city": _("A city is required"),
            "country": _("A country is required")
        }
        for field_name, field_value in extra_fields.items():
            if field_name not in self.fields:
                if field_name == "honor_code":
                    if field_value == "required":
                        self.fields[field_name] = _make_true_field(
                            _("To enroll, you must follow the honor code.")
                        )
                else:
                    required = field_value == "required"
                    min_length = 1 if field_name in ("gender", "level_of_education") else 2
                    error_message = error_message_dict.get(
                        field_name,
                        _("You are missing one or more required fields")
                    )
                    self.fields[field_name] = NullableCharField(
                        required=required,
                        min_length=min_length,
                        error_messages={
                            "required": error_message,
                            "min_length": error_message,
                        }
                    )

        for field in self.extended_profile_fields:
            if field not in self.fields:
                self.fields[field] = NullableCharField(required=False)

    def clean_password(self):
        password = self.cleaned_data["password"]
        if "username" in self.cleaned_data and self.cleaned_data["username"] == password:
            raise ValidationError(_("Username and password fields cannot match"))
        if self.enforce_password_policy:
            try:
                validate_password_length(password)
                validate_password_complexity(password)
                validate_password_dictionary(password)
            except ValidationError, e:
                raise ValidationError(_("Password: ") + e.message)
        return password

    # We actually want year_of_birth to be an integer, but we ignore it instead of raising an error
    # if it is malformed
    def clean_year_of_birth(self):
        try:
            year_str = self.cleaned_data["year_of_birth"]
            return int(year_str) if year_str is not None else None
        except ValueError:
            return None

    @property
    def cleaned_extended_profile(self):
        return {
            key: value
            for key, value in self.cleaned_data.items()
            if key in self.extended_profile_fields and value is not None
        }
