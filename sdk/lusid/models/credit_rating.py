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

class CreditRating(object):
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
        'rating_source': 'str',
        'rating': 'str'
    }

    attribute_map = {
        'rating_source': 'ratingSource',
        'rating': 'rating'
    }

    required_map = {
        'rating_source': 'required',
        'rating': 'required'
    }

    def __init__(self, rating_source=None, rating=None):  # noqa: E501
        """
        CreditRating - a model defined in OpenAPI

        :param rating_source:  Who is providing the rating. This will typically be an agency such as Moody's or Standard and Poor.  The rating would then expected to be consistent with the expected rating scheme from the agency. (required)
        :type rating_source: str
        :param rating:  The credit rating provided by the rating source. This would expected to be consistent with the rating  scheme of that agency/source. (required)
        :type rating: str

        """  # noqa: E501

        self._rating_source = None
        self._rating = None
        self.discriminator = None

        self.rating_source = rating_source
        self.rating = rating

    @property
    def rating_source(self):
        """Gets the rating_source of this CreditRating.  # noqa: E501

        Who is providing the rating. This will typically be an agency such as Moody's or Standard and Poor.  The rating would then expected to be consistent with the expected rating scheme from the agency.  # noqa: E501

        :return: The rating_source of this CreditRating.  # noqa: E501
        :rtype: str
        """
        return self._rating_source

    @rating_source.setter
    def rating_source(self, rating_source):
        """Sets the rating_source of this CreditRating.

        Who is providing the rating. This will typically be an agency such as Moody's or Standard and Poor.  The rating would then expected to be consistent with the expected rating scheme from the agency.  # noqa: E501

        :param rating_source: The rating_source of this CreditRating.  # noqa: E501
        :type: str
        """
        if rating_source is None:
            raise ValueError("Invalid value for `rating_source`, must not be `None`")  # noqa: E501

        self._rating_source = rating_source

    @property
    def rating(self):
        """Gets the rating of this CreditRating.  # noqa: E501

        The credit rating provided by the rating source. This would expected to be consistent with the rating  scheme of that agency/source.  # noqa: E501

        :return: The rating of this CreditRating.  # noqa: E501
        :rtype: str
        """
        return self._rating

    @rating.setter
    def rating(self, rating):
        """Sets the rating of this CreditRating.

        The credit rating provided by the rating source. This would expected to be consistent with the rating  scheme of that agency/source.  # noqa: E501

        :param rating: The rating of this CreditRating.  # noqa: E501
        :type: str
        """
        if rating is None:
            raise ValueError("Invalid value for `rating`, must not be `None`")  # noqa: E501

        self._rating = rating

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
        if not isinstance(other, CreditRating):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
