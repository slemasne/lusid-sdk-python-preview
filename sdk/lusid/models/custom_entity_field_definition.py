# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 0.11.3390
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

class CustomEntityFieldDefinition(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
      required_map (dict): The key is attribute name
                           and the value is whether it is 'required' or 'optional'.
    """
    openapi_types = {
        'name': 'str',
        'temporality': 'str',
        'type': 'str',
        'required': 'bool'
    }

    attribute_map = {
        'name': 'name',
        'temporality': 'temporality',
        'type': 'type',
        'required': 'required'
    }

    required_map = {
        'name': 'required',
        'temporality': 'required',
        'type': 'required',
        'required': 'required'
    }

    def __init__(self, name=None, temporality=None, type=None, required=None):  # noqa: E501
        """
        CustomEntityFieldDefinition - a model defined in OpenAPI

        :param name:  (required)
        :type name: str
        :param temporality:  (required)
        :type temporality: str
        :param type:  (required)
        :type type: str
        :param required:  (required)
        :type required: bool

        """  # noqa: E501

        self._name = None
        self._temporality = None
        self._type = None
        self._required = None
        self.discriminator = None

        self.name = name
        self.temporality = temporality
        self.type = type
        self.required = required

    @property
    def name(self):
        """Gets the name of this CustomEntityFieldDefinition.  # noqa: E501


        :return: The name of this CustomEntityFieldDefinition.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this CustomEntityFieldDefinition.


        :param name: The name of this CustomEntityFieldDefinition.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def temporality(self):
        """Gets the temporality of this CustomEntityFieldDefinition.  # noqa: E501


        :return: The temporality of this CustomEntityFieldDefinition.  # noqa: E501
        :rtype: str
        """
        return self._temporality

    @temporality.setter
    def temporality(self, temporality):
        """Sets the temporality of this CustomEntityFieldDefinition.


        :param temporality: The temporality of this CustomEntityFieldDefinition.  # noqa: E501
        :type: str
        """
        if temporality is None:
            raise ValueError("Invalid value for `temporality`, must not be `None`")  # noqa: E501

        self._temporality = temporality

    @property
    def type(self):
        """Gets the type of this CustomEntityFieldDefinition.  # noqa: E501


        :return: The type of this CustomEntityFieldDefinition.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this CustomEntityFieldDefinition.


        :param type: The type of this CustomEntityFieldDefinition.  # noqa: E501
        :type: str
        """
        if type is None:
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501

        self._type = type

    @property
    def required(self):
        """Gets the required of this CustomEntityFieldDefinition.  # noqa: E501


        :return: The required of this CustomEntityFieldDefinition.  # noqa: E501
        :rtype: bool
        """
        return self._required

    @required.setter
    def required(self, required):
        """Sets the required of this CustomEntityFieldDefinition.


        :param required: The required of this CustomEntityFieldDefinition.  # noqa: E501
        :type: bool
        """
        if required is None:
            raise ValueError("Invalid value for `required`, must not be `None`")  # noqa: E501

        self._required = required

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, CustomEntityFieldDefinition):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
