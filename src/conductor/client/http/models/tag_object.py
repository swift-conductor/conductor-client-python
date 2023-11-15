# coding: utf-8

import pprint
import re  # noqa: F401

import six

class TagObject(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'key': 'str',
        'type': 'str',
        'value': 'object'
    }

    attribute_map = {
        'key': 'key',
        'type': 'type',
        'value': 'value'
    }

    def __init__(self, key=None, type=None, value=None):  # noqa: E501
        """TagObject - a model defined in Swagger"""  # noqa: E501
        self._key = None
        self._type = None
        self._value = None
        self.discriminator = None
        if key is not None:
            self.key = key
        if type is not None:
            self.type = type
        if value is not None:
            self.value = value

    @property
    def key(self):
        """Gets the key of this TagObject.  # noqa: E501


        :return: The key of this TagObject.  # noqa: E501
        :rtype: str
        """
        return self._key

    @key.setter
    def key(self, key):
        """Sets the key of this TagObject.


        :param key: The key of this TagObject.  # noqa: E501
        :type: str
        """

        self._key = key

    @property
    def type(self):
        """Gets the type of this TagObject.  # noqa: E501


        :return: The type of this TagObject.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this TagObject.


        :param type: The type of this TagObject.  # noqa: E501
        :type: str
        """
        allowed_values = ["METADATA", "RATE_LIMIT"]  # noqa: E501
        if type not in allowed_values:
            raise ValueError(
                "Invalid value for `type` ({0}), must be one of {1}"  # noqa: E501
                .format(type, allowed_values)
            )

        self._type = type

    @property
    def value(self):
        """Gets the value of this TagObject.  # noqa: E501


        :return: The value of this TagObject.  # noqa: E501
        :rtype: object
        """
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value of this TagObject.


        :param value: The value of this TagObject.  # noqa: E501
        :type: object
        """

        self._value = value

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
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
        if issubclass(TagObject, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, TagObject):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
