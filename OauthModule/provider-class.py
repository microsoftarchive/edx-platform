class AzureADOauth2(BaseProvider):
    """Provider for Azure AD's Oauth2 auth system."""

    BACKEND_CLASS = azuread.AzureADOAuth2
    ICON_CLASS = 'fa-windows'
    NAME = 'AzureAD'
    SETTINGS = {
        'SOCIAL_AUTH_AZUREAD_OAUTH2_KEY': None,
        'SOCIAL_AUTH_AZUREAD_OAUTH2_SECRET': None,
        'SOCIAL_AUTH_AZUREAD_OAUTH2_SHAREPOINT_SITE': None
    }

    @classmethod
    def get_email(cls, provider_details):
        return provider_details.get('email')

    @classmethod
    def get_name(cls, provider_details):
        return provider_details.get('fullname')
