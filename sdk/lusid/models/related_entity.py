# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 0.11.3002
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

class RelatedEntity(object):
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
        'entity_type': 'str',
        'entity_id': 'dict(str, str)',
        'display_name': 'str',
        'properties': 'dict(str, ModelProperty)'
    }

    attribute_map = {
        'entity_type': 'entityType',
        'entity_id': 'entityId',
        'display_name': 'displayName',
        'properties': 'properties'
    }

    required_map = {
        'entity_type': 'required',
        'entity_id': 'required',
        'display_name': 'required',
        'properties': 'optional'
    }

    def __init__(self, entity_type=None, entity_id=None, display_name=None, properties=None):  # noqa: E501
        """
        RelatedEntity - a model defined in OpenAPI

        :param entity_type:  The type of the entity. (required)
        :type entity_type: str
        :param entity_id:  The identifier of the other related entity in the relationship. It contains 'scope' and 'code' as keys for identifiers of a Portfolio or Portfolio Group, or 'idTypeScope', 'idTypeCode', 'code' as keys for identifiers of a Person or Legal Entity. (required)
        :type entity_id: dict(str, str)
        :param display_name:  The display name of the entity. (required)
        :type display_name: str
        :param properties:  The properties of the entity. This field is empty until further notice.
        :type properties: dict[str, lusid.ModelProperty]

        """  # noqa: E501

        self._entity_type = None
        self._entity_id = None
        self._display_name = None
        self._properties = None
        self.discriminator = None

        self.entity_type = entity_type
        self.entity_id = entity_id
        self.display_name = display_name
        self.properties = properties

    @property
    def entity_type(self):
        """Gets the entity_type of this RelatedEntity.  # noqa: E501

        The type of the entity.  # noqa: E501

        :return: The entity_type of this RelatedEntity.  # noqa: E501
        :rtype: str
        """
        return self._entity_type

    @entity_type.setter
    def entity_type(self, entity_type):
        """Sets the entity_type of this RelatedEntity.

        The type of the entity.  # noqa: E501

        :param entity_type: The entity_type of this RelatedEntity.  # noqa: E501
        :type: str
        """
        if entity_type is None:
            raise ValueError("Invalid value for `entity_type`, must not be `None`")  # noqa: E501

        self._entity_type = entity_type

    @property
    def entity_id(self):
        """Gets the entity_id of this RelatedEntity.  # noqa: E501

        The identifier of the other related entity in the relationship. It contains 'scope' and 'code' as keys for identifiers of a Portfolio or Portfolio Group, or 'idTypeScope', 'idTypeCode', 'code' as keys for identifiers of a Person or Legal Entity.  # noqa: E501

        :return: The entity_id of this RelatedEntity.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._entity_id

    @entity_id.setter
    def entity_id(self, entity_id):
        """Sets the entity_id of this RelatedEntity.

        The identifier of the other related entity in the relationship. It contains 'scope' and 'code' as keys for identifiers of a Portfolio or Portfolio Group, or 'idTypeScope', 'idTypeCode', 'code' as keys for identifiers of a Person or Legal Entity.  # noqa: E501

        :param entity_id: The entity_id of this RelatedEntity.  # noqa: E501
        :type: dict(str, str)
        """
        if entity_id is None:
            raise ValueError("Invalid value for `entity_id`, must not be `None`")  # noqa: E501

        self._entity_id = entity_id

    @property
    def display_name(self):
        """Gets the display_name of this RelatedEntity.  # noqa: E501

        The display name of the entity.  # noqa: E501

        :return: The display_name of this RelatedEntity.  # noqa: E501
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """Sets the display_name of this RelatedEntity.

        The display name of the entity.  # noqa: E501

        :param display_name: The display_name of this RelatedEntity.  # noqa: E501
        :type: str
        """
        if display_name is None:
            raise ValueError("Invalid value for `display_name`, must not be `None`")  # noqa: E501

        self._display_name = display_name

    @property
    def properties(self):
        """Gets the properties of this RelatedEntity.  # noqa: E501

        The properties of the entity. This field is empty until further notice.  # noqa: E501

        :return: The properties of this RelatedEntity.  # noqa: E501
        :rtype: dict(str, ModelProperty)
        """
        return self._properties

    @properties.setter
    def properties(self, properties):
        """Sets the properties of this RelatedEntity.

        The properties of the entity. This field is empty until further notice.  # noqa: E501

        :param properties: The properties of this RelatedEntity.  # noqa: E501
        :type: dict(str, ModelProperty)
        """

        self._properties = properties

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
        if not isinstance(other, RelatedEntity):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
