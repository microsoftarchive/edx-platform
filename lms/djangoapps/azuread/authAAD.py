# -*- coding: utf-8 -*-#
#


#
# AuthorizationHelperForAADGraphService class
#  Class that provides authortization token for apps
#  that need to access Azure Active Directory Graph Service
class AuthorizationHelperForAADGraphService:
	
	def __init__(self):
		import settings
		settings = settings.Settings()
		
		self.appTenantDomainName= settings.appTenantDomainName
		self.appPrincipalId		= settings.appPrincipalId
		self.password			= settings.password
		self.apiVersion			= settings.apiVersion
	
	
	#
	# Post the token generated from the symettric key and 
	# other information to STS URL and construct the authentication header
	#
	def getAuthenticationHeader(self, appTenantDomainName, appPrincipalId, password, apiVersion ):
		import urllib
		# Password
		clientSecret = urllib.quote_plus(password)
		# Information about the resource we need access for which in this case is graph
		graphId = 'https://graph.windows.net'
		protectedResourceHostName = 'graph.windows.net'
		graphPrincipalId = urllib.quote_plus(graphId)
		# Information about the app
		clientPrincipalId = urllib.quote_plus(appPrincipalId)
		# Construct the body for the STS request
		authenticationRequestBody = 'grant_type=client_credentials&client_secret=%s&resource=%s&client_id=%s' % (clientSecret, graphPrincipalId, clientPrincipalId )
		# Set url
		stsUrl = 'https://login.windows.net/%s/oauth2/token?api-version=1.5' % ( appTenantDomainName )

		#Using curl to post the information to STS and get back the authentication response
		import pycurl
		from StringIO import StringIO
		
		c = pycurl.Curl()
		c.setopt(c.URL, stsUrl)
		# By default https does not work for CURL
		c.setopt(pycurl.SSL_VERIFYPEER, 0)
		c.setopt(pycurl.SSL_VERIFYHOST, 0)
		c.setopt(c.POSTFIELDS, authenticationRequestBody)
		
		buffer = StringIO()
		#version pycurl >= 7.19.3
		#c.setopt(c.WRITEDATA, buffer)
		c.setopt(c.WRITEFUNCTION, buffer.write)
		c.perform()
		c.close()
		output = buffer.getvalue()
		
		# decode the response from sts using json decoder
		import json

		if 'access_token' in output:
			#remove non asccii 128 compat python2.x
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
