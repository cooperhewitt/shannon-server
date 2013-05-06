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

html = """
<!DOCTYPE html>
<html>
	<head>
		<title>Shannon Entropy Server</title>
	</head>
	<body>
		<form id="mainform" enctype="multipart/form-data" action="/" method="post" name="mainform">
			<label for="imageupload">Image file:</label> <input name="imageupload" id="imageupload" type="file"><br>
			<input name="submit" id="submit" type="submit" value="submit">
		</form>
	</body>
</html>
"""

def shannon_entropy(img):

	# calculate the shannon entropy for an image

	histogram = img.histogram()
	histogram_length = sum(histogram)

	samples_probability = [float(h) / histogram_length for h in histogram]

	return -sum([p * math.log(p, 2) for p in samples_probability if p != 0])

def index(environ, start_response):
	data = ''	
	status = '200 OK'
	rsp = {}
		
	try:
		request_body_size = int(environ.get('CONTENT_LENGTH', 0))
		params = cgi.parse_qs(environ.get('QUERY_STRING', ''))
	except Exception, e:
		logging.error(e)
		request_body_size = 0
		
	if request_body_size!=0:
		form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
		fileitem = form['imageupload']	
		data = fileitem.file
		im = Image.open(data)
		rsp['shannon'] = shannon_entropy(im)
		shannon = "Shannon Entropy = " + str(rsp['shannon'])
		start_response("200 OK", [
						("Content-Type", "text/html"),
						("Content-Length", str(len(shannon)))
						])
		return iter([shannon])
	
	start_response("200 OK", [
					("Content-Type", "text/html"),
					("Content-Length", str(len(html)))
					])
	
	return iter([html])

def json_response(environ, start_response):
	data = ''
	status = '200 OK'
	rsp = {}

	params = cgi.parse_qs(environ.get('QUERY_STRING', ''))

	path = params.get('path', None)

	if not path:
		rsp = {'stat': 'error', 'error': 'missing image'}

	else:
		path = path[0]
		path = urllib.unquote(path)
		data = cStringIO.StringIO(urllib.urlopen(path).read())

		try:
			im = Image.open(data)
			rsp['shannon'] = shannon_entropy(im)
			rsp['stat'] = 'ok'	
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
	