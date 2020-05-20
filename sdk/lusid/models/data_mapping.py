# coding: utf-8

"""
    LUSID API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.10.1391
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

class DataMapping(object):
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
        'data_field_name_mappings': 'dict(str, DataDefinition)',
        'links': 'list[Link]'
    }

    attribute_map = {
        'data_field_name_mappings': 'dataFieldNameMappings',
        'links': 'links'
    }

    required_map = {
        'data_field_name_mappings': 'optional',
        'links': 'optional'
    }

    def __init__(self, data_field_name_mappings=None, links=None):  # noqa: E501
        """
        DataMapping - a model defined in OpenAPI

        :param data_field_name_mappings:  A map from LUSID item keys to data definitions that define the names, types and degree of uniqueness of data provided to LUSID in structured data stores.
        :type data_field_name_mappings: dict[str, lusid.DataDefinition]
        :param links: 
        :type links: list[lusid.Link]

        """  # noqa: E501

        self._data_field_name_mappings = None
        self._links = None
        self.discriminator = None

        if data_field_name_mappings is not None:
            self.data_field_name_mappings = data_field_name_mappings
        if links is not None:
            self.links = links

    @property
    def data_field_name_mappings(self):
        """Gets the data_field_name_mappings of this DataMapping.  # noqa: E501

        A map from LUSID item keys to data definitions that define the names, types and degree of uniqueness of data provided to LUSID in structured data stores.  # noqa: E501

        :return: The data_field_name_mappings of this DataMapping.  # noqa: E501
        :rtype: dict(str, DataDefinition)
        """
        return self._data_field_name_mappings

    @data_field_name_mappings.setter
    def data_field_name_mappings(self, data_field_name_mappings):
        """Sets the data_field_name_mappings of this DataMapping.

        A map from LUSID item keys to data definitions that define the names, types and degree of uniqueness of data provided to LUSID in structured data stores.  # noqa: E501

        :param data_field_name_mappings: The data_field_name_mappings of this DataMapping.  # noqa: E501
        :type: dict(str, DataDefinition)
        """

        self._data_field_name_mappings = data_field_name_mappings

    @property
    def links(self):
        """Gets the links of this DataMapping.  # noqa: E501


        :return: The links of this DataMapping.  # noqa: E501
        :rtype: list[Link]
        """
        return self._links

    @links.setter
    def links(self, links):
        """Sets the links of this DataMapping.


        :param links: The links of this DataMapping.  # noqa: E501
        :type: list[Link]
        """

        self._links = links

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
        if not isinstance(other, DataMapping):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
