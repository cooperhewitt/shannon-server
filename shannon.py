import Image
import math
import cgi
import json

def shannon_entropy(img):

	# calculate the shannon entropy for an image

	histogram = img.histogram()
	histogram_length = sum(histogram)

	samples_probability = [float(h) / histogram_length for h in histogram]

	return -sum([p * math.log(p, 2) for p in samples_probability if p != 0])


def app(environ, start_response):
		
	status = '200 OK'
	rsp = {}
	
	# determine the size of the request_body
	
	try:
		request_body_size = int(environ.get('CONTENT_LENGTH', 0))
	except (ValueError):
		request_body_size = 0
	
	# if request_body is larger than 0, we have data
	
	if request_body_size!=0:
		form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
		fileitem = form['imageupload']	
		
		# open the image and calculate its shanon entropy
		
		try:
			im = Image.open(fileitem.file)
			rsp['shannon-entropy'] = shannon_entropy(im)
			rsp['stat'] = 'ok'
		except Exception, e:
			rsp = {'stat': 'error', 'error': "failed to process image: %s" % e}
			
		if rsp['stat'] != 'ok':
			status = "500 SERVER ERROR"
			
		rsp = json.dumps(rsp)
		
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
<html>
<body>
<form id="mainform" enctype="multipart/form-data" action="/" method="post" >
<label for="imageupload">Image file:</label>
<input name="imageupload" id="imageupload" type="file" /><br />
<input name="submit" id="submit" type="submit" value="submit"> 
</form>
</body>
</html>
"""
