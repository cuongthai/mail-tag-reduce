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
import wsgiref.handlers
import cgi, os, md5, logging
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import settings
from contextIO2 import ContextIO

class MainHandler(webapp.RequestHandler):
    def get(self):
        if users.get_current_user():

            # Get the email address of the user and see if that mailbox is available
            # in our Context.IO account by using the /imap/accountinfo.json API call
            current_user = users.get_current_user()
            current_email = current_user.email()
            
            # Figure out if there's an account corresponding to the current users's email address.
            # Normally, your app would maintain the Context.IO account id corresponding to each user
            # account but for the sake of keeping this example simple, we're checking every time and
            # setting a cookie with the account id every time an authentified user logs in this demo.

            ctxIO = ContextIO(consumer_key=settings.CONTEXTIO_OAUTH_KEY, consumer_secret=settings.CONTEXTIO_OAUTH_SECRET)
            accntList = ctxIO.get_accounts(email=current_email)
            if len(accntList) >= 1:
                # The mailbox is available under our Context.IO account
                
                # The following is to avoid implementing a user property storage for this app
                # (see comment above)
                self.response.headers.add_header('Set-Cookie','ctxioid='+ accntList[0].id +'; path=/;')
                m = md5.new()
                m.update(accntList[0].id)
                m.update(current_email)
                self.response.headers.add_header('Set-Cookie','ctxiohash='+ m.hexdigest() +'; path=/;')
                
                # show the application main UI. This UI will get data from the mailbox
                # through XMLHttpRequest calls handled by handlers.py
                url = users.create_logout_url(self.request.uri)
                template_values = {
                    'url': url,
                    'url_linktext': 'sign out',
                }
                path = os.path.join(os.path.dirname(__file__), 'templates', 'app.html')
                self.response.out.write(template.render(path, template_values))
            else:
                # This mailbox isn't available under our Context.IO account, show
                # users the page prompting them to connect their Gmail account
                # through OAuth. See imapoauth.py for steps on obtaining Access
                # Token and adding the mailbox to our Context.IO account.
                template_values = {
                    'connect_link': '/imapoauth_step1'
                }
                path = os.path.join(os.path.dirname(__file__), 'templates', 'connect.html')
                self.response.out.write(template.render(path, template_values))
        else:
            self.response.out.write("Oops, forgot to login: required option for this script in app.yaml?")

def main():
    application = webapp.WSGIApplication([('/', MainHandler)], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
