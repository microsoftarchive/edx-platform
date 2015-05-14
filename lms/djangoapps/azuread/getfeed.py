# -*- coding: utf-8 -*-#
#
from django.conf import settings

	
#
# Get complete authHeader array to construct CurlHeader 
#		
def getCurlAuthHeader():
	from  azuread import authAAD
	auth = auth = authAAD.AuthorizationHelperForAADGraphService()
	authHeader = auth.getAuthenticationHeader()
	if authHeader!='':
		listHeader = [ ''+authHeader+'',  'Accept:application/json;odata=minimalmetadata', 'Content-Type:application/json;odata=minimalmetadata', 'Prefer:return-content' ]
	else:
		listHeader = ''
		
	return listHeader


def getFeed(feedName):
	
	if feedName =='':
		feedName = 'users'
		
	#configure curlUrl	

	stsUrl = "https://graph.windows.net/%s/%s?api-version=%s" % ( settings.SOCIAL_AUTH_AZURE_DOMAIN , feedName,  "1.0" )
	# print stsUrl
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
		print "Azure feed output:"
		print output
		return output
		
	else:
		return 'None'
		

""" testing """
# print getFeed('users');