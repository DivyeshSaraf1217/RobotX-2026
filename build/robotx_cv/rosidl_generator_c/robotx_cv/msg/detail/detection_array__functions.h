// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from robotx_cv:msg/DetectionArray.idl
// generated code does not contain a copyright notice

#ifndef ROBOTX_CV__MSG__DETAIL__DETECTION_ARRAY__FUNCTIONS_H_
#define ROBOTX_CV__MSG__DETAIL__DETECTION_ARRAY__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "robotx_cv/msg/rosidl_generator_c__visibility_control.h"

#include "robotx_cv/msg/detail/detection_array__struct.h"

/// Initialize msg/DetectionArray message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * robotx_cv__msg__DetectionArray
 * )) before or use
 * robotx_cv__msg__DetectionArray__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_robotx_cv
bool
robotx_cv__msg__DetectionArray__init(robotx_cv__msg__DetectionArray * msg);

/// Finalize msg/DetectionArray message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_robotx_cv
void
robotx_cv__msg__DetectionArray__fini(robotx_cv__msg__DetectionArray * msg);

/// Create msg/DetectionArray message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * robotx_cv__msg__DetectionArray__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_robotx_cv
robotx_cv__msg__DetectionArray *
robotx_cv__msg__DetectionArray__create();

/// Destroy msg/DetectionArray message.
/**
 * It calls
 * robotx_cv__msg__DetectionArray__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_robotx_cv
void
robotx_cv__msg__DetectionArray__destroy(robotx_cv__msg__DetectionArray * msg);

/// Check for msg/DetectionArray message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_robotx_cv
bool
robotx_cv__msg__DetectionArray__are_equal(const robotx_cv__msg__DetectionArray * lhs, const robotx_cv__msg__DetectionArray * rhs);

/// Copy a msg/DetectionArray message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_robotx_cv
bool
robotx_cv__msg__DetectionArray__copy(
  const robotx_cv__msg__DetectionArray * input,
  robotx_cv__msg__DetectionArray * output);

/// Initialize array of msg/DetectionArray messages.
/**
 * It allocates the memory for the number of elements and calls
 * robotx_cv__msg__DetectionArray__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_robotx_cv
bool
robotx_cv__msg__DetectionArray__Sequence__init(robotx_cv__msg__DetectionArray__Sequence * array, size_t size);

/// Finalize array of msg/DetectionArray messages.
/**
 * It calls
 * robotx_cv__msg__DetectionArray__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_robotx_cv
void
robotx_cv__msg__DetectionArray__Sequence__fini(robotx_cv__msg__DetectionArray__Sequence * array);

/// Create array of msg/DetectionArray messages.
/**
 * It allocates the memory for the array and calls
 * robotx_cv__msg__DetectionArray__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_robotx_cv
robotx_cv__msg__DetectionArray__Sequence *
robotx_cv__msg__DetectionArray__Sequence__create(size_t size);

/// Destroy array of msg/DetectionArray messages.
/**
 * It calls
 * robotx_cv__msg__DetectionArray__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_robotx_cv
void
robotx_cv__msg__DetectionArray__Sequence__destroy(robotx_cv__msg__DetectionArray__Sequence * array);

/// Check for msg/DetectionArray message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_robotx_cv
bool
robotx_cv__msg__DetectionArray__Sequence__are_equal(const robotx_cv__msg__DetectionArray__Sequence * lhs, const robotx_cv__msg__DetectionArray__Sequence * rhs);

/// Copy an array of msg/DetectionArray messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_robotx_cv
bool
robotx_cv__msg__DetectionArray__Sequence__copy(
  const robotx_cv__msg__DetectionArray__Sequence * input,
  robotx_cv__msg__DetectionArray__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // ROBOTX_CV__MSG__DETAIL__DETECTION_ARRAY__FUNCTIONS_H_
