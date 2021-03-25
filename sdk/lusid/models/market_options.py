# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 0.11.2798
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

class MarketOptions(object):
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
        'default_supplier': 'str',
        'default_instrument_code_type': 'str',
        'default_scope': 'str',
        'attempt_to_infer_missing_fx': 'bool'
    }

    attribute_map = {
        'default_supplier': 'defaultSupplier',
        'default_instrument_code_type': 'defaultInstrumentCodeType',
        'default_scope': 'defaultScope',
        'attempt_to_infer_missing_fx': 'attemptToInferMissingFx'
    }

    required_map = {
        'default_supplier': 'optional',
        'default_instrument_code_type': 'optional',
        'default_scope': 'optional',
        'attempt_to_infer_missing_fx': 'optional'
    }

    def __init__(self, default_supplier=None, default_instrument_code_type=None, default_scope=None, attempt_to_infer_missing_fx=None):  # noqa: E501
        """
        MarketOptions - a model defined in OpenAPI

        :param default_supplier:  The default supplier of data. This controls which 'dialect' is used to find particular market data. e.g. one supplier might address data by RIC, another by PermId
        :type default_supplier: str
        :param default_instrument_code_type:  When instrument quotes are searched for, what identifier should be used by default
        :type default_instrument_code_type: str
        :param default_scope:  For default rules, which scope should data be searched for in
        :type default_scope: str
        :param attempt_to_infer_missing_fx:  if true will calculate a missing Fx pair (e.g. THBJPY) from the inverse JPYTHB or from standardised pairs against USD, e.g. THBUSD and JPYUSD
        :type attempt_to_infer_missing_fx: bool

        """  # noqa: E501

        self._default_supplier = None
        self._default_instrument_code_type = None
        self._default_scope = None
        self._attempt_to_infer_missing_fx = None
        self.discriminator = None

        self.default_supplier = default_supplier
        self.default_instrument_code_type = default_instrument_code_type
        self.default_scope = default_scope
        if attempt_to_infer_missing_fx is not None:
            self.attempt_to_infer_missing_fx = attempt_to_infer_missing_fx

    @property
    def default_supplier(self):
        """Gets the default_supplier of this MarketOptions.  # noqa: E501

        The default supplier of data. This controls which 'dialect' is used to find particular market data. e.g. one supplier might address data by RIC, another by PermId  # noqa: E501

        :return: The default_supplier of this MarketOptions.  # noqa: E501
        :rtype: str
        """
        return self._default_supplier

    @default_supplier.setter
    def default_supplier(self, default_supplier):
        """Sets the default_supplier of this MarketOptions.

        The default supplier of data. This controls which 'dialect' is used to find particular market data. e.g. one supplier might address data by RIC, another by PermId  # noqa: E501

        :param default_supplier: The default_supplier of this MarketOptions.  # noqa: E501
        :type: str
        """

        self._default_supplier = default_supplier

    @property
    def default_instrument_code_type(self):
        """Gets the default_instrument_code_type of this MarketOptions.  # noqa: E501

        When instrument quotes are searched for, what identifier should be used by default  # noqa: E501

        :return: The default_instrument_code_type of this MarketOptions.  # noqa: E501
        :rtype: str
        """
        return self._default_instrument_code_type

    @default_instrument_code_type.setter
    def default_instrument_code_type(self, default_instrument_code_type):
        """Sets the default_instrument_code_type of this MarketOptions.

        When instrument quotes are searched for, what identifier should be used by default  # noqa: E501

        :param default_instrument_code_type: The default_instrument_code_type of this MarketOptions.  # noqa: E501
        :type: str
        """

        self._default_instrument_code_type = default_instrument_code_type

    @property
    def default_scope(self):
        """Gets the default_scope of this MarketOptions.  # noqa: E501

        For default rules, which scope should data be searched for in  # noqa: E501

        :return: The default_scope of this MarketOptions.  # noqa: E501
        :rtype: str
        """
        return self._default_scope

    @default_scope.setter
    def default_scope(self, default_scope):
        """Sets the default_scope of this MarketOptions.

        For default rules, which scope should data be searched for in  # noqa: E501

        :param default_scope: The default_scope of this MarketOptions.  # noqa: E501
        :type: str
        """

        self._default_scope = default_scope

    @property
    def attempt_to_infer_missing_fx(self):
        """Gets the attempt_to_infer_missing_fx of this MarketOptions.  # noqa: E501

        if true will calculate a missing Fx pair (e.g. THBJPY) from the inverse JPYTHB or from standardised pairs against USD, e.g. THBUSD and JPYUSD  # noqa: E501

        :return: The attempt_to_infer_missing_fx of this MarketOptions.  # noqa: E501
        :rtype: bool
        """
        return self._attempt_to_infer_missing_fx

    @attempt_to_infer_missing_fx.setter
    def attempt_to_infer_missing_fx(self, attempt_to_infer_missing_fx):
        """Sets the attempt_to_infer_missing_fx of this MarketOptions.

        if true will calculate a missing Fx pair (e.g. THBJPY) from the inverse JPYTHB or from standardised pairs against USD, e.g. THBUSD and JPYUSD  # noqa: E501

        :param attempt_to_infer_missing_fx: The attempt_to_infer_missing_fx of this MarketOptions.  # noqa: E501
        :type: bool
        """

        self._attempt_to_infer_missing_fx = attempt_to_infer_missing_fx

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
        if not isinstance(other, MarketOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
