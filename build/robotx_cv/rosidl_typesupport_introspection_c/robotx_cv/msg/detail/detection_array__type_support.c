// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from robotx_cv:msg/DetectionArray.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "robotx_cv/msg/detail/detection_array__rosidl_typesupport_introspection_c.h"
#include "robotx_cv/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "robotx_cv/msg/detail/detection_array__functions.h"
#include "robotx_cv/msg/detail/detection_array__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `detections`
#include "robotx_cv/msg/detection.h"
// Member `detections`
#include "robotx_cv/msg/detail/detection__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__DetectionArray_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  robotx_cv__msg__DetectionArray__init(message_memory);
}

void robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__DetectionArray_fini_function(void * message_memory)
{
  robotx_cv__msg__DetectionArray__fini(message_memory);
}

size_t robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__size_function__DetectionArray__detections(
  const void * untyped_member)
{
  const robotx_cv__msg__Detection__Sequence * member =
    (const robotx_cv__msg__Detection__Sequence *)(untyped_member);
  return member->size;
}

const void * robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__get_const_function__DetectionArray__detections(
  const void * untyped_member, size_t index)
{
  const robotx_cv__msg__Detection__Sequence * member =
    (const robotx_cv__msg__Detection__Sequence *)(untyped_member);
  return &member->data[index];
}

void * robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__get_function__DetectionArray__detections(
  void * untyped_member, size_t index)
{
  robotx_cv__msg__Detection__Sequence * member =
    (robotx_cv__msg__Detection__Sequence *)(untyped_member);
  return &member->data[index];
}

void robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__fetch_function__DetectionArray__detections(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const robotx_cv__msg__Detection * item =
    ((const robotx_cv__msg__Detection *)
    robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__get_const_function__DetectionArray__detections(untyped_member, index));
  robotx_cv__msg__Detection * value =
    (robotx_cv__msg__Detection *)(untyped_value);
  *value = *item;
}

void robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__assign_function__DetectionArray__detections(
  void * untyped_member, size_t index, const void * untyped_value)
{
  robotx_cv__msg__Detection * item =
    ((robotx_cv__msg__Detection *)
    robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__get_function__DetectionArray__detections(untyped_member, index));
  const robotx_cv__msg__Detection * value =
    (const robotx_cv__msg__Detection *)(untyped_value);
  *item = *value;
}

bool robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__resize_function__DetectionArray__detections(
  void * untyped_member, size_t size)
{
  robotx_cv__msg__Detection__Sequence * member =
    (robotx_cv__msg__Detection__Sequence *)(untyped_member);
  robotx_cv__msg__Detection__Sequence__fini(member);
  return robotx_cv__msg__Detection__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__DetectionArray_message_member_array[2] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(robotx_cv__msg__DetectionArray, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "detections",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(robotx_cv__msg__DetectionArray, detections),  // bytes offset in struct
    NULL,  // default value
    robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__size_function__DetectionArray__detections,  // size() function pointer
    robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__get_const_function__DetectionArray__detections,  // get_const(index) function pointer
    robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__get_function__DetectionArray__detections,  // get(index) function pointer
    robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__fetch_function__DetectionArray__detections,  // fetch(index, &value) function pointer
    robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__assign_function__DetectionArray__detections,  // assign(index, value) function pointer
    robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__resize_function__DetectionArray__detections  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__DetectionArray_message_members = {
  "robotx_cv__msg",  // message namespace
  "DetectionArray",  // message name
  2,  // number of fields
  sizeof(robotx_cv__msg__DetectionArray),
  robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__DetectionArray_message_member_array,  // message members
  robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__DetectionArray_init_function,  // function to initialize message memory (memory has to be allocated)
  robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__DetectionArray_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__DetectionArray_message_type_support_handle = {
  0,
  &robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__DetectionArray_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_robotx_cv
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, robotx_cv, msg, DetectionArray)() {
  robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__DetectionArray_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__DetectionArray_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, robotx_cv, msg, Detection)();
  if (!robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__DetectionArray_message_type_support_handle.typesupport_identifier) {
    robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__DetectionArray_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &robotx_cv__msg__DetectionArray__rosidl_typesupport_introspection_c__DetectionArray_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
