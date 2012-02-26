#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app,login_required
from google.appengine.api import users
import gdata.gauth
import gdata.docs.client
import settings

gdocs=gdata.docs.client.DocsClient(source=settings.APPENGINE_APP_NAME)

class Fetcher(webapp.RequestHandler):

	@login_required
	def get(self):
		"""This handler is responsible for fetching an initial OAuth
		request token and redirecting the user to the approval page."""
		current_user = users.get_current_user()

		# We need to first get a unique token for the user to
		# promote.
		#
		# We provide the callback URL. This is where we want the
		# user to be sent after they have granted us
		# access. Sometimes, developers generate different URLs
		# based on the environment. You want to set this value to
		# "http://localhost:8080/imapoauth_step2" if you are running the
		# development server locally.
		#
		# We also provide the data scope(s). In general, we want
		# to limit the scope as much as possible. For this
		# example, we just ask for access to all feeds.	
		
		scopes = ['https://mail.google.com/']
		oauth_callback='http://%s/imapoauth_step2' % self.request.host
		consumer_key = settings.APPENGINE_CONSUMER_KEY
		consumer_secret = settings.APPENGINE_CONSUMER_SECRET
		request_token = gdocs.get_oauth_token(scopes,oauth_callback,consumer_key,consumer_secret)
		
		# Persist this token in the datastore.
		request_token_key = 'request_token_%s' % current_user.user_id()
		gdata.gauth.ae_save(request_token,request_token_key)
		
		# Generate and redirect to the authorization URL.
		auth_url = '%s' % request_token.generate_authorization_url()
		self.redirect(auth_url)
		
class RequestTokenCallback(webapp.RequestHandler):

	@login_required
	def get(self):
		"""When the user grants access, they are redirected back to this
		handler where their authorized request token is exchanged for a
		long-lived access token."""		
		
		current_user = users.get_current_user()
		
		# Remember the token that we stashed? Let's get it back from
		# datastore now and adds information to allow it to become an
		# access token.		
		request_token_key = 'request_token_%s'% current_user.user_id()
		request_token = gdata.gauth.ae_load(request_token_key)
		gdata.gauth.authorize_request_token(request_token,self.request.uri)
		
		# We can now upgrade our authorized token to a long-lived
		# access token by associating it with gdocs client, and
		# calling the get_access_token method.	
		gdocs.auth_token = gdocs.get_access_token(request_token)
		
		import logging
		logging.info('auth_token %s request_token %s'%(str(gdocs.auth_token),str(request_token)))
		
		self.redirect('/')
		
def main():
	application = webapp.WSGIApplication([('/imapoauth_step1',Fetcher),('imapoauth_step2',RequestTokenCallback)],debug=True)
	
	run_wsgi_app(application)
	
if __name__ == '__main__':
	main()
