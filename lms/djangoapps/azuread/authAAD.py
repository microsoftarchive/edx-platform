# -*- coding: utf-8 -*-#
#
from django.conf import settings
import json
import pycurl
from StringIO import StringIO

#
# AuthorizationHelperForAADGraphService class
#  Class that provides authortization token for apps
#  that need to access Azure Active Directory Graph Service
class AuthorizationHelperForAADGraphService:
	
	def __init__(self):
		
		self.appTenantDomainName= settings.SOCIAL_AUTH_AZURE_DOMAIN
		self.appPrincipalId		= settings.SOCIAL_AUTH_AZURE_CLIENT_ID
		self.password			= settings.SOCIAL_AUTH_AZURE_PASSWORD
		self.apiVersion			= "1.0"


	def getCurlAuthHeader(self):
		from  azuread import authAAD
		auth = auth = authAAD.AuthorizationHelperForAADGraphService()
		authHeader = auth.getAuthenticationHeader()
		if authHeader!='':
			listHeader = [ ''+authHeader+'',  'Accept:application/json;odata=minimalmetadata', 'Content-Type:application/json;odata=minimalmetadata', 'Prefer:return-content' ]
		else:
			listHeader = ''
			
		return listHeader

	def get_roles(self):
		stsUrl = "https://graph.windows.net/%s/roles?api-version=%s" % ( self.appTenantDomainName, self.apiVersion )
		authHeader = self.getCurlAuthHeader()
		if authHeader !='':

			c = pycurl.Curl()
			c.setopt(c.URL, stsUrl)
			c.setopt(pycurl.HTTPHEADER, authHeader)
			c.setopt(pycurl.SSL_VERIFYPEER, 0)
			c.setopt(pycurl.SSL_VERIFYHOST, 0)

			buffer = StringIO()
			c.setopt(c.WRITEFUNCTION, buffer.write)
			c.perform()
			c.close()
			output = buffer.getvalue()
			return output
		else:
			return 'None'

	#send a PATCH request to azure to update an user's data
	def update_user(self, user_id, new_data):

		stsUrl = "https://graph.windows.net/%s/users/%s?api-version=%s" % ( self.appTenantDomainName , user_id, self.apiVersion )
		
		authHeader = self.getCurlAuthHeader()
		if authHeader !='':

			c = pycurl.Curl()
			c.setopt(c.URL, stsUrl)
			c.setopt(pycurl.HTTPHEADER, authHeader)
			c.setopt(pycurl.SSL_VERIFYPEER, 0)
			c.setopt(pycurl.SSL_VERIFYHOST, 0)

			user_data = new_data
			user_data = json.dumps(user_data)

			
			c.setopt(pycurl.POSTFIELDS,user_data)
			c.setopt(c.CUSTOMREQUEST, 'PATCH')
			buffer = StringIO()
			c.setopt(c.WRITEFUNCTION, buffer.write)
			c.perform()
			c.close()
			output = buffer.getvalue()

			return output
			
		else:
			return 'None'

	#send basic POST to azure to create a new user
	def create_user(self, data):

		stsUrl = "https://graph.windows.net/%s/users?api-version=%s" % ( self.appTenantDomainName , self.apiVersion )
		authHeader = self.getCurlAuthHeader()
		if authHeader !='':
		

			c = pycurl.Curl()
			c.setopt(c.URL, stsUrl)
			c.setopt(pycurl.HTTPHEADER, authHeader)
			c.setopt(pycurl.SSL_VERIFYPEER, 0)
			c.setopt(pycurl.SSL_VERIFYHOST, 0)

			user_data = {}
			user_data["accountEnabled"] = True
			user_data["displayName"] = data["fullname"]
			user_data["mailNickname"] = data["username"]
			user_data["passwordProfile"] = {"password":data["password"],"forceChangePasswordNextLogin":False}
			user_data["userPrincipalName"] = "%s@%s" % (data["username"], self.appTenantDomainName)
			user_data["givenName"] = data["givenName"]
			user_data["surname"] = data["surname"]

			user_data = json.dumps(user_data)


			c.setopt(pycurl.POSTFIELDS,user_data)
			
			buffer = StringIO()

			c.setopt(c.WRITEFUNCTION, buffer.write)
			c.perform()
			c.close()
			output = buffer.getvalue()
			return output
			
		else:
			return 'None'

	#retrieve user info from azure, using the user's object id.
	def get_user(self, user_id):
		stsUrl = "https://graph.windows.net/%s/users/%s?api-version=%s" % ( self.appTenantDomainName ,user_id, self.apiVersion )
		authHeader = self.getCurlAuthHeader()
		if authHeader !='':
		

			c = pycurl.Curl()
			c.setopt(c.URL, stsUrl)
			c.setopt(pycurl.HTTPHEADER, authHeader)
			c.setopt(pycurl.SSL_VERIFYPEER, 0)
			c.setopt(pycurl.SSL_VERIFYHOST, 0)
			
			buffer = StringIO()

			c.setopt(c.WRITEFUNCTION, buffer.write)
			c.perform()
			c.close()
			output = buffer.getvalue()
			return output
			
		else:
			return 'None'

	#create azure auth header to login via sso
	def getAuthenticationHeader(self ):
		import urllib
		# Password
		clientSecret = urllib.quote_plus(self.password)

		graphId = 'https://graph.windows.net'
		protectedResourceHostName = 'graph.windows.net'
		graphPrincipalId = urllib.quote_plus(graphId)
		clientPrincipalId = urllib.quote_plus(self.appPrincipalId)
		authenticationRequestBody = 'grant_type=client_credentials&client_secret=%s&resource=%s&client_id=%s' % (clientSecret, graphPrincipalId, clientPrincipalId )
		stsUrl = 'https://login.windows.net/%s/oauth2/token?api-version=1.5' % ( self.appTenantDomainName )

		
		c = pycurl.Curl()
		c.setopt(c.URL, stsUrl)
		c.setopt(pycurl.SSL_VERIFYPEER, 0)
		c.setopt(pycurl.SSL_VERIFYHOST, 0)
		c.setopt(c.POSTFIELDS, authenticationRequestBody)
		
		buffer = StringIO()

		c.setopt(c.WRITEFUNCTION, buffer.write)
		c.perform()
		c.close()
		output = buffer.getvalue()

		if 'access_token' in output:

			from azuread import CommonFunc
			jsonResponse	= json.loads(output.decode("ascii","ignore"))
			jsonData		= CommonFunc.convertUnicode2Utf8Dict(jsonResponse)
			access_token 	= jsonData['access_token']
			token_type 		= jsonData['token_type']
			headers_provider = 'Authorization: %s %s' % (token_type , access_token)
			return headers_provider
		else:
			return ''
		
		#return 'Authorization:' . $tokenOutput->{'token_type'}.' '.$tokenOutput->{'access_token'};