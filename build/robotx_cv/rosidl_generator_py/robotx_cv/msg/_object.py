# generated from rosidl_generator_py/resource/_idl.py.em
# with input from robotx_cv:msg/Object.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Object(type):
    """Metaclass of message 'Object'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('robotx_cv')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'robotx_cv.msg.Object')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__object
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__object
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__object
            cls._TYPE_SUPPORT = module.type_support_msg__msg__object
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__object

            from geometry_msgs.msg import Point
            if Point.__class__._TYPE_SUPPORT is None:
                Point.__class__.__import_type_support__()

            from vision_msgs.msg import BoundingBox2D
            if BoundingBox2D.__class__._TYPE_SUPPORT is None:
                BoundingBox2D.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Object(metaclass=Metaclass_Object):
    """Message class 'Object'."""

    __slots__ = [
        '_class_name',
        '_score',
        '_bbox',
        '_parent',
        '_part',
        '_found',
        '_light',
        '_light_id',
        '_colour',
        '_distance',
        '_position',
    ]

    _fields_and_field_types = {
        'class_name': 'string',
        'score': 'float',
        'bbox': 'vision_msgs/BoundingBox2D',
        'parent': 'int32',
        'part': 'string',
        'found': 'boolean',
        'light': 'string',
        'light_id': 'int32',
        'colour': 'string',
        'distance': 'float',
        'position': 'geometry_msgs/Point',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['vision_msgs', 'msg'], 'BoundingBox2D'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'Point'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.class_name = kwargs.get('class_name', str())
        self.score = kwargs.get('score', float())
        from vision_msgs.msg import BoundingBox2D
        self.bbox = kwargs.get('bbox', BoundingBox2D())
        self.parent = kwargs.get('parent', int())
        self.part = kwargs.get('part', str())
        self.found = kwargs.get('found', bool())
        self.light = kwargs.get('light', str())
        self.light_id = kwargs.get('light_id', int())
        self.colour = kwargs.get('colour', str())
        self.distance = kwargs.get('distance', float())
        from geometry_msgs.msg import Point
        self.position = kwargs.get('position', Point())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.class_name != other.class_name:
            return False
        if self.score != other.score:
            return False
        if self.bbox != other.bbox:
            return False
        if self.parent != other.parent:
            return False
        if self.part != other.part:
            return False
        if self.found != other.found:
            return False
        if self.light != other.light:
            return False
        if self.light_id != other.light_id:
            return False
        if self.colour != other.colour:
            return False
        if self.distance != other.distance:
            return False
        if self.position != other.position:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def class_name(self):
        """Message field 'class_name'."""
        return self._class_name

    @class_name.setter
    def class_name(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'class_name' field must be of type 'str'"
        self._class_name = value

    @builtins.property
    def score(self):
        """Message field 'score'."""
        return self._score

    @score.setter
    def score(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'score' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'score' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._score = value

    @builtins.property
    def bbox(self):
        """Message field 'bbox'."""
        return self._bbox

    @bbox.setter
    def bbox(self, value):
        if __debug__:
            from vision_msgs.msg import BoundingBox2D
            assert \
                isinstance(value, BoundingBox2D), \
                "The 'bbox' field must be a sub message of type 'BoundingBox2D'"
        self._bbox = value

    @builtins.property
    def parent(self):
        """Message field 'parent'."""
        return self._parent

    @parent.setter
    def parent(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'parent' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'parent' field must be an integer in [-2147483648, 2147483647]"
        self._parent = value

    @builtins.property
    def part(self):
        """Message field 'part'."""
        return self._part

    @part.setter
    def part(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'part' field must be of type 'str'"
        self._part = value

    @builtins.property
    def found(self):
        """Message field 'found'."""
        return self._found

    @found.setter
    def found(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'found' field must be of type 'bool'"
        self._found = value

    @builtins.property
    def light(self):
        """Message field 'light'."""
        return self._light

    @light.setter
    def light(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'light' field must be of type 'str'"
        self._light = value

    @builtins.property
    def light_id(self):
        """Message field 'light_id'."""
        return self._light_id

    @light_id.setter
    def light_id(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'light_id' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'light_id' field must be an integer in [-2147483648, 2147483647]"
        self._light_id = value

    @builtins.property
    def colour(self):
        """Message field 'colour'."""
        return self._colour

    @colour.setter
    def colour(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'colour' field must be of type 'str'"
        self._colour = value

    @builtins.property
    def distance(self):
        """Message field 'distance'."""
        return self._distance

    @distance.setter
    def distance(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'distance' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'distance' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._distance = value

    @builtins.property
    def position(self):
        """Message field 'position'."""
        return self._position

    @position.setter
    def position(self, value):
        if __debug__:
            from geometry_msgs.msg import Point
            assert \
                isinstance(value, Point), \
                "The 'position' field must be a sub message of type 'Point'"
        self._position = value
