// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from robotx_cv:msg/Object.idl
// generated code does not contain a copyright notice
#include "robotx_cv/msg/detail/object__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `class_name`
// Member `part`
// Member `light`
// Member `colour`
#include "rosidl_runtime_c/string_functions.h"
// Member `bbox`
#include "vision_msgs/msg/detail/bounding_box2_d__functions.h"
// Member `position`
#include "geometry_msgs/msg/detail/point__functions.h"

bool
robotx_cv__msg__Object__init(robotx_cv__msg__Object * msg)
{
  if (!msg) {
    return false;
  }
  // class_name
  if (!rosidl_runtime_c__String__init(&msg->class_name)) {
    robotx_cv__msg__Object__fini(msg);
    return false;
  }
  // score
  // bbox
  if (!vision_msgs__msg__BoundingBox2D__init(&msg->bbox)) {
    robotx_cv__msg__Object__fini(msg);
    return false;
  }
  // parent
  // part
  if (!rosidl_runtime_c__String__init(&msg->part)) {
    robotx_cv__msg__Object__fini(msg);
    return false;
  }
  // found
  // light
  if (!rosidl_runtime_c__String__init(&msg->light)) {
    robotx_cv__msg__Object__fini(msg);
    return false;
  }
  // light_id
  // colour
  if (!rosidl_runtime_c__String__init(&msg->colour)) {
    robotx_cv__msg__Object__fini(msg);
    return false;
  }
  // distance
  // position
  if (!geometry_msgs__msg__Point__init(&msg->position)) {
    robotx_cv__msg__Object__fini(msg);
    return false;
  }
  return true;
}

void
robotx_cv__msg__Object__fini(robotx_cv__msg__Object * msg)
{
  if (!msg) {
    return;
  }
  // class_name
  rosidl_runtime_c__String__fini(&msg->class_name);
  // score
  // bbox
  vision_msgs__msg__BoundingBox2D__fini(&msg->bbox);
  // parent
  // part
  rosidl_runtime_c__String__fini(&msg->part);
  // found
  // light
  rosidl_runtime_c__String__fini(&msg->light);
  // light_id
  // colour
  rosidl_runtime_c__String__fini(&msg->colour);
  // distance
  // position
  geometry_msgs__msg__Point__fini(&msg->position);
}

bool
robotx_cv__msg__Object__are_equal(const robotx_cv__msg__Object * lhs, const robotx_cv__msg__Object * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // class_name
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->class_name), &(rhs->class_name)))
  {
    return false;
  }
  // score
  if (lhs->score != rhs->score) {
    return false;
  }
  // bbox
  if (!vision_msgs__msg__BoundingBox2D__are_equal(
      &(lhs->bbox), &(rhs->bbox)))
  {
    return false;
  }
  // parent
  if (lhs->parent != rhs->parent) {
    return false;
  }
  // part
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->part), &(rhs->part)))
  {
    return false;
  }
  // found
  if (lhs->found != rhs->found) {
    return false;
  }
  // light
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->light), &(rhs->light)))
  {
    return false;
  }
  // light_id
  if (lhs->light_id != rhs->light_id) {
    return false;
  }
  // colour
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->colour), &(rhs->colour)))
  {
    return false;
  }
  // distance
  if (lhs->distance != rhs->distance) {
    return false;
  }
  // position
  if (!geometry_msgs__msg__Point__are_equal(
      &(lhs->position), &(rhs->position)))
  {
    return false;
  }
  return true;
}

bool
robotx_cv__msg__Object__copy(
  const robotx_cv__msg__Object * input,
  robotx_cv__msg__Object * output)
{
  if (!input || !output) {
    return false;
  }
  // class_name
  if (!rosidl_runtime_c__String__copy(
      &(input->class_name), &(output->class_name)))
  {
    return false;
  }
  // score
  output->score = input->score;
  // bbox
  if (!vision_msgs__msg__BoundingBox2D__copy(
      &(input->bbox), &(output->bbox)))
  {
    return false;
  }
  // parent
  output->parent = input->parent;
  // part
  if (!rosidl_runtime_c__String__copy(
      &(input->part), &(output->part)))
  {
    return false;
  }
  // found
  output->found = input->found;
  // light
  if (!rosidl_runtime_c__String__copy(
      &(input->light), &(output->light)))
  {
    return false;
  }
  // light_id
  output->light_id = input->light_id;
  // colour
  if (!rosidl_runtime_c__String__copy(
      &(input->colour), &(output->colour)))
  {
    return false;
  }
  // distance
  output->distance = input->distance;
  // position
  if (!geometry_msgs__msg__Point__copy(
      &(input->position), &(output->position)))
  {
    return false;
  }
  return true;
}

robotx_cv__msg__Object *
robotx_cv__msg__Object__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  robotx_cv__msg__Object * msg = (robotx_cv__msg__Object *)allocator.allocate(sizeof(robotx_cv__msg__Object), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(robotx_cv__msg__Object));
  bool success = robotx_cv__msg__Object__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
robotx_cv__msg__Object__destroy(robotx_cv__msg__Object * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    robotx_cv__msg__Object__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
robotx_cv__msg__Object__Sequence__init(robotx_cv__msg__Object__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  robotx_cv__msg__Object * data = NULL;

  if (size) {
    data = (robotx_cv__msg__Object *)allocator.zero_allocate(size, sizeof(robotx_cv__msg__Object), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = robotx_cv__msg__Object__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        robotx_cv__msg__Object__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
robotx_cv__msg__Object__Sequence__fini(robotx_cv__msg__Object__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      robotx_cv__msg__Object__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

robotx_cv__msg__Object__Sequence *
robotx_cv__msg__Object__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  robotx_cv__msg__Object__Sequence * array = (robotx_cv__msg__Object__Sequence *)allocator.allocate(sizeof(robotx_cv__msg__Object__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = robotx_cv__msg__Object__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
robotx_cv__msg__Object__Sequence__destroy(robotx_cv__msg__Object__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    robotx_cv__msg__Object__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
robotx_cv__msg__Object__Sequence__are_equal(const robotx_cv__msg__Object__Sequence * lhs, const robotx_cv__msg__Object__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!robotx_cv__msg__Object__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
robotx_cv__msg__Object__Sequence__copy(
  const robotx_cv__msg__Object__Sequence * input,
  robotx_cv__msg__Object__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(robotx_cv__msg__Object);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    robotx_cv__msg__Object * data =
      (robotx_cv__msg__Object *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!robotx_cv__msg__Object__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          robotx_cv__msg__Object__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!robotx_cv__msg__Object__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
