// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from robotx_cv:msg/DetectionArray.idl
// generated code does not contain a copyright notice

#ifndef ROBOTX_CV__MSG__DETAIL__DETECTION_ARRAY__STRUCT_H_
#define ROBOTX_CV__MSG__DETAIL__DETECTION_ARRAY__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'detections'
#include "robotx_cv/msg/detail/detection__struct.h"

/// Struct defined in msg/DetectionArray in the package robotx_cv.
typedef struct robotx_cv__msg__DetectionArray
{
  /// same stamp and frame_id as the source image
  std_msgs__msg__Header header;
  robotx_cv__msg__Detection__Sequence detections;
} robotx_cv__msg__DetectionArray;

// Struct for a sequence of robotx_cv__msg__DetectionArray.
typedef struct robotx_cv__msg__DetectionArray__Sequence
{
  robotx_cv__msg__DetectionArray * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} robotx_cv__msg__DetectionArray__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROBOTX_CV__MSG__DETAIL__DETECTION_ARRAY__STRUCT_H_
