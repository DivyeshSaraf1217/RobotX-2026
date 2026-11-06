// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__rosidl_typesupport_fastrtps_cpp.hpp.em
// with input from robotx_cv:msg/ObjectArray.idl
// generated code does not contain a copyright notice

#ifndef ROBOTX_CV__MSG__DETAIL__OBJECT_ARRAY__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
#define ROBOTX_CV__MSG__DETAIL__OBJECT_ARRAY__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_

#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "robotx_cv/msg/rosidl_typesupport_fastrtps_cpp__visibility_control.h"
#include "robotx_cv/msg/detail/object_array__struct.hpp"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

#include "fastcdr/Cdr.h"

namespace robotx_cv
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_robotx_cv
cdr_serialize(
  const robotx_cv::msg::ObjectArray & ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_robotx_cv
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  robotx_cv::msg::ObjectArray & ros_message);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_robotx_cv
get_serialized_size(
  const robotx_cv::msg::ObjectArray & ros_message,
  size_t current_alignment);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_robotx_cv
max_serialized_size_ObjectArray(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace robotx_cv

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_robotx_cv
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, robotx_cv, msg, ObjectArray)();

#ifdef __cplusplus
}
#endif

#endif  // ROBOTX_CV__MSG__DETAIL__OBJECT_ARRAY__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
