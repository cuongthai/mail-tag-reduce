# -*- coding: utf-8 -*-
"""
Copyright (C) 2011 DokDok Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import time
import oauth2 as oauth
import httplib2
import collections
from urllib import quote

from contextIO.ContextIOResponse import ContextIOResponse


class ContextIORequester(httplib2.Http):

    def __init__(self, api_key, api_secret, api_url='https://api.context.io',
                 api_version=1.1, api_format='json', account=None,
                 cache=None, timeout=None, proxy_info=None):

        self.api_url = api_url
        self.api_version = api_version
        self.api_format = api_format
        self.params = {
            'oauth_version': "1.0",
        }

        self.consumer = oauth.Consumer(key=api_key, secret=api_secret)
        self.params['oauth_consumer_key'] = self.consumer.key
        if account:
            self.account = account
        else:
            self.account = None
            
        super(ContextIORequester,self).__init__(cache,timeout,proxy_info)

    def build_url_with_format(self,
                               action,
                               context,
                               account):
        action_with_format = '%s.%s' % (action, self.api_format)
        return self.build_url(action_with_format,
                               context,
                               account)

    def build_base_url(self, action):
        url = '%s/%s/%s' % (self.api_url, self.api_version, action)
        return url

    def build_query_string(self, context, account=None):
        queryString = ''
        if account:
            context['account'] = account
        elif self.account:
            context['account'] = self.account

        for key in context:
            queryString += '%s=%s&' % (key, quote('%s' % context[key]))
        return queryString

    def build_url(self, action, context, account=None):
        url = self.build_base_url(action) + "?" + self.build_query_string(context, account)
        return url

    def get_response(self,
                      action,
                      context,
                      account):
        url = self.build_url_with_format(action, context, account)
        return self.get_response_for_url(url)

    def get_response_for_url(self, url):
        parameters = self.params
        parameters['oauth_nonce'] = oauth.generate_nonce()
        parameters['oauth_timestamp'] = '%s' % int(time.time())

        req = oauth.Request(method="GET", url=url, parameters=parameters)
        # Sign the request.
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, self.consumer, None)
        response, content = self.request(req.to_url(),
                                        method="GET",
                                        body='',
                                        headers={},
                                        redirections=httplib2.DEFAULT_MAX_REDIRECTS,
                                        connection_type=None)
        if response['status'] != '200':
            raise Exception("Invalid response %s" % response['status'])
        return ContextIOResponse(response, content)

    def post_response_for_url(self, url, context, account):
        parameters = self.params
        parameters['oauth_nonce'] = oauth.generate_nonce()
        parameters['oauth_timestamp'] = '%s' % int(time.time())
        if account:
            parameters['account'] = account
        elif self.account:
            parameters['account'] = self.account

        for key in context:
            if isinstance(context[key],collections.Iterable):
                parameters[key] = quote(context[key])
            else:
                parameters[key] = context[key]

        req = oauth.Request(method="POST", url=url, parameters=parameters)
        # Sign the request.
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, self.consumer, None)
        response, content = self.request(url,
                                        method="POST",
                                        body=req.to_postdata(),
                                        headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                        redirections=httplib2.DEFAULT_MAX_REDIRECTS,
                                        connection_type=None)
        if response['status'] != '200':
            raise Exception("Invalid response %s" % response['status'])
        return ContextIOResponse(response, content)


class ContextIO(object):
    """
       ContextIO's client implementation using oauth.

       Note: If you have only one account you can instantiate ContextIO with the account parameter.
             If you have more than one account, you need to specify it for each method call

    """
    def __init__(self,
                 api_key,
                 api_secret,
                 api_format='json',
                 api_url='https://api.context.io',
                 api_version=1.1,
                 account=None,
                 cache=None,
                 timeout=None,
                 proxy_info=None):

        self.requester = ContextIORequester(api_key=api_key,
                                            api_secret=api_secret,
                                            api_version=api_version,
                                            api_format=api_format,
                                            api_url=api_url,
                                            account=account,
                                            cache=cache,
                                            timeout=timeout,
                                            proxy_info=proxy_info)

    def addresses(self,account=None):
        return self._get_response(action='addresses',context={},account=account)


    def allfiles(self, since, limit=None, account=None):
        """
         see http://context.io/docs/1.1/allfiles
        """
        context = {'since': since}
        return self._get_response('allfiles',
                                  context,
                                  limit,
                                  account)

    def allmessages(self, since, limit=None, account=None):
        """
        see http://context.io/docs/1.1/allmessages
        """
        context= {'since': since}
        return self._get_response('allmessages',
                                  context,
                                  limit,
                                  account)

    def apikeyinfo(self):
        return self._get_response('apikeyinfo', {}, None, None)

    def contactfiles(self, email='', to_address='', from_address='',
                     cc_address='', bcc_address='', limit=None, account=None):
        """
        see http://context.io/docs/1.1/contactfiles
        """
        context={}
        if email:
            context['email'] = email
        if to_address:
            context['to'] = to_address
        if from_address:
            context['from'] = from_address
        if cc_address:
            context['cc'] = cc_address
        if bcc_address:
            context['bcc'] = bcc_address
        return self._get_response('contactfiles',
                                   context,
                                   limit,
                                   account)

    def contactmessages(self, email='', to_address='', from_address='',
                        cc_address='', bcc_address='', limit=None, account=None):
        """
        see http://context.io/docs/1.1/contactmessages
        """
        context = {}
        if email:
            context['email'] = email
        if to_address:
            context['to'] = to_address
        if from_address:
            context['from'] = from_address
        if cc_address:
            context['cc'] = cc_address
        if bcc_address:
            context['bcc'] = bcc_address
        return self._get_response('contactmessages',
                                  context,
                                  limit,
                                  account)

    def contactsearch(self, search='', account=None):
        """
        see http://context.io/docs/1.1/contactsearch
        """
        context = {'search': search}
        return self._get_response('contactsearch', context, account=account)

    def diffsummary(self, file_id1, file_id2, account):
        """
        see http://context.io/docs/1.1/diffsummmary
        """

        context = {
            'fileid1': file_id1,
            'fileid2': file_id2,
	    'generate' : '1'
        }
        return self._get_response('diffsummary',
                                  context,
                                  account=account)

    def downloadfile(self, file_id, account=None):
        """
        see http://context.io/docs/1.1/downloadfile
        """
        context = {
            'fileid': file_id
        }
        url = self.requester.build_url('downloadfile',
                              context,
                              account)
        return self._get_response_for_url(url)

    def filerevisions(self, file_id='', filename='', account=None):
        """
        see http://context.io/docs/1.1/filerevisions
        """
        context = {}
        if file_id:
            context['fileid'] = file_id
        if filename:
            context['filename'] = filename

        return self._get_response('filerevisions',
                                  context,
                                  account=account)

    def filesearch(self, filename, account=None):
        """
        see http://context.io/docs/1.1/filesearch
        """
        context = {
            'filename': filename
        }
        return  self._get_response('filesearch',
                                   context,
                                   account=account)

    def messageheaders(self, message_id='', date_sent='', from_address='', account=None):
        """
        see http://context.io/docs/1.1/messageheaders
        """
        context = {}
        if message_id:
            context['emailmessageid'] = message_id
        if date_sent:
            context['datesent'] = date_sent
        if from_address:
            context['from'] = from_address

        return self._get_response('messageheaders',
                                  context,
                                  account=account)

    def messageinfo(self, message_id='', date_sent='', from_address='', account=None):
        """
        see http://context.io/docs/1.1/messageinfo
        """
        context = {}
        if message_id:
            context['emailmessageid'] = message_id
        if date_sent:
            context['datesent'] = date_sent
        if from_address:
            context['from'] = from_address
        return self._get_response('messageinfo',
                                  context,
                                  account=account)

    def messagetext(self, message_id='', date_sent='', from_address='', type='all', account=None):
        """
        see http://context.io/docs/1.1/messagetext
        """
        context = {}
        if message_id:
            context['emailmessageid'] = message_id
        if date_sent:
            context['datesent'] = date_sent
        if from_address:
            context['from'] = from_address
        if type != 'all':
            context['type'] = type

        return self._get_response('messagetext',
                                  context,
                                  account=account)

    def relatedfiles(self, file_id='', filename='', account=None):
        """
        see http://context.io/docs/1.1/relatedfiles
        """
        context = {}
        if file_id:
            context['fileid'] = file_id
	if filename:
            context['filename'] = filename

        return self._get_response('relatedfiles',
                                  context,
                                  account=account)

    def search(self, subject, limit=None, account=None):
        """
        see http://context.io/docs/1.1/search
        """
        context = {
            'subject': subject
        }

        return self._get_response('search',
                                  context,
                                  limit,
                                  account)

    def threadinfo(self, gmail_thread_id='',email_id='', account=None):
        """
        see http://context.io/docs/1.1/threadinfo
        """
        context = {}

        if gmail_thread_id and email_id:
            raise Exception("You can't specify both parameter at the same time")

        if not (gmail_thread_id or email_id):
            raise Exception("You need to specify at least one parameter")

        if gmail_thread_id:
            context['gmailthreadid'] = gmail_thread_id

        if email_id:
            context['emailmessageid'] = email_id

        return self._get_response('threadinfo',
                                  context,
                                  account=account)

    def _get_response(self, action, context, limit=None, account=None):
        if limit:
            context['limit']= limit
        url = self.requester.build_url_with_format(action, context, account)
        return self.requester.get_response_for_url(url)

    def _get_response_for_url(self, url):
        return self.requester.get_response_for_url(url)


class IMAPAdmin(object):

    """
       Administrative IMAP functions
    """
    def __init__(self,
                 api_key,
                 api_secret,
                 api_version=1.1,
                 api_format='json',
                 api_url='https://api.context.io',
                 cache=None, timeout=None, proxy_info=None):
        self.requester = ContextIORequester(api_key=api_key,
                                        api_secret=api_secret,
                                        api_version=api_version,
                                        api_format=api_format,
                                        api_url=api_url,
                                        account=None,
                                        cache=cache, timeout=timeout, proxy_info=proxy_info)

    def _get_response(self, action, context,account=None):
        url = self.requester.build_url(action, context,account=account)
        return self.requester.get_response_for_url(url)

    def _post_response(self, action, context,account=None):
        url = self.requester.build_base_url(action)
        return self.requester.post_response_for_url(url,context,account)

    def account_info(self,email):
        return self._get_response('imap/accountinfo.json', {'email':email})

    def add_account(self, email, username, password='', firstname='', lastname='',
                    oauthtoken='', oauthconsumername='', oauthtokensecret='',
                    server='imap.gmail.com', usessl=True, port=993):
        """
        see http://context.io/docs/1.1/imap/addaccount
        """
        context = {
            'email': email,
            'username': username,
            'server': server,
            'usessl': '1' if usessl else '0',
            'port': '%s' % port
        }
        if password:
            context['password'] = password
        if oauthtoken:
            context['oauthtoken'] = oauthtoken
        if oauthconsumername:
            context['oauthconsumername'] = oauthconsumername
        if oauthtokensecret:
            context['oauthtokensecret'] = oauthtokensecret
        if firstname:
            context['firstname']= firstname
        if lastname:
            context['lastname']= lastname
        return self._get_response('imap/addaccount.json', context)

    def discover(self, email):
        """
        see http://context.io/docs/1.1/imap/discover
        """
        context = {
            'email': email
        }
        return self._get_response('imap/discover.json', context)

    def modify_account(self, credentials='', mailboxes=None, account=None):
        """
        see http://context.io/docs/1.1/imap/modifyaccount
        """
        context = {}
        if credentials:
            context['credentials'] = credentials
        if mailboxes:
            context['mailboxes'] = ','.join(mailboxes)

        return self._get_response('imap/modifyaccount.json',context=context,account=account)

    def remove_account(self, account):
        """
        see http://context.io/docs/1.1/imap/removeaccount
        """
        context = {'account':account}
        return self._get_response('imap/removeaccount.json', context)

    def delete_oauth_provider(self, key=''):
        context = {
            'key': key,
            'action': 'delete'
        }
        return self._post_response('imap/oauthproviders.json', context)

    def set_oauth_provider(self, type='', key='', secret=''):
        context = {
            'key': key,
            'secret': secret,
            'type': type
        }
        return self._post_response('imap/oauthproviders.json', context)

    def get_oauth_providers(self, key=''):
        context = { }
        if key:
            context['key'] = key
        return self._get_response('imap/oauthproviders.json', context)

    def reset_status(self, account):
        """
        see http://context.io/docs/1.1/imap/resetstatus
        """
        context = {'account':account}
        return self._get_response('imap/resetstatus.json', context)

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
