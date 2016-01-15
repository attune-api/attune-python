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


class BlacklistParams(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """

    def __init__(self):
        """
        BlacklistParams - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'entity_type': 'str',
            'ids': 'list[str]',
            'active_from': 'datetime',
            'active_to': 'datetime',
            'disabled': 'bool',
            'scope': 'list[ScopeEntry]'
        }

        self.attribute_map = {
            'entity_type': 'entityType',
            'ids': 'ids',
            'active_from': 'activeFrom',
            'active_to': 'activeTo',
            'disabled': 'disabled',
            'scope': 'scope'
        }

        self._entity_type = None
        self._ids = None
        self._active_from = None
        self._active_to = None
        self._disabled = None
        self._scope = None

    @property
    def entity_type(self):
        """
        Gets the entity_type of this BlacklistParams.


        :return: The entity_type of this BlacklistParams.
        :rtype: str
        """
        return self._entity_type

    @entity_type.setter
    def entity_type(self, entity_type):
        """
        Sets the entity_type of this BlacklistParams.


        :param entity_type: The entity_type of this BlacklistParams.
        :type: str
        """
        self._entity_type = entity_type

    @property
    def ids(self):
        """
        Gets the ids of this BlacklistParams.


        :return: The ids of this BlacklistParams.
        :rtype: list[str]
        """
        return self._ids

    @ids.setter
    def ids(self, ids):
        """
        Sets the ids of this BlacklistParams.


        :param ids: The ids of this BlacklistParams.
        :type: list[str]
        """
        self._ids = ids

    @property
    def active_from(self):
        """
        Gets the active_from of this BlacklistParams.


        :return: The active_from of this BlacklistParams.
        :rtype: datetime
        """
        return self._active_from

    @active_from.setter
    def active_from(self, active_from):
        """
        Sets the active_from of this BlacklistParams.


        :param active_from: The active_from of this BlacklistParams.
        :type: datetime
        """
        self._active_from = active_from

    @property
    def active_to(self):
        """
        Gets the active_to of this BlacklistParams.


        :return: The active_to of this BlacklistParams.
        :rtype: datetime
        """
        return self._active_to

    @active_to.setter
    def active_to(self, active_to):
        """
        Sets the active_to of this BlacklistParams.


        :param active_to: The active_to of this BlacklistParams.
        :type: datetime
        """
        self._active_to = active_to

    @property
    def disabled(self):
        """
        Gets the disabled of this BlacklistParams.


        :return: The disabled of this BlacklistParams.
        :rtype: bool
        """
        return self._disabled

    @disabled.setter
    def disabled(self, disabled):
        """
        Sets the disabled of this BlacklistParams.


        :param disabled: The disabled of this BlacklistParams.
        :type: bool
        """
        self._disabled = disabled

    @property
    def scope(self):
        """
        Gets the scope of this BlacklistParams.


        :return: The scope of this BlacklistParams.
        :rtype: list[ScopeEntry]
        """
        return self._scope

    @scope.setter
    def scope(self, scope):
        """
        Sets the scope of this BlacklistParams.


        :param scope: The scope of this BlacklistParams.
        :type: list[ScopeEntry]
        """
        self._scope = scope

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
