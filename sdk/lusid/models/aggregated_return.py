# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 0.11.3114
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

class AggregatedReturn(object):
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
        'effective_at': 'datetime',
        'opening_market_value': 'float',
        'metrics_value': 'dict(str, float)',
        'frequency': 'str'
    }

    attribute_map = {
        'effective_at': 'effectiveAt',
        'opening_market_value': 'openingMarketValue',
        'metrics_value': 'metricsValue',
        'frequency': 'frequency'
    }

    required_map = {
        'effective_at': 'required',
        'opening_market_value': 'required',
        'metrics_value': 'required',
        'frequency': 'optional'
    }

    def __init__(self, effective_at=None, opening_market_value=None, metrics_value=None, frequency=None):  # noqa: E501
        """
        AggregatedReturn - a model defined in OpenAPI

        :param effective_at:  The effectiveAt for the return. (required)
        :type effective_at: datetime
        :param opening_market_value:  The opening market value. (required)
        :type opening_market_value: float
        :param metrics_value:  The value for the specified metric. (required)
        :type metrics_value: dict(str, float)
        :param frequency:  Show the aggregated output returns on a Daily or Monthly period.
        :type frequency: str

        """  # noqa: E501

        self._effective_at = None
        self._opening_market_value = None
        self._metrics_value = None
        self._frequency = None
        self.discriminator = None

        self.effective_at = effective_at
        self.opening_market_value = opening_market_value
        self.metrics_value = metrics_value
        self.frequency = frequency

    @property
    def effective_at(self):
        """Gets the effective_at of this AggregatedReturn.  # noqa: E501

        The effectiveAt for the return.  # noqa: E501

        :return: The effective_at of this AggregatedReturn.  # noqa: E501
        :rtype: datetime
        """
        return self._effective_at

    @effective_at.setter
    def effective_at(self, effective_at):
        """Sets the effective_at of this AggregatedReturn.

        The effectiveAt for the return.  # noqa: E501

        :param effective_at: The effective_at of this AggregatedReturn.  # noqa: E501
        :type: datetime
        """
        if effective_at is None:
            raise ValueError("Invalid value for `effective_at`, must not be `None`")  # noqa: E501

        self._effective_at = effective_at

    @property
    def opening_market_value(self):
        """Gets the opening_market_value of this AggregatedReturn.  # noqa: E501

        The opening market value.  # noqa: E501

        :return: The opening_market_value of this AggregatedReturn.  # noqa: E501
        :rtype: float
        """
        return self._opening_market_value

    @opening_market_value.setter
    def opening_market_value(self, opening_market_value):
        """Sets the opening_market_value of this AggregatedReturn.

        The opening market value.  # noqa: E501

        :param opening_market_value: The opening_market_value of this AggregatedReturn.  # noqa: E501
        :type: float
        """
        if opening_market_value is None:
            raise ValueError("Invalid value for `opening_market_value`, must not be `None`")  # noqa: E501

        self._opening_market_value = opening_market_value

    @property
    def metrics_value(self):
        """Gets the metrics_value of this AggregatedReturn.  # noqa: E501

        The value for the specified metric.  # noqa: E501

        :return: The metrics_value of this AggregatedReturn.  # noqa: E501
        :rtype: dict(str, float)
        """
        return self._metrics_value

    @metrics_value.setter
    def metrics_value(self, metrics_value):
        """Sets the metrics_value of this AggregatedReturn.

        The value for the specified metric.  # noqa: E501

        :param metrics_value: The metrics_value of this AggregatedReturn.  # noqa: E501
        :type: dict(str, float)
        """
        if metrics_value is None:
            raise ValueError("Invalid value for `metrics_value`, must not be `None`")  # noqa: E501

        self._metrics_value = metrics_value

    @property
    def frequency(self):
        """Gets the frequency of this AggregatedReturn.  # noqa: E501

        Show the aggregated output returns on a Daily or Monthly period.  # noqa: E501

        :return: The frequency of this AggregatedReturn.  # noqa: E501
        :rtype: str
        """
        return self._frequency

    @frequency.setter
    def frequency(self, frequency):
        """Sets the frequency of this AggregatedReturn.

        Show the aggregated output returns on a Daily or Monthly period.  # noqa: E501

        :param frequency: The frequency of this AggregatedReturn.  # noqa: E501
        :type: str
        """

        self._frequency = frequency

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
        if not isinstance(other, AggregatedReturn):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
