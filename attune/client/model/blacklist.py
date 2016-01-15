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

    Ref: https://github.com/swagger-api/swagger-codegen
"""

from pprint import pformat
from six import iteritems


class Blacklist(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """

    def __init__(self):
        """
        Blacklist - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'ids': 'list[str]',
            'updated_date': 'datetime',
            'created_date': 'datetime',
            'consumer': 'str',
            'entity_type': 'str',
            'start_date': 'datetime',
            'end_date': 'datetime',
            'scope': 'str',
            'disabled': 'bool',
            'id': 'str'
        }

        self.attribute_map = {
            'ids': 'ids',
            'updated_date': 'updatedDate',
            'created_date': 'createdDate',
            'consumer': 'consumer',
            'entity_type': 'entityType',
            'start_date': 'startDate',
            'end_date': 'endDate',
            'scope': 'scope',
            'disabled': 'disabled',
            'id': 'id'
        }

        self._ids = None
        self._updated_date = None
        self._created_date = None
        self._consumer = None
        self._entity_type = None
        self._start_date = None
        self._end_date = None
        self._scope = None
        self._disabled = None
        self._id = None

    @property
    def ids(self):
        """
        Gets the ids of this Blacklist.


        :return: The ids of this Blacklist.
        :rtype: list[str]
        """
        return self._ids

    @ids.setter
    def ids(self, ids):
        """
        Sets the ids of this Blacklist.


        :param ids: The ids of this Blacklist.
        :type: list[str]
        """
        self._ids = ids

    @property
    def updated_date(self):
        """
        Gets the updated_date of this Blacklist.


        :return: The updated_date of this Blacklist.
        :rtype: datetime
        """
        return self._updated_date

    @updated_date.setter
    def updated_date(self, updated_date):
        """
        Sets the updated_date of this Blacklist.


        :param updated_date: The updated_date of this Blacklist.
        :type: datetime
        """
        self._updated_date = updated_date

    @property
    def created_date(self):
        """
        Gets the created_date of this Blacklist.


        :return: The created_date of this Blacklist.
        :rtype: datetime
        """
        return self._created_date

    @created_date.setter
    def created_date(self, created_date):
        """
        Sets the created_date of this Blacklist.


        :param created_date: The created_date of this Blacklist.
        :type: datetime
        """
        self._created_date = created_date

    @property
    def consumer(self):
        """
        Gets the consumer of this Blacklist.


        :return: The consumer of this Blacklist.
        :rtype: str
        """
        return self._consumer

    @consumer.setter
    def consumer(self, consumer):
        """
        Sets the consumer of this Blacklist.


        :param consumer: The consumer of this Blacklist.
        :type: str
        """
        self._consumer = consumer

    @property
    def entity_type(self):
        """
        Gets the entity_type of this Blacklist.


        :return: The entity_type of this Blacklist.
        :rtype: str
        """
        return self._entity_type

    @entity_type.setter
    def entity_type(self, entity_type):
        """
        Sets the entity_type of this Blacklist.


        :param entity_type: The entity_type of this Blacklist.
        :type: str
        """
        self._entity_type = entity_type

    @property
    def start_date(self):
        """
        Gets the start_date of this Blacklist.


        :return: The start_date of this Blacklist.
        :rtype: datetime
        """
        return self._start_date

    @start_date.setter
    def start_date(self, start_date):
        """
        Sets the start_date of this Blacklist.


        :param start_date: The start_date of this Blacklist.
        :type: datetime
        """
        self._start_date = start_date

    @property
    def end_date(self):
        """
        Gets the end_date of this Blacklist.


        :return: The end_date of this Blacklist.
        :rtype: datetime
        """
        return self._end_date

    @end_date.setter
    def end_date(self, end_date):
        """
        Sets the end_date of this Blacklist.


        :param end_date: The end_date of this Blacklist.
        :type: datetime
        """
        self._end_date = end_date

    @property
    def scope(self):
        """
        Gets the scope of this Blacklist.


        :return: The scope of this Blacklist.
        :rtype: str
        """
        return self._scope

    @scope.setter
    def scope(self, scope):
        """
        Sets the scope of this Blacklist.


        :param scope: The scope of this Blacklist.
        :type: str
        """
        self._scope = scope

    @property
    def disabled(self):
        """
        Gets the disabled of this Blacklist.


        :return: The disabled of this Blacklist.
        :rtype: bool
        """
        return self._disabled

    @disabled.setter
    def disabled(self, disabled):
        """
        Sets the disabled of this Blacklist.


        :param disabled: The disabled of this Blacklist.
        :type: bool
        """
        self._disabled = disabled

    @property
    def id(self):
        """
        Gets the id of this Blacklist.


        :return: The id of this Blacklist.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this Blacklist.


        :param id: The id of this Blacklist.
        :type: str
        """
        self._id = id

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()
