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

class Swaption(object):
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
        'start_date': 'datetime',
        'is_payer_not_receiver': 'bool',
        'is_delivery_not_cash': 'bool',
        'swap': 'LusidInstrument',
        'instrument_type': 'str'
    }

    attribute_map = {
        'start_date': 'startDate',
        'is_payer_not_receiver': 'isPayerNotReceiver',
        'is_delivery_not_cash': 'isDeliveryNotCash',
        'swap': 'swap',
        'instrument_type': 'instrumentType'
    }

    required_map = {
        'start_date': 'required',
        'is_payer_not_receiver': 'required',
        'is_delivery_not_cash': 'required',
        'swap': 'required',
        'instrument_type': 'required'
    }

    def __init__(self, start_date=None, is_payer_not_receiver=None, is_delivery_not_cash=None, swap=None, instrument_type=None):  # noqa: E501
        """
        Swaption - a model defined in OpenAPI

        :param start_date:  (required)
        :type start_date: datetime
        :param is_payer_not_receiver:  True if on exercise the holder of the option enters the swap paying fixed, false if floating. (required)
        :type is_payer_not_receiver: bool
        :param is_delivery_not_cash:  True of the option is settled in cash false if by delivery of the swap. (required)
        :type is_delivery_not_cash: bool
        :param swap:  (required)
        :type swap: lusid.LusidInstrument
        :param instrument_type:  Instrument type, must be property for JSON. (required)
        :type instrument_type: str

        """  # noqa: E501

        self._start_date = None
        self._is_payer_not_receiver = None
        self._is_delivery_not_cash = None
        self._swap = None
        self._instrument_type = None
        self.discriminator = None

        self.start_date = start_date
        self.is_payer_not_receiver = is_payer_not_receiver
        self.is_delivery_not_cash = is_delivery_not_cash
        self.swap = swap
        self.instrument_type = instrument_type

    @property
    def start_date(self):
        """Gets the start_date of this Swaption.  # noqa: E501


        :return: The start_date of this Swaption.  # noqa: E501
        :rtype: datetime
        """
        return self._start_date

    @start_date.setter
    def start_date(self, start_date):
        """Sets the start_date of this Swaption.


        :param start_date: The start_date of this Swaption.  # noqa: E501
        :type: datetime
        """
        if start_date is None:
            raise ValueError("Invalid value for `start_date`, must not be `None`")  # noqa: E501

        self._start_date = start_date

    @property
    def is_payer_not_receiver(self):
        """Gets the is_payer_not_receiver of this Swaption.  # noqa: E501

        True if on exercise the holder of the option enters the swap paying fixed, false if floating.  # noqa: E501

        :return: The is_payer_not_receiver of this Swaption.  # noqa: E501
        :rtype: bool
        """
        return self._is_payer_not_receiver

    @is_payer_not_receiver.setter
    def is_payer_not_receiver(self, is_payer_not_receiver):
        """Sets the is_payer_not_receiver of this Swaption.

        True if on exercise the holder of the option enters the swap paying fixed, false if floating.  # noqa: E501

        :param is_payer_not_receiver: The is_payer_not_receiver of this Swaption.  # noqa: E501
        :type: bool
        """
        if is_payer_not_receiver is None:
            raise ValueError("Invalid value for `is_payer_not_receiver`, must not be `None`")  # noqa: E501

        self._is_payer_not_receiver = is_payer_not_receiver

    @property
    def is_delivery_not_cash(self):
        """Gets the is_delivery_not_cash of this Swaption.  # noqa: E501

        True of the option is settled in cash false if by delivery of the swap.  # noqa: E501

        :return: The is_delivery_not_cash of this Swaption.  # noqa: E501
        :rtype: bool
        """
        return self._is_delivery_not_cash

    @is_delivery_not_cash.setter
    def is_delivery_not_cash(self, is_delivery_not_cash):
        """Sets the is_delivery_not_cash of this Swaption.

        True of the option is settled in cash false if by delivery of the swap.  # noqa: E501

        :param is_delivery_not_cash: The is_delivery_not_cash of this Swaption.  # noqa: E501
        :type: bool
        """
        if is_delivery_not_cash is None:
            raise ValueError("Invalid value for `is_delivery_not_cash`, must not be `None`")  # noqa: E501

        self._is_delivery_not_cash = is_delivery_not_cash

    @property
    def swap(self):
        """Gets the swap of this Swaption.  # noqa: E501


        :return: The swap of this Swaption.  # noqa: E501
        :rtype: LusidInstrument
        """
        return self._swap

    @swap.setter
    def swap(self, swap):
        """Sets the swap of this Swaption.


        :param swap: The swap of this Swaption.  # noqa: E501
        :type: LusidInstrument
        """
        if swap is None:
            raise ValueError("Invalid value for `swap`, must not be `None`")  # noqa: E501

        self._swap = swap

    @property
    def instrument_type(self):
        """Gets the instrument_type of this Swaption.  # noqa: E501

        Instrument type, must be property for JSON.  # noqa: E501

        :return: The instrument_type of this Swaption.  # noqa: E501
        :rtype: str
        """
        return self._instrument_type

    @instrument_type.setter
    def instrument_type(self, instrument_type):
        """Sets the instrument_type of this Swaption.

        Instrument type, must be property for JSON.  # noqa: E501

        :param instrument_type: The instrument_type of this Swaption.  # noqa: E501
        :type: str
        """
        if instrument_type is None:
            raise ValueError("Invalid value for `instrument_type`, must not be `None`")  # noqa: E501
        allowed_values = ["QuotedSecurity", "InterestRateSwap", "FxForward", "Exotic", "FxOption", "CreditDefaultSwap", "InterestRateSwaption", "Bond", "EquityOption", "Unknown"]  # noqa: E501
        if instrument_type not in allowed_values:
            raise ValueError(
                "Invalid value for `instrument_type` ({0}), must be one of {1}"  # noqa: E501
                .format(instrument_type, allowed_values)
            )

        self._instrument_type = instrument_type

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
        if not isinstance(other, Swaption):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
