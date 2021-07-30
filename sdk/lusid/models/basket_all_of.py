# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 0.11.3344
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

class BasketAllOf(object):
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
        'basket_name': 'BasketIdentifier',
        'basket_type': 'str',
        'weighted_instruments': 'WeightedInstruments',
        'instrument_type': 'str'
    }

    attribute_map = {
        'basket_name': 'basketName',
        'basket_type': 'basketType',
        'weighted_instruments': 'weightedInstruments',
        'instrument_type': 'instrumentType'
    }

    required_map = {
        'basket_name': 'required',
        'basket_type': 'required',
        'weighted_instruments': 'required',
        'instrument_type': 'required'
    }

    def __init__(self, basket_name=None, basket_type=None, weighted_instruments=None, instrument_type=None):  # noqa: E501
        """
        BasketAllOf - a model defined in OpenAPI

        :param basket_name:  (required)
        :type basket_name: lusid.BasketIdentifier
        :param basket_type:  What contents does the basket have. The validation will check that the instrument types contained match those expected.  Supported string (enumeration) values are: [Bonds, Credits, Equities, EquitySwap, Unknown]. (required)
        :type basket_type: str
        :param weighted_instruments:  (required)
        :type weighted_instruments: lusid.WeightedInstruments
        :param instrument_type:  The available values are: QuotedSecurity, InterestRateSwap, FxForward, Future, ExoticInstrument, FxOption, CreditDefaultSwap, InterestRateSwaption, Bond, EquityOption, FixedLeg, FloatingLeg, BespokeCashFlowsLeg, Unknown, TermDeposit, ContractForDifference, EquitySwap, CashPerpetual, CashSettled, CdsIndex, Basket, FundingLeg, CrossCurrencySwap, FxSwap, ForwardRateAgreement, SimpleInstrument, Repo (required)
        :type instrument_type: str

        """  # noqa: E501

        self._basket_name = None
        self._basket_type = None
        self._weighted_instruments = None
        self._instrument_type = None
        self.discriminator = None

        self.basket_name = basket_name
        self.basket_type = basket_type
        self.weighted_instruments = weighted_instruments
        self.instrument_type = instrument_type

    @property
    def basket_name(self):
        """Gets the basket_name of this BasketAllOf.  # noqa: E501


        :return: The basket_name of this BasketAllOf.  # noqa: E501
        :rtype: BasketIdentifier
        """
        return self._basket_name

    @basket_name.setter
    def basket_name(self, basket_name):
        """Sets the basket_name of this BasketAllOf.


        :param basket_name: The basket_name of this BasketAllOf.  # noqa: E501
        :type: BasketIdentifier
        """
        if basket_name is None:
            raise ValueError("Invalid value for `basket_name`, must not be `None`")  # noqa: E501

        self._basket_name = basket_name

    @property
    def basket_type(self):
        """Gets the basket_type of this BasketAllOf.  # noqa: E501

        What contents does the basket have. The validation will check that the instrument types contained match those expected.  Supported string (enumeration) values are: [Bonds, Credits, Equities, EquitySwap, Unknown].  # noqa: E501

        :return: The basket_type of this BasketAllOf.  # noqa: E501
        :rtype: str
        """
        return self._basket_type

    @basket_type.setter
    def basket_type(self, basket_type):
        """Sets the basket_type of this BasketAllOf.

        What contents does the basket have. The validation will check that the instrument types contained match those expected.  Supported string (enumeration) values are: [Bonds, Credits, Equities, EquitySwap, Unknown].  # noqa: E501

        :param basket_type: The basket_type of this BasketAllOf.  # noqa: E501
        :type: str
        """
        if basket_type is None:
            raise ValueError("Invalid value for `basket_type`, must not be `None`")  # noqa: E501

        self._basket_type = basket_type

    @property
    def weighted_instruments(self):
        """Gets the weighted_instruments of this BasketAllOf.  # noqa: E501


        :return: The weighted_instruments of this BasketAllOf.  # noqa: E501
        :rtype: WeightedInstruments
        """
        return self._weighted_instruments

    @weighted_instruments.setter
    def weighted_instruments(self, weighted_instruments):
        """Sets the weighted_instruments of this BasketAllOf.


        :param weighted_instruments: The weighted_instruments of this BasketAllOf.  # noqa: E501
        :type: WeightedInstruments
        """
        if weighted_instruments is None:
            raise ValueError("Invalid value for `weighted_instruments`, must not be `None`")  # noqa: E501

        self._weighted_instruments = weighted_instruments

    @property
    def instrument_type(self):
        """Gets the instrument_type of this BasketAllOf.  # noqa: E501

        The available values are: QuotedSecurity, InterestRateSwap, FxForward, Future, ExoticInstrument, FxOption, CreditDefaultSwap, InterestRateSwaption, Bond, EquityOption, FixedLeg, FloatingLeg, BespokeCashFlowsLeg, Unknown, TermDeposit, ContractForDifference, EquitySwap, CashPerpetual, CashSettled, CdsIndex, Basket, FundingLeg, CrossCurrencySwap, FxSwap, ForwardRateAgreement, SimpleInstrument, Repo  # noqa: E501

        :return: The instrument_type of this BasketAllOf.  # noqa: E501
        :rtype: str
        """
        return self._instrument_type

    @instrument_type.setter
    def instrument_type(self, instrument_type):
        """Sets the instrument_type of this BasketAllOf.

        The available values are: QuotedSecurity, InterestRateSwap, FxForward, Future, ExoticInstrument, FxOption, CreditDefaultSwap, InterestRateSwaption, Bond, EquityOption, FixedLeg, FloatingLeg, BespokeCashFlowsLeg, Unknown, TermDeposit, ContractForDifference, EquitySwap, CashPerpetual, CashSettled, CdsIndex, Basket, FundingLeg, CrossCurrencySwap, FxSwap, ForwardRateAgreement, SimpleInstrument, Repo  # noqa: E501

        :param instrument_type: The instrument_type of this BasketAllOf.  # noqa: E501
        :type: str
        """
        if instrument_type is None:
            raise ValueError("Invalid value for `instrument_type`, must not be `None`")  # noqa: E501
        allowed_values = ["QuotedSecurity", "InterestRateSwap", "FxForward", "Future", "ExoticInstrument", "FxOption", "CreditDefaultSwap", "InterestRateSwaption", "Bond", "EquityOption", "FixedLeg", "FloatingLeg", "BespokeCashFlowsLeg", "Unknown", "TermDeposit", "ContractForDifference", "EquitySwap", "CashPerpetual", "CashSettled", "CdsIndex", "Basket", "FundingLeg", "CrossCurrencySwap", "FxSwap", "ForwardRateAgreement", "SimpleInstrument", "Repo"]  # noqa: E501
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
        if not isinstance(other, BasketAllOf):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
