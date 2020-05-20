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

class ResourceListOfValueType(object):
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
        'values': 'list[str]',
        'href': 'str',
        'links': 'list[Link]'
    }

    attribute_map = {
        'values': 'values',
        'href': 'href',
        'links': 'links'
    }

    required_map = {
        'values': 'required',
        'href': 'optional',
        'links': 'optional'
    }

    def __init__(self, values=None, href=None, links=None):  # noqa: E501
        """
        ResourceListOfValueType - a model defined in OpenAPI

        :param values:  (required)
        :type values: list[str]
        :param href: 
        :type href: str
        :param links: 
        :type links: list[lusid.Link]

        """  # noqa: E501

        self._values = None
        self._href = None
        self._links = None
        self.discriminator = None

        self.values = values
        if href is not None:
            self.href = href
        if links is not None:
            self.links = links

    @property
    def values(self):
        """Gets the values of this ResourceListOfValueType.  # noqa: E501


        :return: The values of this ResourceListOfValueType.  # noqa: E501
        :rtype: list[str]
        """
        return self._values

    @values.setter
    def values(self, values):
        """Sets the values of this ResourceListOfValueType.


        :param values: The values of this ResourceListOfValueType.  # noqa: E501
        :type: list[str]
        """
        if values is None:
            raise ValueError("Invalid value for `values`, must not be `None`")  # noqa: E501
        allowed_values = ["String", "Int", "Decimal", "DateTime", "Boolean", "Map", "List", "PropertyArray", "Percentage", "BenchmarkType", "Code", "Id", "Uri", "ArrayOfIds", "ArrayOfTransactionAliases", "ArrayofTransactionMovements", "ArrayofUnits", "StringArray", "CurrencyAndAmount", "TradePrice", "UnitCreation", "Currency", "UserId", "MetricValue", "QuoteId", "QuoteSeriesId", "ResourceId", "ResultValue", "CutLocalTime", "DateOrCutLabel", "Transition", "StructuredData", "StructuredDataId", "ConfigurationRecipe", "ConfigurationRecipeSnippet", "StructuredResultDataId", "StructuredResultData", "DataMapping", "LusidInstrument", "WeightedInstrument", "Tenor", "CdsDetailSpecifications", "FlowConventions", "OrderId"]  # noqa: E501
        if not set(values).issubset(set(allowed_values)):
            raise ValueError(
                "Invalid values for `values` [{0}], must be a subset of [{1}]"  # noqa: E501
                .format(", ".join(map(str, set(values) - set(allowed_values))),  # noqa: E501
                        ", ".join(map(str, allowed_values)))
            )

        self._values = values

    @property
    def href(self):
        """Gets the href of this ResourceListOfValueType.  # noqa: E501


        :return: The href of this ResourceListOfValueType.  # noqa: E501
        :rtype: str
        """
        return self._href

    @href.setter
    def href(self, href):
        """Sets the href of this ResourceListOfValueType.


        :param href: The href of this ResourceListOfValueType.  # noqa: E501
        :type: str
        """

        self._href = href

    @property
    def links(self):
        """Gets the links of this ResourceListOfValueType.  # noqa: E501


        :return: The links of this ResourceListOfValueType.  # noqa: E501
        :rtype: list[Link]
        """
        return self._links

    @links.setter
    def links(self, links):
        """Sets the links of this ResourceListOfValueType.


        :param links: The links of this ResourceListOfValueType.  # noqa: E501
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
        if not isinstance(other, ResourceListOfValueType):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
