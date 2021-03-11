# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 0.11.2725
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

class ResultDataKeyRule(object):
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
        'resource_key': 'str',
        'supplier': 'str',
        'data_scope': 'str',
        'document_code': 'str',
        'quote_interval': 'str',
        'as_at': 'datetime'
    }

    attribute_map = {
        'resource_key': 'resourceKey',
        'supplier': 'supplier',
        'data_scope': 'dataScope',
        'document_code': 'documentCode',
        'quote_interval': 'quoteInterval',
        'as_at': 'asAt'
    }

    required_map = {
        'resource_key': 'required',
        'supplier': 'required',
        'data_scope': 'required',
        'document_code': 'required',
        'quote_interval': 'optional',
        'as_at': 'optional'
    }

    def __init__(self, resource_key=None, supplier=None, data_scope=None, document_code=None, quote_interval=None, as_at=None):  # noqa: E501
        """
        ResultDataKeyRule - a model defined in OpenAPI

        :param resource_key:  The result data key that identifies the address pattern that this is a rule for (required)
        :type resource_key: str
        :param supplier:  the result resource supplier (where the data comes from) (required)
        :type supplier: str
        :param data_scope:  which is the scope in which the data should be found (required)
        :type data_scope: str
        :param document_code:  document code that defines which document is desired (required)
        :type document_code: str
        :param quote_interval:  Shorthand for the time interval used to select result data.
        :type quote_interval: str
        :param as_at:  The AsAt predicate specification.
        :type as_at: datetime

        """  # noqa: E501

        self._resource_key = None
        self._supplier = None
        self._data_scope = None
        self._document_code = None
        self._quote_interval = None
        self._as_at = None
        self.discriminator = None

        self.resource_key = resource_key
        self.supplier = supplier
        self.data_scope = data_scope
        self.document_code = document_code
        self.quote_interval = quote_interval
        self.as_at = as_at

    @property
    def resource_key(self):
        """Gets the resource_key of this ResultDataKeyRule.  # noqa: E501

        The result data key that identifies the address pattern that this is a rule for  # noqa: E501

        :return: The resource_key of this ResultDataKeyRule.  # noqa: E501
        :rtype: str
        """
        return self._resource_key

    @resource_key.setter
    def resource_key(self, resource_key):
        """Sets the resource_key of this ResultDataKeyRule.

        The result data key that identifies the address pattern that this is a rule for  # noqa: E501

        :param resource_key: The resource_key of this ResultDataKeyRule.  # noqa: E501
        :type: str
        """
        if resource_key is None:
            raise ValueError("Invalid value for `resource_key`, must not be `None`")  # noqa: E501

        self._resource_key = resource_key

    @property
    def supplier(self):
        """Gets the supplier of this ResultDataKeyRule.  # noqa: E501

        the result resource supplier (where the data comes from)  # noqa: E501

        :return: The supplier of this ResultDataKeyRule.  # noqa: E501
        :rtype: str
        """
        return self._supplier

    @supplier.setter
    def supplier(self, supplier):
        """Sets the supplier of this ResultDataKeyRule.

        the result resource supplier (where the data comes from)  # noqa: E501

        :param supplier: The supplier of this ResultDataKeyRule.  # noqa: E501
        :type: str
        """
        if supplier is None:
            raise ValueError("Invalid value for `supplier`, must not be `None`")  # noqa: E501

        self._supplier = supplier

    @property
    def data_scope(self):
        """Gets the data_scope of this ResultDataKeyRule.  # noqa: E501

        which is the scope in which the data should be found  # noqa: E501

        :return: The data_scope of this ResultDataKeyRule.  # noqa: E501
        :rtype: str
        """
        return self._data_scope

    @data_scope.setter
    def data_scope(self, data_scope):
        """Sets the data_scope of this ResultDataKeyRule.

        which is the scope in which the data should be found  # noqa: E501

        :param data_scope: The data_scope of this ResultDataKeyRule.  # noqa: E501
        :type: str
        """
        if data_scope is None:
            raise ValueError("Invalid value for `data_scope`, must not be `None`")  # noqa: E501

        self._data_scope = data_scope

    @property
    def document_code(self):
        """Gets the document_code of this ResultDataKeyRule.  # noqa: E501

        document code that defines which document is desired  # noqa: E501

        :return: The document_code of this ResultDataKeyRule.  # noqa: E501
        :rtype: str
        """
        return self._document_code

    @document_code.setter
    def document_code(self, document_code):
        """Sets the document_code of this ResultDataKeyRule.

        document code that defines which document is desired  # noqa: E501

        :param document_code: The document_code of this ResultDataKeyRule.  # noqa: E501
        :type: str
        """
        if document_code is None:
            raise ValueError("Invalid value for `document_code`, must not be `None`")  # noqa: E501

        self._document_code = document_code

    @property
    def quote_interval(self):
        """Gets the quote_interval of this ResultDataKeyRule.  # noqa: E501

        Shorthand for the time interval used to select result data.  # noqa: E501

        :return: The quote_interval of this ResultDataKeyRule.  # noqa: E501
        :rtype: str
        """
        return self._quote_interval

    @quote_interval.setter
    def quote_interval(self, quote_interval):
        """Sets the quote_interval of this ResultDataKeyRule.

        Shorthand for the time interval used to select result data.  # noqa: E501

        :param quote_interval: The quote_interval of this ResultDataKeyRule.  # noqa: E501
        :type: str
        """

        self._quote_interval = quote_interval

    @property
    def as_at(self):
        """Gets the as_at of this ResultDataKeyRule.  # noqa: E501

        The AsAt predicate specification.  # noqa: E501

        :return: The as_at of this ResultDataKeyRule.  # noqa: E501
        :rtype: datetime
        """
        return self._as_at

    @as_at.setter
    def as_at(self, as_at):
        """Sets the as_at of this ResultDataKeyRule.

        The AsAt predicate specification.  # noqa: E501

        :param as_at: The as_at of this ResultDataKeyRule.  # noqa: E501
        :type: datetime
        """

        self._as_at = as_at

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
        if not isinstance(other, ResultDataKeyRule):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
