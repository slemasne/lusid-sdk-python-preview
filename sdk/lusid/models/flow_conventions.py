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

class FlowConventions(object):
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
        'currency': 'str',
        'payment_frequency': 'Tenor',
        'day_count_convention': 'str',
        'roll_convention': 'str',
        'holiday_calendars': 'list[str]'
    }

    attribute_map = {
        'currency': 'currency',
        'payment_frequency': 'paymentFrequency',
        'day_count_convention': 'dayCountConvention',
        'roll_convention': 'rollConvention',
        'holiday_calendars': 'holidayCalendars'
    }

    required_map = {
        'currency': 'required',
        'payment_frequency': 'required',
        'day_count_convention': 'required',
        'roll_convention': 'required',
        'holiday_calendars': 'required'
    }

    def __init__(self, currency=None, payment_frequency=None, day_count_convention=None, roll_convention=None, holiday_calendars=None):  # noqa: E501
        """
        FlowConventions - a model defined in OpenAPI

        :param currency:  Currency of the flow convention. (required)
        :type currency: str
        :param payment_frequency:  (required)
        :type payment_frequency: lusid.Tenor
        :param day_count_convention:  when calculating the fraction of a year between two dates, what convention is used to represent the number of days in a year  and difference between them. (required)
        :type day_count_convention: str
        :param roll_convention:  when generating a set of dates, what convention should be used for adjusting dates that coincide with a non-business day. (required)
        :type roll_convention: str
        :param holiday_calendars:  An array of strings denoting holiday calendars that apply to generation and payment. (required)
        :type holiday_calendars: list[str]

        """  # noqa: E501

        self._currency = None
        self._payment_frequency = None
        self._day_count_convention = None
        self._roll_convention = None
        self._holiday_calendars = None
        self.discriminator = None

        self.currency = currency
        self.payment_frequency = payment_frequency
        self.day_count_convention = day_count_convention
        self.roll_convention = roll_convention
        self.holiday_calendars = holiday_calendars

    @property
    def currency(self):
        """Gets the currency of this FlowConventions.  # noqa: E501

        Currency of the flow convention.  # noqa: E501

        :return: The currency of this FlowConventions.  # noqa: E501
        :rtype: str
        """
        return self._currency

    @currency.setter
    def currency(self, currency):
        """Sets the currency of this FlowConventions.

        Currency of the flow convention.  # noqa: E501

        :param currency: The currency of this FlowConventions.  # noqa: E501
        :type: str
        """
        if currency is None:
            raise ValueError("Invalid value for `currency`, must not be `None`")  # noqa: E501

        self._currency = currency

    @property
    def payment_frequency(self):
        """Gets the payment_frequency of this FlowConventions.  # noqa: E501


        :return: The payment_frequency of this FlowConventions.  # noqa: E501
        :rtype: Tenor
        """
        return self._payment_frequency

    @payment_frequency.setter
    def payment_frequency(self, payment_frequency):
        """Sets the payment_frequency of this FlowConventions.


        :param payment_frequency: The payment_frequency of this FlowConventions.  # noqa: E501
        :type: Tenor
        """
        if payment_frequency is None:
            raise ValueError("Invalid value for `payment_frequency`, must not be `None`")  # noqa: E501

        self._payment_frequency = payment_frequency

    @property
    def day_count_convention(self):
        """Gets the day_count_convention of this FlowConventions.  # noqa: E501

        when calculating the fraction of a year between two dates, what convention is used to represent the number of days in a year  and difference between them.  # noqa: E501

        :return: The day_count_convention of this FlowConventions.  # noqa: E501
        :rtype: str
        """
        return self._day_count_convention

    @day_count_convention.setter
    def day_count_convention(self, day_count_convention):
        """Sets the day_count_convention of this FlowConventions.

        when calculating the fraction of a year between two dates, what convention is used to represent the number of days in a year  and difference between them.  # noqa: E501

        :param day_count_convention: The day_count_convention of this FlowConventions.  # noqa: E501
        :type: str
        """
        if day_count_convention is None:
            raise ValueError("Invalid value for `day_count_convention`, must not be `None`")  # noqa: E501
        allowed_values = ["Actual360", "Act360", "MoneyMarket", "Actual365", "Act365", "Thirty360", "ThirtyU360", "Bond", "ThirtyE360", "EuroBond", "ActAct", "ActualActual", "ActActIsda", "Invalid"]  # noqa: E501
        if day_count_convention not in allowed_values:
            raise ValueError(
                "Invalid value for `day_count_convention` ({0}), must be one of {1}"  # noqa: E501
                .format(day_count_convention, allowed_values)
            )

        self._day_count_convention = day_count_convention

    @property
    def roll_convention(self):
        """Gets the roll_convention of this FlowConventions.  # noqa: E501

        when generating a set of dates, what convention should be used for adjusting dates that coincide with a non-business day.  # noqa: E501

        :return: The roll_convention of this FlowConventions.  # noqa: E501
        :rtype: str
        """
        return self._roll_convention

    @roll_convention.setter
    def roll_convention(self, roll_convention):
        """Sets the roll_convention of this FlowConventions.

        when generating a set of dates, what convention should be used for adjusting dates that coincide with a non-business day.  # noqa: E501

        :param roll_convention: The roll_convention of this FlowConventions.  # noqa: E501
        :type: str
        """
        if roll_convention is None:
            raise ValueError("Invalid value for `roll_convention`, must not be `None`")  # noqa: E501
        allowed_values = ["NoAdjustment", "None", "Previous", "P", "Following", "F", "ModifiedPrevious", "MP", "ModifiedFollowing", "MF", "EndOfMonth", "EOM", "EndOfMonthPrevious", "EOMP", "EndOfMonthFollowing", "EOMF", "Invalid"]  # noqa: E501
        if roll_convention not in allowed_values:
            raise ValueError(
                "Invalid value for `roll_convention` ({0}), must be one of {1}"  # noqa: E501
                .format(roll_convention, allowed_values)
            )

        self._roll_convention = roll_convention

    @property
    def holiday_calendars(self):
        """Gets the holiday_calendars of this FlowConventions.  # noqa: E501

        An array of strings denoting holiday calendars that apply to generation and payment.  # noqa: E501

        :return: The holiday_calendars of this FlowConventions.  # noqa: E501
        :rtype: list[str]
        """
        return self._holiday_calendars

    @holiday_calendars.setter
    def holiday_calendars(self, holiday_calendars):
        """Sets the holiday_calendars of this FlowConventions.

        An array of strings denoting holiday calendars that apply to generation and payment.  # noqa: E501

        :param holiday_calendars: The holiday_calendars of this FlowConventions.  # noqa: E501
        :type: list[str]
        """
        if holiday_calendars is None:
            raise ValueError("Invalid value for `holiday_calendars`, must not be `None`")  # noqa: E501

        self._holiday_calendars = holiday_calendars

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
        if not isinstance(other, FlowConventions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
