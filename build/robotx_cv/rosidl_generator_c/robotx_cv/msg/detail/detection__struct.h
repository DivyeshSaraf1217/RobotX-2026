// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from robotx_cv:msg/Detection.idl
// generated code does not contain a copyright notice

#ifndef ROBOTX_CV__MSG__DETAIL__DETECTION__STRUCT_H_
#define ROBOTX_CV__MSG__DETAIL__DETECTION__STRUCT_H_

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
// Member 'state'
#include "rosidl_runtime_c/string.h"
// Member 'bbox'
#include "vision_msgs/msg/detail/bounding_box2_d__struct.h"
// Member 'position'
#include "geometry_msgs/msg/detail/point__struct.h"

/// Struct defined in msg/Detection in the package robotx_cv.
/**
  * One detected object, any vehicle / task.
 */
typedef struct robotx_cv__msg__Detection
{
  /// model class (light_beacon, robobuoy, ...)
  rosidl_runtime_c__String class_name;
  /// model confidence, this frame
  float score;
  /// same object across frames, -1 if not tracked
  int32_t id;
  /// pixels, original image; center.theta = rotation (rad), 0 if upright
  vision_msgs__msg__BoundingBox2D bbox;
  /// Confirmed state of a tracked object, '' if its class has none. Task 1 robobuoy, its light beacon:
  /// off | flashing_red | flashing_green | flashing_blue | solid_blue | unknown (not confirmed yet)
  rosidl_runtime_c__String state;
  /// m, camera to object, NaN if unknown
  float distance;
  /// m, from the depth image at the box centroid, ROS body axes (x forward, y left, z up; task1 ros_frame:=false: optical x right, y down, z forward), NaN if unknown
  geometry_msgs__msg__Point position;
} robotx_cv__msg__Detection;

// Struct for a sequence of robotx_cv__msg__Detection.
typedef struct robotx_cv__msg__Detection__Sequence
{
  robotx_cv__msg__Detection * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} robotx_cv__msg__Detection__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROBOTX_CV__MSG__DETAIL__DETECTION__STRUCT_H_
