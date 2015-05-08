#
#
import sys

# ----------------
# COMMON FUNCTIONS
# ----------------

#
# Get data from 
#
def get_form_data_general(environ):
	import cgi, cgitb, urllib
	#define vars
	index 		= {}
	# get form values
	form = cgi.FieldStorage(fp=environ['wsgi.input'],environ=environ)
	#proceed
	i =0
	for k in form.keys():
		index[k] = form[k].value 

	#print index
	return index

#
# Convert dict to query-string
#
def convert_dict2querystring(dict):
	import urllib
	text = ''
	count = 0
	for i in dict:
		if count > 0:
			text+= "&"
		#text+= str(i) + "=" + urllib.quote( str(dict[i]) )
		text+= str(i) + "=" + str(dict[i])
		count += 1
	return text

#
# Convert query-string to dict
#
def convert_qerystring2dict(str):
	#r_dict = parser.parse(str)
	return str
#
# Get form field list
#
def get_form_fieldlists(flistvalues):
	#listvalues = form.getlist("evidence")
	flist = flistvalues
	for item in flist:
		print item

#
# convert unicode2utf8 dicts
#
def convertUnicode2Utf8Dict(data):
	import collections
	if isinstance(data, basestring):
		return str(data)
	elif isinstance(data, collections.Mapping):
		return dict(map(convertUnicode2Utf8Dict, data.iteritems()))
	elif isinstance(data, collections.Iterable):
		return type(data)(map(convertUnicode2Utf8Dict, data))
	else:
		return data


# -----------------
# OUTPUTS FUNCTIONS
# -----------------

#
# Get Template buffer
#
def get_file_template(filename):
    f = open(filename,"r")
    buffer = f.read()
    f.close()
    return buffer


#
# Output Common Error Result
#
def show_common_action_result_formatted(strres):
	result =''
	if strres != 'error':
		result =''
		result  ='<div class="alert alert-success col-lg-12">'
		result +='<div class="col-lg-2"><img src="/media/logo.png" class="img-responsive" style="width:100px; height:100px"></div>'
		result +='<div class="col-lg-10"><h1><i class="fa fa-check-square-o"></i> Action is been correctly processed</h1></div>'
		result +='</div>'
	else:
		result =''
		result  ='<div class="alert alert-danger col-lg-12">'
		result +='<div class="col-lg-2"><img src="/media/logo.png" class="img-responsive" style="width:100px; height:100px"></div>'
		result +='<div class="col-lg-10"><h1><i class="fa fa-exclamation-triangle"></i> Error: The action could not be performed</h1></div>'
		result +='</div>'
	return result


# -----------------
# DEBUGS FUNCTIONS
# -----------------


#
# debug list object data
#
def debug_list_object_data(obj):
	from pprint import pprint
	if obj:	
		for e in obj:
			print "---------------------------------------"
			attrs = vars(e)
			pprint (attrs)
			print "---------------------------------------"

#
# debug object data
#
def debug_object_data(obj):
	from pprint import pprint
	if obj:
		print "---------------------------------------"
		attrs = vars(obj)
		pprint(attrs)
		print "---------------------------------------"

#
# Debug function
#
def debug(s):
	print "D: %s" % (str(s))

#
# Warning function
#
def warning(s):
	print "W: %s" % (str(s))

#
# Error function
#
def error(s):
	print "E: %s" % (str(s))
	sys.exit(1)
