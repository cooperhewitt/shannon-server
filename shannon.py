import Image
import math
import cgi
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


def app(environ, start_response):
	data = ''	
	status = '200 OK'
	rsp = {}
	
	# determine the size of the request_body, and grab any params
	
	try:
		request_body_size = int(environ.get('CONTENT_LENGTH', 0))
		params = cgi.parse_qs(environ.get('QUERY_STRING', ''))
		path = params.get('path', None)
	except Exception, e:
		logging.error(e)
		request_body_size = 0
	
	# look for data as either a POST or path param
	
	if request_body_size!=0:
		form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
		fileitem = form['imageupload']	
		data = fileitem.file
	elif path:
		path = path[0]
		path = urllib.unquote(path)
		print path
		data = cStringIO.StringIO(urllib.urlopen(path).read())
		
		
		
	# open the image and calculate its shannon entropy
		
	try:
		im = Image.open(data)
		rsp['shannon-entropy'] = shannon_entropy(im)
		rsp['stat'] = 'ok'
	except Exception, e:
		logging.error(e)
		rsp = {'stat': 'error', 'error': "failed to process image: %s" % e}
			
	if rsp['stat'] != 'ok':
		status = "500 SERVER ERROR"
	else:		
		rsp = json.dumps(rsp)
		
		logging.debug(status)
	
		# return the result as json 
		
		start_response("200 OK", [
					("Content-Type", "text/javascript"),
					("Content-Length", str(len(rsp)))
					])
		
		return iter([rsp])
					
	# otherwise we just return the form
	
	start_response("200 OK", [
					("Content-Type", "text/html"),
					("Content-Length", str(len(html)))
					])
	
	return iter([html])



# basic form for uploading an image

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
