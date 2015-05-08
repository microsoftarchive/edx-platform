# -*- coding: utf-8 -*-#
#

	
#
# Get complete authHeader array to construct CurlHeader 
#		
def getCurlAuthHeader():
	from  azuread import authAAD
	auth = auth = authAAD.AuthorizationHelperForAADGraphService()
	authHeader = auth.getAuthenticationHeader(auth.appTenantDomainName, auth.appPrincipalId, auth.password+'', auth.apiVersion)
	if authHeader!='':
		listHeader = [ ''+authHeader+'',  'Accept:application/json;odata=minimalmetadata', 'Content-Type:application/json;odata=minimalmetadata', 'Prefer:return-content' ]
	else:
		listHeader = ''
		
	return listHeader


def getFeed(feedName):
	
	if feedName =='':
		feedName = 'users'
		
	#configure curlUrl	
	import settings
	settings = settings.Settings()
	stsUrl = "https://graph.windows.net/%s/%s?api-version=%s" % ( settings.appTenantDomainName , feedName,  settings.apiVersion )
	print stsUrl
	#get authHeader
	authHeader = getCurlAuthHeader()
	#return authHeader
	if authHeader !='':
	
		#initiaze curl which is used to make the http request.
		import pycurl
		from StringIO import StringIO
		c = pycurl.Curl()
		c.setopt(c.URL, stsUrl)
		#c.setopt(pycurl.HTTPHEADER, ['Accept: application/json','Authorization: Bearer %s' % str(token)])
		c.setopt(pycurl.HTTPHEADER, authHeader)
		# By default https does not work for CURL
		c.setopt(pycurl.SSL_VERIFYPEER, 0)
		c.setopt(pycurl.SSL_VERIFYHOST, 0)
		#c.setopt(c.POSTFIELDS, authenticationRequestBody)
		
		buffer = StringIO()
		#version pycurl >= 7.19.3
		#c.setopt(c.WRITEDATA, buffer)
		c.setopt(c.WRITEFUNCTION, buffer.write)
		c.perform()
		c.close()
		output = buffer.getvalue()
		
		return output
		
	else:
		return 'None'
		

""" testing """
print getFeed('users');
