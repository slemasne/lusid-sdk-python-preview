# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 0.11.3181
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

class OpaqueMarketData(object):
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
        'document': 'str',
        'format': 'str',
        'name': 'str',
        'market_data_type': 'str'
    }

    attribute_map = {
        'document': 'document',
        'format': 'format',
        'name': 'name',
        'market_data_type': 'marketDataType'
    }

    required_map = {
        'document': 'required',
        'format': 'required',
        'name': 'required',
        'market_data_type': 'required'
    }

    def __init__(self, document=None, format=None, name=None, market_data_type=None):  # noqa: E501
        """
        OpaqueMarketData - a model defined in OpenAPI

        :param document:  The document as a string. (required)
        :type document: str
        :param format:  What format is the document stored in, e.g. Xml.  Supported string (enumeration) values are: [Unknown, Xml, Json, Csv]. (required)
        :type format: str
        :param name:  Internal name of document. This is not used for search, it is simply a designator that helps identify the document  and could be anything (filename, ftp address or similar) (required)
        :type name: str
        :param market_data_type:  The available values are: DiscountFactorCurveData, EquityVolSurfaceData, FxVolSurfaceData, IrVolCubeData, OpaqueMarketData, YieldCurveData (required)
        :type market_data_type: str

        """  # noqa: E501

        self._document = None
        self._format = None
        self._name = None
        self._market_data_type = None
        self.discriminator = None

        self.document = document
        self.format = format
        self.name = name
        self.market_data_type = market_data_type

    @property
    def document(self):
        """Gets the document of this OpaqueMarketData.  # noqa: E501

        The document as a string.  # noqa: E501

        :return: The document of this OpaqueMarketData.  # noqa: E501
        :rtype: str
        """
        return self._document

    @document.setter
    def document(self, document):
        """Sets the document of this OpaqueMarketData.

        The document as a string.  # noqa: E501

        :param document: The document of this OpaqueMarketData.  # noqa: E501
        :type: str
        """
        if document is None:
            raise ValueError("Invalid value for `document`, must not be `None`")  # noqa: E501

        self._document = document

    @property
    def format(self):
        """Gets the format of this OpaqueMarketData.  # noqa: E501

        What format is the document stored in, e.g. Xml.  Supported string (enumeration) values are: [Unknown, Xml, Json, Csv].  # noqa: E501

        :return: The format of this OpaqueMarketData.  # noqa: E501
        :rtype: str
        """
        return self._format

    @format.setter
    def format(self, format):
        """Sets the format of this OpaqueMarketData.

        What format is the document stored in, e.g. Xml.  Supported string (enumeration) values are: [Unknown, Xml, Json, Csv].  # noqa: E501

        :param format: The format of this OpaqueMarketData.  # noqa: E501
        :type: str
        """
        if format is None:
            raise ValueError("Invalid value for `format`, must not be `None`")  # noqa: E501

        self._format = format

    @property
    def name(self):
        """Gets the name of this OpaqueMarketData.  # noqa: E501

        Internal name of document. This is not used for search, it is simply a designator that helps identify the document  and could be anything (filename, ftp address or similar)  # noqa: E501

        :return: The name of this OpaqueMarketData.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this OpaqueMarketData.

        Internal name of document. This is not used for search, it is simply a designator that helps identify the document  and could be anything (filename, ftp address or similar)  # noqa: E501

        :param name: The name of this OpaqueMarketData.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def market_data_type(self):
        """Gets the market_data_type of this OpaqueMarketData.  # noqa: E501

        The available values are: DiscountFactorCurveData, EquityVolSurfaceData, FxVolSurfaceData, IrVolCubeData, OpaqueMarketData, YieldCurveData  # noqa: E501

        :return: The market_data_type of this OpaqueMarketData.  # noqa: E501
        :rtype: str
        """
        return self._market_data_type

    @market_data_type.setter
    def market_data_type(self, market_data_type):
        """Sets the market_data_type of this OpaqueMarketData.

        The available values are: DiscountFactorCurveData, EquityVolSurfaceData, FxVolSurfaceData, IrVolCubeData, OpaqueMarketData, YieldCurveData  # noqa: E501

        :param market_data_type: The market_data_type of this OpaqueMarketData.  # noqa: E501
        :type: str
        """
        if market_data_type is None:
            raise ValueError("Invalid value for `market_data_type`, must not be `None`")  # noqa: E501
        allowed_values = ["DiscountFactorCurveData", "EquityVolSurfaceData", "FxVolSurfaceData", "IrVolCubeData", "OpaqueMarketData", "YieldCurveData"]  # noqa: E501
        if market_data_type not in allowed_values:
            raise ValueError(
                "Invalid value for `market_data_type` ({0}), must be one of {1}"  # noqa: E501
                .format(market_data_type, allowed_values)
            )

        self._market_data_type = market_data_type

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
        if not isinstance(other, OpaqueMarketData):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
