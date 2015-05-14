from social.backends.oauth import BaseOAuth2
# from azuread.oauth import BaseOAuth2
from urllib import urlencode
import json
from django.conf import settings


class AzureAdOAut2(BaseOAuth2):
    """AzureAD OAuth authentication backend"""
    name = 'azuread'

    AUTHORIZATION_URL = 'https://login.microsoftonline.com/common/oauth2/authorize' 
    ACCESS_TOKEN_URL  ='https://login.microsoftonline.com/common/oauth2/token'
    SCOPE_SEPARATOR = ','
    STATE_PARAMETER = "state"
    EXTRA_DATA = [
        ('id', 'id'),
        ('expires', 'expires')
    ]

    RETURNED_USER_DATA = None

    def get_key_and_secret(self):
    	return 	 (settings.SOCIAL_AUTH_AZURE_CLIENT_ID, settings.SOCIAL_AUTH_AZURE_PASSWORD)

    def auth_complete_params(self, state=None):
        client_id, client_secret = self.get_key_and_secret()
        return {
            'code': self.data.get('code', ''),
            'client_secret': client_secret,
            'client_id':client_id,
            'authorization_response': self.get_redirect_uri(state),
            'grant_type': 'authorization_code',
            'api-version':'1.0',
            'redirect_uri': self.get_redirect_uri(),
            'resource': 'https://graph.windows.net'
        }

    def get_user_id(self, details, response):
        """Return a unique ID for the current user, by default from server
        response."""
        return self.RETURNED_USER_DATA["unique_name"]




    def auth_params(self, state=None):

        client_id, client_secret = self.get_key_and_secret()
        params = {
            'client_id': settings.SOCIAL_AUTH_AZURE_CLIENT_ID,
            'redirect_uri': self.get_redirect_uri(state)
        }
        if self.STATE_PARAMETER and state:
            params['state'] = state
        if self.RESPONSE_TYPE:
            params['response_type'] = self.RESPONSE_TYPE

        import random
        import string
        allowed_chars = ''.join((string.lowercase, string.uppercase, string.digits))
        unique_id = ''.join(random.choice(allowed_chars) for _ in range(32))
        params["response_mode"] = "query"
        params["nonce"] = unique_id
        params["api-version"] = "1.0"
        params["grant_type"] = 'authorization_code'
        return params

    def get_user_details(self, response):
        """Return user details from Github account"""
        # print self.RETURNED_USER_DATA

        if self.RETURNED_USER_DATA.has_key("email"):
        	email = self.RETURNED_USER_DATA["email"]
        else:
        	email = self.RETURNED_USER_DATA["unique_name"]

        # username = email.split("@")[0]

        data =  {'username': email,
                'email': email,
                'first_name': self.RETURNED_USER_DATA["name"]}
        # print data
        return data

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        import jwt
        jwt_data = kwargs["response"]["id_token"]
        self.RETURNED_USER_DATA = jwt.decode(jwt_data,verify=False)
 		
    def get_username(self):
        return self.RETURNED_USER_DATA["unique_name"]
