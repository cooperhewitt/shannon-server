import Image
import math
import cgi
from cgi import escape
import re
import json
import cStringIO
import urllib
import logging

logging.basicConfig(level=logging.DEBUG)

def shannon_entropy(img):

	# calculate the shannon entropy for an image

	histogram = img.histogram()
	histogram_length = sum(histogram)

	samples_probability = [float(h) / histogram_length for h in histogram]

	return -sum([p * math.log(p, 2) for p in samples_probability if p != 0])

def index(environ, start_response):
	start_response('200 OK', [('Content-Type', 'text/html')])
	return ['''Shannon Entropy''']

def json_response(environ, start_response):

	status = '200 OK'
	rsp = {}

	params = cgi.parse_qs(environ.get('QUERY_STRING', ''))

	path = params.get('path', None)

	if not path:
		rsp = {'stat': 'error', 'error': 'missing image'}

	else:
		path = path[0]

		try:
			rsp['stat'] = 'ok'
			rsp['shannon'] = shannon_entropy(path)	
		except Exception, e:
			logging.error(e)
			rsp = {'stat': 'error', 'error': "failed to process image: %s" % e}

	if rsp['stat'] != 'ok':
		status = "500 SERVER ERROR"

	rsp = json.dumps(rsp)
		
	logging.debug("%s : %s" % (path, status))

	start_response(status, [
            ("Content-Type", "text/javascript"),
            ("Content-Length", str(len(rsp)))
            ])

	return iter([rsp])


	
def not_found(environ, start_response):
	start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
	return ['Not Found']
	

urls = [
	(r'^$', index),
	(r'json/?$', json_response)
]

def application(environ, start_response):
	path = environ.get('PATH_INFO', '').lstrip('/')
	for regex, callback in urls:
		match = re.search(regex, path)
		if match is not None:
			environ['myapp.url_args'] = match.groups()
			return callback(environ, start_response)
	return not_found(environ, start_response)
	
