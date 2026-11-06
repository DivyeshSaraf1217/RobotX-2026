// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from robotx_cv:msg/Object.idl
// generated code does not contain a copyright notice

#ifndef ROBOTX_CV__MSG__DETAIL__OBJECT__STRUCT_H_
#define ROBOTX_CV__MSG__DETAIL__OBJECT__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'class_name'
// Member 'part'
// Member 'light'
// Member 'colour'
#include "rosidl_runtime_c/string.h"
// Member 'bbox'
#include "vision_msgs/msg/detail/bounding_box2_d__struct.h"
// Member 'position'
#include "geometry_msgs/msg/detail/point__struct.h"

/// Struct defined in msg/Object in the package robotx_cv.
/**
  * One detected object.
 */
typedef struct robotx_cv__msg__Object
{
  rosidl_runtime_c__String class_name;
  float score;
  /// pixels, original image; center.theta = rotation (rad), 0 if upright
  vision_msgs__msg__BoundingBox2D bbox;
  /// Part of another object (dock.py: window / dock_indicator of a dock_face), else -1 and ''.
  /// index in ObjectArray.objects of the whole object
  int32_t parent;
  /// window_left | window_right | indicator
  rosidl_runtime_c__String part;
  /// part seen in the image; false: placed from the layout
  bool found;
  /// LED state, '' if the class has no LED:
  /// red | green | blue (steady), <colour>_flash, seq_<c1>_<c2>, off, unknown
  rosidl_runtime_c__String light;
  /// same light across frames, -1 if no LED
  int32_t light_id;
  /// this frame only: red | green | blue | off, '' if not read / can't tell
  rosidl_runtime_c__String colour;
  /// m, camera to object, NaN if unknown
  float distance;
  /// m, camera optical frame (x right, y down, z forward), NaN if unknown
  geometry_msgs__msg__Point position;
} robotx_cv__msg__Object;

// Struct for a sequence of robotx_cv__msg__Object.
typedef struct robotx_cv__msg__Object__Sequence
{
  robotx_cv__msg__Object * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} robotx_cv__msg__Object__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROBOTX_CV__MSG__DETAIL__OBJECT__STRUCT_H_
