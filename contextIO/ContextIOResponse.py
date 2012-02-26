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
from django.utils import simplejson as json


class ContextIOResponse(object):
    def __init__(self,
                 response,
                 content):
        self.response = response

        if 'application/json' == response['content-type']:
            self.content = json.loads(content)
        else:
            self.content = content

    def get_status(self):
        return self.response['status']

    def get_content_type(self):
        return self.response['content-type']

    def get_messages(self):
        return self.response['messages']

    def get_response(self):
        return self.response

    def get_content(self):
        return self.content

    def get_data(self):
        return self.content.get('data', '')
