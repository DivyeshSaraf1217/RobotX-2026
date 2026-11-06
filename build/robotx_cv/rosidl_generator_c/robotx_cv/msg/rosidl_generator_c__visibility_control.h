// generated from rosidl_generator_c/resource/rosidl_generator_c__visibility_control.h.in
// generated code does not contain a copyright notice

#ifndef ROBOTX_CV__MSG__ROSIDL_GENERATOR_C__VISIBILITY_CONTROL_H_
#define ROBOTX_CV__MSG__ROSIDL_GENERATOR_C__VISIBILITY_CONTROL_H_

#ifdef __cplusplus
extern "C"
{
#endif

// This logic was borrowed (then namespaced) from the examples on the gcc wiki:
//     https://gcc.gnu.org/wiki/Visibility

#if defined _WIN32 || defined __CYGWIN__
  #ifdef __GNUC__
    #define ROSIDL_GENERATOR_C_EXPORT_robotx_cv __attribute__ ((dllexport))
    #define ROSIDL_GENERATOR_C_IMPORT_robotx_cv __attribute__ ((dllimport))
  #else
    #define ROSIDL_GENERATOR_C_EXPORT_robotx_cv __declspec(dllexport)
    #define ROSIDL_GENERATOR_C_IMPORT_robotx_cv __declspec(dllimport)
  #endif
  #ifdef ROSIDL_GENERATOR_C_BUILDING_DLL_robotx_cv
    #define ROSIDL_GENERATOR_C_PUBLIC_robotx_cv ROSIDL_GENERATOR_C_EXPORT_robotx_cv
  #else
    #define ROSIDL_GENERATOR_C_PUBLIC_robotx_cv ROSIDL_GENERATOR_C_IMPORT_robotx_cv
  #endif
#else
  #define ROSIDL_GENERATOR_C_EXPORT_robotx_cv __attribute__ ((visibility("default")))
  #define ROSIDL_GENERATOR_C_IMPORT_robotx_cv
  #if __GNUC__ >= 4
    #define ROSIDL_GENERATOR_C_PUBLIC_robotx_cv __attribute__ ((visibility("default")))
  #else
    #define ROSIDL_GENERATOR_C_PUBLIC_robotx_cv
  #endif
#endif

#ifdef __cplusplus
}
#endif

#endif  // ROBOTX_CV__MSG__ROSIDL_GENERATOR_C__VISIBILITY_CONTROL_H_
