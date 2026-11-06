# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target robotx_cv::robotx_cv
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${robotx_cv_TARGETS}.
if(robotx_cv_TARGETS AND NOT TARGET robotx_cv::robotx_cv)
  add_library(robotx_cv::robotx_cv INTERFACE IMPORTED)
  set_target_properties(robotx_cv::robotx_cv PROPERTIES
    INTERFACE_LINK_LIBRARIES "${robotx_cv_TARGETS}")
endif()
