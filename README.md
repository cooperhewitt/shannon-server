shannon-server
===

shannon-server is a small WSGI-compliant httpony to calculate the [Shannon Entropy](http://en.wikipedia.org/wiki/Entropy_%28information_theory%29) for a given image.

**This package is officially DEPRECATED. You should take a look at [plumbing-shannon-server](https://github.com/cooperhewitt/plumbing-shannon-server) instead.**

You can run this locally with either Gunicorn
--

	$ gunicorn shannon:application
	$ curl 'http://localhost:8000/json/?path=http://mysite.com/cat.jpg' | python -m json.tool
		
	{
	    "shannon-entropy": 7.98169630470466, 
	    "stat": "ok"
	}
	
On Heroku
--

You can run this locally with foreman to test before pushing to [Heroku](http://heroku.com)

	$ virtualenv venv --distribute
	$ source venv/bin/activate
	$ pip install -r requirements.txt
	$ foreman start
	
Once tested, use the Heroku gem to create a new app

	$ heroku create
	$ git push heroku master
	$ curl 'http://your-heroku-app.herokuapp.com/?path=http://mysite.com/cat.jpg | python -m json.tool
	
This should result in the same output as above.

Using with POST
--

You can also send image data directly with a POST either via the web form or via curl as follows

	$ curl --form "imageupload=@YOUR_LOCAL_FILE.jpg" http://your-heroku-app.com

Dependencies
--

* [PIL](http://www.pythonware.com/products/pil/)
* [gunicorn](http://www.gunicorn.org/)
	
	


