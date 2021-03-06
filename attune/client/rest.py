# coding: utf-8

"""
Copyright 2015 SmartBear Software

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

Credit: this file (rest.py) is modified based on rest.py in Dropbox Python SDK:
https://www.dropbox.com/developers/core/sdks/python
"""
from __future__ import absolute_import

import io
import logging
import sys
try:
    import ujson as json
except ImportError:
    import json

# python 2 and python 3 compatibility library
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry
from requests.packages.urllib3.exceptions import SSLError

try:
    # for python3
    from urllib.parse import urlencode
except ImportError:
    # for python2
    from urllib import urlencode

logger = logging.getLogger(__name__)


class RESTResponse(io.IOBase):
    def __init__(self, resp):
        super(RESTResponse, self).__init__()

        self.urllib3_response = resp
        self.status = resp.status_code
        self.reason = resp.reason
        self.data = resp.content

    def getheaders(self):
        """
        Returns a dictionary of the response headers.
        """
        return self.urllib3_response.headers

    def getheader(self, name, default=None):
        """
        Returns a given response header.
        """
        return self.urllib3_response.headers.get(name, default)


class RESTClientObject(object):
    def __init__(self, config):
        self.config = config

        self.pool_manager = requests.Session()

        self.retry_methods = frozenset(['GET', 'HEAD', 'DELETE', 'OPTIONS'])

        # noinspection PyTypeChecker
        adapter = HTTPAdapter(
                pool_connections=config.http_pool_connections,
                pool_maxsize=config.http_pool_size,
                max_retries=Retry(
                        method_whitelist=self.retry_methods,
                        total=config.http_max_retries,
                        connect=config.http_max_retries,
                        read=config.http_max_retries,
                        status_forcelist=range(500, 600)
                ),
                pool_block=True
        )
        self.pool_manager.mount('https://', adapter)
        self.pool_manager.mount('http://', adapter)

        self.pool_manager.verify = bool(self.config.verify_ssl)

    @property
    def timeouts(self):
        return (float(self.config.http_timeout_connect), float(self.config.http_timeout_read))

    def request(self, method, url, query_params=None, headers=None,
                body=None, post_params=None):
        """
        :param method: http request method
        :param url: http request url
        :param query_params: query parameters in the url
        :param headers: http request headers
        :param body: request json body, for `application/json`
        :param post_params: request post parameters,
                            `application/x-www-form-urlencode`
                            and `multipart/form-data`
        """
        method = method.upper()
        assert method in ['GET', 'HEAD', 'DELETE', 'POST', 'PUT', 'PATCH', 'OPTIONS']

        if post_params and body:
            raise ValueError(
                    "body parameter cannot be used with post_params parameter."
            )

        post_params = post_params or {}
        headers = headers or {}

        # if 'Content-Type' not in headers:
        #     headers['Content-Type'] = 'application/json'

        try:
            # For `POST`, `PUT`, `PATCH`, `OPTIONS`
            if method in ['POST', 'PUT', 'PATCH', 'OPTIONS']:
                if query_params:
                    url += '?' + urlencode(query_params)
                if headers['Content-Type'] == 'application/json':
                    r = self.pool_manager.request(method, url,
                                                  data=json.dumps(body),
                                                  headers=headers,
                                                  timeout=self.timeouts)
                if headers['Content-Type'] == 'application/x-www-form-urlencoded':
                    r = self.pool_manager.request(method, url,
                                                  data=post_params,
                                                  headers=headers,
                                                  timeout=self.timeouts)
                if headers['Content-Type'] == 'multipart/form-data':
                    # must del headers['Content-Type'], or the correct Content-Type
                    # which generated by urllib3 will be overwritten.
                    del headers['Content-Type']
                    r = self.pool_manager.request(method, url,
                                                  data=post_params,
                                                  headers=headers,
                                                  timeout=self.timeouts)
            # For `GET`, `HEAD`, `DELETE`
            else:
                r = self.pool_manager.request(method, url,
                                              params=query_params,
                                              headers=headers,
                                              timeout=self.timeouts)
        except SSLError as e:
            msg = "{0}\n{1}".format(type(e).__name__, str(e))
            raise ApiException(status=0, reason=msg)

        r = RESTResponse(r)

        # In the python 3, the response.data is bytes.
        # we need to decode it to string.
        if sys.version_info > (3,):
            r.data = r.data.decode('utf8')

        # log response body
        logger.debug("response body: %s" % r.data)

        if r.status not in range(200, 206):
            raise ApiException(http_resp=r)

        return r

    def GET(self, url, headers=None, query_params=None):
        return self.request("GET", url,
                            headers=headers,
                            query_params=query_params)

    def HEAD(self, url, headers=None, query_params=None):
        return self.request("HEAD", url,
                            headers=headers,
                            query_params=query_params)

    def OPTIONS(self, url, headers=None, query_params=None, post_params=None, body=None):
        return self.request("OPTIONS", url,
                            headers=headers,
                            query_params=query_params,
                            post_params=post_params,
                            body=body)

    def DELETE(self, url, headers=None, query_params=None):
        return self.request("DELETE", url,
                            headers=headers,
                            query_params=query_params)

    def POST(self, url, headers=None, query_params=None, post_params=None, body=None):
        return self.request("POST", url,
                            headers=headers,
                            query_params=query_params,
                            post_params=post_params,
                            body=body)

    def PUT(self, url, headers=None, query_params=None, post_params=None, body=None):
        return self.request("PUT", url,
                            headers=headers,
                            query_params=query_params,
                            post_params=post_params,
                            body=body)

    def PATCH(self, url, headers=None, query_params=None, post_params=None, body=None):
        return self.request("PATCH", url,
                            headers=headers,
                            query_params=query_params,
                            post_params=post_params,
                            body=body)


class ApiException(Exception):
    def __init__(self, status=None, reason=None, http_resp=None):
        if http_resp:
            self.status = http_resp.status
            self.reason = http_resp.reason
            self.body = http_resp.data
            self.headers = http_resp.getheaders()
        else:
            self.status = status
            self.reason = reason
            self.body = None
            self.headers = None

    def __str__(self):
        """
        Custom error messages for exception
        """
        error_message = "({0})\n" \
                        "Reason: {1}\n".format(self.status, self.reason)
        if self.headers:
            error_message += "HTTP response headers: {0}\n".format(self.headers)

        if self.body:
            error_message += "HTTP response body: {0}\n".format(self.body)

        return error_message
