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

class SwapInstrument(object):
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
        'maturity_date': 'datetime',
        'legs': 'list[InstrumentLeg]',
        'notional': 'float',
        'is_amortizing': 'bool',
        'notional_exchange_type': 'str',
        'instrument_type': 'str'
    }

    attribute_map = {
        'start_date': 'startDate',
        'maturity_date': 'maturityDate',
        'legs': 'legs',
        'notional': 'notional',
        'is_amortizing': 'isAmortizing',
        'notional_exchange_type': 'notionalExchangeType',
        'instrument_type': 'instrumentType'
    }

    required_map = {
        'start_date': 'required',
        'maturity_date': 'required',
        'legs': 'required',
        'notional': 'required',
        'is_amortizing': 'required',
        'notional_exchange_type': 'required',
        'instrument_type': 'required'
    }

    def __init__(self, start_date=None, maturity_date=None, legs=None, notional=None, is_amortizing=None, notional_exchange_type=None, instrument_type=None):  # noqa: E501
        """
        SwapInstrument - a model defined in OpenAPI

        :param start_date:  Starting date of the swap (required)
        :type start_date: datetime
        :param maturity_date:  Maturity date of the swap (required)
        :type maturity_date: datetime
        :param legs:  True if the swap is amortizing (required)
        :type legs: list[lusid.InstrumentLeg]
        :param notional:  The notional. (required)
        :type notional: float
        :param is_amortizing:  True if the swap is amortizing (required)
        :type is_amortizing: bool
        :param notional_exchange_type:  True notional exchange type. (required)
        :type notional_exchange_type: str
        :param instrument_type:  Instrument type, must be property for JSON. (required)
        :type instrument_type: str

        """  # noqa: E501

        self._start_date = None
        self._maturity_date = None
        self._legs = None
        self._notional = None
        self._is_amortizing = None
        self._notional_exchange_type = None
        self._instrument_type = None
        self.discriminator = None

        self.start_date = start_date
        self.maturity_date = maturity_date
        self.legs = legs
        self.notional = notional
        self.is_amortizing = is_amortizing
        self.notional_exchange_type = notional_exchange_type
        self.instrument_type = instrument_type

    @property
    def start_date(self):
        """Gets the start_date of this SwapInstrument.  # noqa: E501

        Starting date of the swap  # noqa: E501

        :return: The start_date of this SwapInstrument.  # noqa: E501
        :rtype: datetime
        """
        return self._start_date

    @start_date.setter
    def start_date(self, start_date):
        """Sets the start_date of this SwapInstrument.

        Starting date of the swap  # noqa: E501

        :param start_date: The start_date of this SwapInstrument.  # noqa: E501
        :type: datetime
        """
        if start_date is None:
            raise ValueError("Invalid value for `start_date`, must not be `None`")  # noqa: E501

        self._start_date = start_date

    @property
    def maturity_date(self):
        """Gets the maturity_date of this SwapInstrument.  # noqa: E501

        Maturity date of the swap  # noqa: E501

        :return: The maturity_date of this SwapInstrument.  # noqa: E501
        :rtype: datetime
        """
        return self._maturity_date

    @maturity_date.setter
    def maturity_date(self, maturity_date):
        """Sets the maturity_date of this SwapInstrument.

        Maturity date of the swap  # noqa: E501

        :param maturity_date: The maturity_date of this SwapInstrument.  # noqa: E501
        :type: datetime
        """
        if maturity_date is None:
            raise ValueError("Invalid value for `maturity_date`, must not be `None`")  # noqa: E501

        self._maturity_date = maturity_date

    @property
    def legs(self):
        """Gets the legs of this SwapInstrument.  # noqa: E501

        True if the swap is amortizing  # noqa: E501

        :return: The legs of this SwapInstrument.  # noqa: E501
        :rtype: list[InstrumentLeg]
        """
        return self._legs

    @legs.setter
    def legs(self, legs):
        """Sets the legs of this SwapInstrument.

        True if the swap is amortizing  # noqa: E501

        :param legs: The legs of this SwapInstrument.  # noqa: E501
        :type: list[InstrumentLeg]
        """
        if legs is None:
            raise ValueError("Invalid value for `legs`, must not be `None`")  # noqa: E501

        self._legs = legs

    @property
    def notional(self):
        """Gets the notional of this SwapInstrument.  # noqa: E501

        The notional.  # noqa: E501

        :return: The notional of this SwapInstrument.  # noqa: E501
        :rtype: float
        """
        return self._notional

    @notional.setter
    def notional(self, notional):
        """Sets the notional of this SwapInstrument.

        The notional.  # noqa: E501

        :param notional: The notional of this SwapInstrument.  # noqa: E501
        :type: float
        """
        if notional is None:
            raise ValueError("Invalid value for `notional`, must not be `None`")  # noqa: E501

        self._notional = notional

    @property
    def is_amortizing(self):
        """Gets the is_amortizing of this SwapInstrument.  # noqa: E501

        True if the swap is amortizing  # noqa: E501

        :return: The is_amortizing of this SwapInstrument.  # noqa: E501
        :rtype: bool
        """
        return self._is_amortizing

    @is_amortizing.setter
    def is_amortizing(self, is_amortizing):
        """Sets the is_amortizing of this SwapInstrument.

        True if the swap is amortizing  # noqa: E501

        :param is_amortizing: The is_amortizing of this SwapInstrument.  # noqa: E501
        :type: bool
        """
        if is_amortizing is None:
            raise ValueError("Invalid value for `is_amortizing`, must not be `None`")  # noqa: E501

        self._is_amortizing = is_amortizing

    @property
    def notional_exchange_type(self):
        """Gets the notional_exchange_type of this SwapInstrument.  # noqa: E501

        True notional exchange type.  # noqa: E501

        :return: The notional_exchange_type of this SwapInstrument.  # noqa: E501
        :rtype: str
        """
        return self._notional_exchange_type

    @notional_exchange_type.setter
    def notional_exchange_type(self, notional_exchange_type):
        """Sets the notional_exchange_type of this SwapInstrument.

        True notional exchange type.  # noqa: E501

        :param notional_exchange_type: The notional_exchange_type of this SwapInstrument.  # noqa: E501
        :type: str
        """
        if notional_exchange_type is None:
            raise ValueError("Invalid value for `notional_exchange_type`, must not be `None`")  # noqa: E501
        allowed_values = ["None", "Initial", "Final", "Both"]  # noqa: E501
        if notional_exchange_type not in allowed_values:
            raise ValueError(
                "Invalid value for `notional_exchange_type` ({0}), must be one of {1}"  # noqa: E501
                .format(notional_exchange_type, allowed_values)
            )

        self._notional_exchange_type = notional_exchange_type

    @property
    def instrument_type(self):
        """Gets the instrument_type of this SwapInstrument.  # noqa: E501

        Instrument type, must be property for JSON.  # noqa: E501

        :return: The instrument_type of this SwapInstrument.  # noqa: E501
        :rtype: str
        """
        return self._instrument_type

    @instrument_type.setter
    def instrument_type(self, instrument_type):
        """Sets the instrument_type of this SwapInstrument.

        Instrument type, must be property for JSON.  # noqa: E501

        :param instrument_type: The instrument_type of this SwapInstrument.  # noqa: E501
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
        if not isinstance(other, SwapInstrument):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
