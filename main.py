from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
import os
from google.appengine.ext.webapp import template

class MainPage(webapp.RequestHandler):
    def get(self):
	if users.get_current_user():
		# This mailbox isn't available under our Context.IO account, show
		# users the page prompting them to connect their Gmail account
		# through OAuth. See imapoauth.py for steps on obtaining Access
		# Token and adding the mailbox to our Context.IO account.   
		template_values = {
			'connect_link' : 'imapoauth_step1'
		}     	
		path = os.path.join(os.path.dirname(__file__),'templates','connect.html')
		self.response.out.write(template.render(path,template_values))
	else:
        	self.response.out.write('Oops, forgot to login: required option for this script in app.yaml?')	

application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
