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

   ref: https://github.com/swagger-api/swagger-codegen
"""

from __future__ import absolute_import

import json
import mimetypes
import os
import re
import sys
import tempfile
import threading
from datetime import date
from datetime import datetime

import attune.client.commands as commands
from attune.client.model import Customer
from .rest import ApiException
from .rest import RESTClientObject

# noinspection PyUnresolvedReferences
from attune.client import model

# python 2 and python 3 compatibility library
from six import iteritems

try:
    # for python3
    from urllib.parse import quote
except ImportError:
    # for python2
    from urllib import quote

from .configuration import Configuration


class BaseClient(object):
    def __init__(self, config=None):
        self.config = config or Configuration()

        self.host = self.config.host

        self.rest_client = RESTClientObject(self.config)

        self.default_headers = {}

        self.user_agent = 'attune-python/1.0.0'

    @property
    def user_agent(self):
        return self.default_headers['User-Agent']

    @user_agent.setter
    def user_agent(self, value):
        self.default_headers['User-Agent'] = value

    def set_default_header(self, header_name, header_value):
        self.default_headers[header_name] = header_value

    def __call_api(self, resource_path, method,
                   path_params=None, query_params=None, header_params=None,
                   body=None, post_params=None, files=None,
                   response_type=None, auth_settings=None, oauth_token=None, callback=None):

        # headers parameters
        header_params = header_params or {}
        header_params.update(self.default_headers)
        if header_params:
            header_params = self.sanitize_for_serialization(header_params)

        # path parameters
        if path_params:
            path_params = self.sanitize_for_serialization(path_params)
            for k, v in iteritems(path_params):
                replacement = quote(str(self.to_path_value(v)))
                resource_path = resource_path. \
                    replace('{' + k + '}', replacement)

        # query parameters
        if query_params:
            query_params = self.sanitize_for_serialization(query_params)
            # Todo: we do this in requests library
            # query_params = {k: self.to_path_value(v)
            #                 for k, v in iteritems(query_params)}

        # post parameters
        if post_params or files:
            post_params = self.prepare_post_parameters(post_params, files)
            post_params = self.sanitize_for_serialization(post_params)

        # auth setting
        self.update_params_for_auth(oauth_token, header_params, query_params, auth_settings)

        # body
        if body:
            body = self.sanitize_for_serialization(body)

        # request url
        url = self.host + resource_path

        # perform request and return response
        response_data = self.request(method, url,
                                     query_params=query_params,
                                     headers=header_params,
                                     post_params=post_params, body=body)

        self.last_response = response_data

        # deserialize response data
        if response_type:
            deserialized_data = self.deserialize(response_data, response_type)
        else:
            deserialized_data = None

        if callback:
            callback(deserialized_data)
        else:
            return deserialized_data

    def to_path_value(self, obj):
        """
        Takes value and turn it into a string suitable for inclusion in
        the path, by url-encoding.

        :param obj: object or string value.

        :return string: quoted value.
        """
        if type(obj) == list:
            return ','.join(obj)
        else:
            return str(obj)

    def sanitize_for_serialization(self, obj):
        """
        Builds a JSON POST object.

        If obj is None, return None.
        If obj is str, int, float, bool, return directly.
        If obj is datetime.datetime, datetime.date
            convert to string in iso8601 format.
        If obj is list, sanitize each element in the list.
        If obj is dict, return the dict.
        If obj is swagger model, return the properties dict.

        :param obj: The data to serialize.
        :return: The serialized form of data.
        """
        types = (str, int, float, bool, tuple)
        if sys.version_info < (3, 0):
            types = types + (unicode,)
        if isinstance(obj, type(None)):
            return None
        elif isinstance(obj, types):
            return obj
        elif isinstance(obj, list):
            return [self.sanitize_for_serialization(sub_obj)
                    for sub_obj in obj]
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        else:
            if isinstance(obj, dict):
                obj_dict = obj
            else:
                # Convert model obj to dict except
                # attributes `swagger_types`, `attribute_map`
                # and attributes which value is not None.
                # Convert attribute name to json key in
                # model definition for request.
                obj_dict = {obj.attribute_map[attr]: getattr(obj, attr)
                            for attr, _ in iteritems(obj.swagger_types)
                            if getattr(obj, attr) is not None}

            return {key: self.sanitize_for_serialization(val)
                    for key, val in iteritems(obj_dict)}

    def deserialize(self, response, response_type):
        """
        Deserializes response into an object.

        :param response: RESTResponse object to be deserialized.
        :param response_type: class literal for
            deserialzied object, or string of class name.

        :return: deserialized object.
        """
        # handle file downloading
        # save response body into a tmp file and return the instance
        if "file" == response_type:
            return self.__deserialize_file(response)

        # fetch data from response object
        try:
            data = json.loads(response.data)
        except ValueError:
            data = response.data

        return self.__manual_deserialize(data, response_type)

    def __manual_deserialize(self, data, klass):
        if "RankedEntities" == klass:
           r = model.RankedEntities()
           r.cell = data.get('cell', None);
           r.ranking = data.get('ranking', None);
           r.status = data.get('status', None);
           r.message = data.get('message', None);
        else:
           r = __deserialize(data, klass)
        return r

    def __deserialize(self, data, klass):
        """
        Deserializes dict, list, str into an object.

        :param data: dict, list or str.
        :param klass: class literal, or string of class name.

        :return: object.
        """
        if data is None:
            return None

        if type(klass) == str:
            if klass.startswith('list['):
                sub_kls = re.match('list\[(.*)\]', klass).group(1)
                return [self.__deserialize(sub_data, sub_kls)
                        for sub_data in data]

            if klass.startswith('dict('):
                sub_kls = re.match('dict\(([^,]*), (.*)\)', klass).group(2)
                return {k: self.__deserialize(v, sub_kls)
                        for k, v in iteritems(data)}

            # convert str to class
            # for native types
            if klass in ['int', 'float', 'str', 'bool',
                         "date", 'datetime', "object"]:
                klass = eval(klass)
            # for model types
            else:
                klass = eval('model.' + klass)

        if klass in [int, float, str, bool]:
            return self.__deserialize_primitive(data, klass)
        elif klass == object:
            return self.__deserialize_object(data)
        elif klass == date:
            return self.__deserialize_date(data)
        elif klass == datetime:
            return self.__deserialize_datatime(data)
        else:
            return self.__deserialize_model(data, klass)

    def call_api(self, resource_path, method,
                 path_params=None, query_params=None, header_params=None,
                 body=None, post_params=None, files=None,
                 response_type=None, auth_settings=None, oauth_token=None, callback=None):
        """
        Makes the HTTP request (synchronous) and return the deserialized data.
        To make an async request, define a function for callback.

        :param resource_path: Path to method endpoint.
        :param method: Method to call.
        :param path_params: Path parameters in the url.
        :param query_params: Query parameters in the url.
        :param header_params: Header parameters to be
            placed in the request header.
        :param body: Request body.
        :param post_params dict: Request post form parameters,
            for `application/x-www-form-urlencoded`, `multipart/form-data`.
        :param auth_settings list: Auth Settings names for the request.
        :param response: Response data type.
        :param files dict: key -> filename, value -> filepath,
            for `multipart/form-data`.
        :param callback function: Callback function for asynchronous request.
            If provide this parameter,
            the request will be called asynchronously.
        :return:
            If provide parameter callback,
            the request will be called asynchronously.
            The method will return the request thread.
            If parameter callback is None,
            then the method will return the response directly.
        """
        if callback is None:
            return self.__call_api(resource_path, method,
                                   path_params, query_params, header_params,
                                   body, post_params, files,
                                   response_type, auth_settings, oauth_token, callback)
        else:
            thread = threading.Thread(target=self.__call_api,
                                      args=(resource_path, method,
                                            path_params, query_params,
                                            header_params, body,
                                            post_params, files,
                                            response_type, auth_settings,
                                            oauth_token, callback))
        thread.start()
        return thread

    def request(self, method, url, query_params=None, headers=None,
                post_params=None, body=None):
        """
        Makes the HTTP request using RESTClient.
        """
        if method == "GET":
            return self.rest_client.GET(url,
                                        query_params=query_params,
                                        headers=headers)
        elif method == "HEAD":
            return self.rest_client.HEAD(url,
                                         query_params=query_params,
                                         headers=headers)
        elif method == "OPTIONS":
            return self.rest_client.OPTIONS(url,
                                            query_params=query_params,
                                            headers=headers,
                                            post_params=post_params,
                                            body=body)
        elif method == "POST":
            return self.rest_client.POST(url,
                                         query_params=query_params,
                                         headers=headers,
                                         post_params=post_params,
                                         body=body)
        elif method == "PUT":
            return self.rest_client.PUT(url,
                                        query_params=query_params,
                                        headers=headers,
                                        post_params=post_params,
                                        body=body)
        elif method == "PATCH":
            return self.rest_client.PATCH(url,
                                          query_params=query_params,
                                          headers=headers,
                                          post_params=post_params,
                                          body=body)
        elif method == "DELETE":
            return self.rest_client.DELETE(url,
                                           query_params=query_params,
                                           headers=headers)
        else:
            raise ValueError(
                    "http method must be `GET`, `HEAD`,"
                    " `POST`, `PATCH`, `PUT` or `DELETE`."
            )

    def prepare_post_parameters(self, post_params=None, files=None):
        """
        Builds form parameters.

        :param post_params: Normal form parameters.
        :param files: File parameters.
        :return: Form parameters with files.
        """
        params = {}

        if post_params:
            params.update(post_params)

        if files:
            for k, v in iteritems(files):
                if not v:
                    continue

                with open(v, 'rb') as f:
                    filename = os.path.basename(f.name)
                    filedata = f.read()
                    mimetype = mimetypes. \
                                   guess_type(filename)[0] or 'application/octet-stream'
                    params[k] = tuple([filename, filedata, mimetype])

        return params

    def select_header_accept(self, accepts):
        """
        Returns `Accept` based on an array of accepts provided.

        :param accepts: List of headers.
        :return: Accept (e.g. application/json).
        """
        if not accepts:
            return

        accepts = list(map(lambda x: x.lower(), accepts))

        if 'application/json' in accepts:
            return 'application/json'
        else:
            return ', '.join(accepts)

    def select_header_content_type(self, content_types):
        """
        Returns `Content-Type` based on an array of content_types provided.

        :param content_types: List of content-types.
        :return: Content-Type (e.g. application/json).
        """
        if not content_types:
            return 'application/json'

        content_types = list(map(lambda x: x.lower(), content_types))

        if 'application/json' in content_types:
            return 'application/json'
        else:
            return content_types[0]

    def update_params_for_auth(self, oauth_token, headers, querys, auth_settings):
        """
        Updates header and query params based on authentication setting.

        :param headers: Header parameters dict to be updated.
        :param querys: Query parameters dict to be updated.
        :param auth_settings: Authentication setting identifiers list.
        """

        token = oauth_token or self.config.access_token
        if token:
            headers['Authorization'] = 'Bearer %s' % token

    def __deserialize_file(self, response):
        """
        Saves response body into a file in a temporary folder,
        using the filename from the `Content-Disposition` header if provided.

        :param response:  RESTResponse.
        :return: file path.
        """
        config = self.config

        fd, path = tempfile.mkstemp(dir=config.temp_folder_path)
        os.close(fd)
        os.remove(path)

        content_disposition = response.getheader("Content-Disposition")
        if content_disposition:
            filename = re. \
                search(r'filename=[\'"]?([^\'"\s]+)[\'"]?', content_disposition). \
                group(1)
            path = os.path.join(os.path.dirname(path), filename)

        with open(path, "w") as f:
            f.write(response.data)

        return path

    def __deserialize_primitive(self, data, klass):
        """
        Deserializes string to primitive type.

        :param data: str.
        :param klass: class literal.

        :return: int, float, str, bool.
        """
        try:
            value = klass(data)
        except UnicodeEncodeError:
            value = unicode(data)
        except TypeError:
            value = data
        return value

    def __deserialize_object(self, value):
        """
        Return a original value.

        :return: object.
        """
        return value

    def __deserialize_date(self, string):
        """
        Deserializes string to date.

        :param string: str.
        :return: date.
        """
        try:
            from dateutil.parser import parse
            return parse(string).date()
        except ImportError:
            return string
        except ValueError:
            raise ApiException(
                    status=0,
                    reason="Failed to parse `{0}` into a date object"
                        .format(string)
            )

    def __deserialize_datatime(self, string):
        """
        Deserializes string to datetime.

        The string should be in iso8601 datetime format.

        :param string: str.
        :return: datetime.
        """
        try:
            from dateutil.parser import parse
            return parse(string)
        except ImportError:
            return string
        except ValueError:
            raise ApiException(
                    status=0,
                    reason="Failed to parse `{0}` into a datetime object".
                        format(string)
            )

    def __deserialize_model(self, data, klass):
        """
        Deserializes list or dict to model.

        :param data: dict, list.
        :param klass: class literal.
        :return: model object.
        """
        instance = klass()

        for attr, attr_type in iteritems(instance.swagger_types):
            if data is not None \
                    and instance.attribute_map[attr] in data \
                    and isinstance(data, (list, dict)):
                value = data[instance.attribute_map[attr]]
                setattr(instance, attr, self.__deserialize(value, attr_type))

        return instance


class Client(BaseClient):
    def __init__(self, config=None):
        super(Client, self).__init__(config)

        from attune.client.api import Entities

        self.api = Entities(self)

    def update_fallback_to_default(self, boolean):
        self.config.commands_fallback = bool(boolean)

    def run(self, command, callback=None):
        return command.execute(callback=callback)

    def get_auth_token(self, client_id, client_secret, callback=None):
        return self.run(commands.GetAuthToken(self, args=(client_id, client_secret)), callback)

    def create_anonymous(self, oauth_token=None, callback=None):
        return self.run(commands.CreateAnonymous(self, oauth_token=oauth_token), callback)

    def bind(self, anonymous_id, customer_id, oauth_token=None, callback=None):
        customer = Customer()
        customer.customer = customer_id

        return self.run(commands.Bind(self, args=(anonymous_id, customer), oauth_token=oauth_token), callback)

    def get_bound_customer(self, anonymous_id, oauth_token=None, callback=None):
        return self.run(commands.BoundCustomer(self, args=(anonymous_id,), oauth_token=oauth_token), callback)

    def get_rankings(self, ranking_params, oauth_token=None, callback=None, offset=None, count=None):
        ranking_params.entity_source = ranking_params.entity_source or 'ids'

        if ranking_params.entity_source.upper() == 'IDS':
            command = commands.GetRankingsPOST(self, args=(ranking_params,), offset=offset, count=count, oauth_token=oauth_token)
        else:
            command = commands.GetRankingsGET(self, args=(ranking_params,), oauth_token=oauth_token)

        return self.run(command, callback)
