# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 0.11.3280
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

class Premium(object):
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
        'amount': 'float',
        'currency': 'str',
        'date': 'datetime'
    }

    attribute_map = {
        'amount': 'amount',
        'currency': 'currency',
        'date': 'date'
    }

    required_map = {
        'amount': 'required',
        'currency': 'required',
        'date': 'required'
    }

    def __init__(self, amount=None, currency=None, date=None):  # noqa: E501
        """
        Premium - a model defined in OpenAPI

        :param amount:  Premium amount (required)
        :type amount: float
        :param currency:  Premium currency (required)
        :type currency: str
        :param date:  Date when premium paid (required)
        :type date: datetime

        """  # noqa: E501

        self._amount = None
        self._currency = None
        self._date = None
        self.discriminator = None

        self.amount = amount
        self.currency = currency
        self.date = date

    @property
    def amount(self):
        """Gets the amount of this Premium.  # noqa: E501

        Premium amount  # noqa: E501

        :return: The amount of this Premium.  # noqa: E501
        :rtype: float
        """
        return self._amount

    @amount.setter
    def amount(self, amount):
        """Sets the amount of this Premium.

        Premium amount  # noqa: E501

        :param amount: The amount of this Premium.  # noqa: E501
        :type: float
        """
        if amount is None:
            raise ValueError("Invalid value for `amount`, must not be `None`")  # noqa: E501

        self._amount = amount

    @property
    def currency(self):
        """Gets the currency of this Premium.  # noqa: E501

        Premium currency  # noqa: E501

        :return: The currency of this Premium.  # noqa: E501
        :rtype: str
        """
        return self._currency

    @currency.setter
    def currency(self, currency):
        """Sets the currency of this Premium.

        Premium currency  # noqa: E501

        :param currency: The currency of this Premium.  # noqa: E501
        :type: str
        """
        if currency is None:
            raise ValueError("Invalid value for `currency`, must not be `None`")  # noqa: E501

        self._currency = currency

    @property
    def date(self):
        """Gets the date of this Premium.  # noqa: E501

        Date when premium paid  # noqa: E501

        :return: The date of this Premium.  # noqa: E501
        :rtype: datetime
        """
        return self._date

    @date.setter
    def date(self, date):
        """Sets the date of this Premium.

        Date when premium paid  # noqa: E501

        :param date: The date of this Premium.  # noqa: E501
        :type: datetime
        """
        if date is None:
            raise ValueError("Invalid value for `date`, must not be `None`")  # noqa: E501

        self._date = date

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
        if not isinstance(other, Premium):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other