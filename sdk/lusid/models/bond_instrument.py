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

class BondInstrument(object):
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
        'dom_ccy': 'str',
        'coupon_rate': 'float',
        'principal': 'float',
        'flow_conventions': 'FlowConventions',
        'instrument_type': 'str'
    }

    attribute_map = {
        'start_date': 'startDate',
        'maturity_date': 'maturityDate',
        'dom_ccy': 'domCcy',
        'coupon_rate': 'couponRate',
        'principal': 'principal',
        'flow_conventions': 'flowConventions',
        'instrument_type': 'instrumentType'
    }

    required_map = {
        'start_date': 'required',
        'maturity_date': 'required',
        'dom_ccy': 'required',
        'coupon_rate': 'required',
        'principal': 'required',
        'flow_conventions': 'required',
        'instrument_type': 'required'
    }

    def __init__(self, start_date=None, maturity_date=None, dom_ccy=None, coupon_rate=None, principal=None, flow_conventions=None, instrument_type=None):  # noqa: E501
        """
        BondInstrument - a model defined in OpenAPI

        :param start_date:  (required)
        :type start_date: datetime
        :param maturity_date:  (required)
        :type maturity_date: datetime
        :param dom_ccy:  (required)
        :type dom_ccy: str
        :param coupon_rate:  simple coupon rate. (required)
        :type coupon_rate: float
        :param principal:  The face-value or principal for the bond at outset.              This might be reduced through its lifetime in the event of amortization or similar. (required)
        :type principal: float
        :param flow_conventions:  (required)
        :type flow_conventions: lusid.FlowConventions
        :param instrument_type:  Instrument type, must be property for JSON. (required)
        :type instrument_type: str

        """  # noqa: E501

        self._start_date = None
        self._maturity_date = None
        self._dom_ccy = None
        self._coupon_rate = None
        self._principal = None
        self._flow_conventions = None
        self._instrument_type = None
        self.discriminator = None

        self.start_date = start_date
        self.maturity_date = maturity_date
        self.dom_ccy = dom_ccy
        self.coupon_rate = coupon_rate
        self.principal = principal
        self.flow_conventions = flow_conventions
        self.instrument_type = instrument_type

    @property
    def start_date(self):
        """Gets the start_date of this BondInstrument.  # noqa: E501


        :return: The start_date of this BondInstrument.  # noqa: E501
        :rtype: datetime
        """
        return self._start_date

    @start_date.setter
    def start_date(self, start_date):
        """Sets the start_date of this BondInstrument.


        :param start_date: The start_date of this BondInstrument.  # noqa: E501
        :type: datetime
        """
        if start_date is None:
            raise ValueError("Invalid value for `start_date`, must not be `None`")  # noqa: E501

        self._start_date = start_date

    @property
    def maturity_date(self):
        """Gets the maturity_date of this BondInstrument.  # noqa: E501


        :return: The maturity_date of this BondInstrument.  # noqa: E501
        :rtype: datetime
        """
        return self._maturity_date

    @maturity_date.setter
    def maturity_date(self, maturity_date):
        """Sets the maturity_date of this BondInstrument.


        :param maturity_date: The maturity_date of this BondInstrument.  # noqa: E501
        :type: datetime
        """
        if maturity_date is None:
            raise ValueError("Invalid value for `maturity_date`, must not be `None`")  # noqa: E501

        self._maturity_date = maturity_date

    @property
    def dom_ccy(self):
        """Gets the dom_ccy of this BondInstrument.  # noqa: E501


        :return: The dom_ccy of this BondInstrument.  # noqa: E501
        :rtype: str
        """
        return self._dom_ccy

    @dom_ccy.setter
    def dom_ccy(self, dom_ccy):
        """Sets the dom_ccy of this BondInstrument.


        :param dom_ccy: The dom_ccy of this BondInstrument.  # noqa: E501
        :type: str
        """
        if dom_ccy is None:
            raise ValueError("Invalid value for `dom_ccy`, must not be `None`")  # noqa: E501

        self._dom_ccy = dom_ccy

    @property
    def coupon_rate(self):
        """Gets the coupon_rate of this BondInstrument.  # noqa: E501

        simple coupon rate.  # noqa: E501

        :return: The coupon_rate of this BondInstrument.  # noqa: E501
        :rtype: float
        """
        return self._coupon_rate

    @coupon_rate.setter
    def coupon_rate(self, coupon_rate):
        """Sets the coupon_rate of this BondInstrument.

        simple coupon rate.  # noqa: E501

        :param coupon_rate: The coupon_rate of this BondInstrument.  # noqa: E501
        :type: float
        """
        if coupon_rate is None:
            raise ValueError("Invalid value for `coupon_rate`, must not be `None`")  # noqa: E501

        self._coupon_rate = coupon_rate

    @property
    def principal(self):
        """Gets the principal of this BondInstrument.  # noqa: E501

        The face-value or principal for the bond at outset.              This might be reduced through its lifetime in the event of amortization or similar.  # noqa: E501

        :return: The principal of this BondInstrument.  # noqa: E501
        :rtype: float
        """
        return self._principal

    @principal.setter
    def principal(self, principal):
        """Sets the principal of this BondInstrument.

        The face-value or principal for the bond at outset.              This might be reduced through its lifetime in the event of amortization or similar.  # noqa: E501

        :param principal: The principal of this BondInstrument.  # noqa: E501
        :type: float
        """
        if principal is None:
            raise ValueError("Invalid value for `principal`, must not be `None`")  # noqa: E501

        self._principal = principal

    @property
    def flow_conventions(self):
        """Gets the flow_conventions of this BondInstrument.  # noqa: E501


        :return: The flow_conventions of this BondInstrument.  # noqa: E501
        :rtype: FlowConventions
        """
        return self._flow_conventions

    @flow_conventions.setter
    def flow_conventions(self, flow_conventions):
        """Sets the flow_conventions of this BondInstrument.


        :param flow_conventions: The flow_conventions of this BondInstrument.  # noqa: E501
        :type: FlowConventions
        """
        if flow_conventions is None:
            raise ValueError("Invalid value for `flow_conventions`, must not be `None`")  # noqa: E501

        self._flow_conventions = flow_conventions

    @property
    def instrument_type(self):
        """Gets the instrument_type of this BondInstrument.  # noqa: E501

        Instrument type, must be property for JSON.  # noqa: E501

        :return: The instrument_type of this BondInstrument.  # noqa: E501
        :rtype: str
        """
        return self._instrument_type

    @instrument_type.setter
    def instrument_type(self, instrument_type):
        """Sets the instrument_type of this BondInstrument.

        Instrument type, must be property for JSON.  # noqa: E501

        :param instrument_type: The instrument_type of this BondInstrument.  # noqa: E501
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
        if not isinstance(other, BondInstrument):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
