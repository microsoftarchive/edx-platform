"""
Models for contentstore
"""
# pylint: disable=no-member

from django.db.models.fields import TextField, PositiveIntegerField

from config_models.models import ConfigurationModel


class VideoUploadConfig(ConfigurationModel):
    """Configuration for the video upload feature."""
    profile_whitelist = TextField(
        blank=True,
        help_text="A comma-separated list of names of profiles to include in video encoding downloads."
    )

    @classmethod
    def get_profile_whitelist(cls):
        """Get the list of profiles to include in the encoding download"""
        return [profile for profile in cls.current().profile_whitelist.split(",") if profile]


class MobileNotificationsConfig(ConfigurationModel):
    """Configuration for mobile push notifications."""
    number_of_retry_attempts = PositiveIntegerField(
        blank=True,
        default=0,
        help_text="The number of attempts at sending a push notification, in the event of failure."
    )
