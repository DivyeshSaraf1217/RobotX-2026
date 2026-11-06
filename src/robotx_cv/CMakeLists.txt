cmake_minimum_required(VERSION 3.8)
project(robotx_cv)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(vision_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  msg/Object.msg
  msg/ObjectArray.msg
  msg/Detection.msg
  msg/DetectionArray.msg
  DEPENDENCIES geometry_msgs std_msgs vision_msgs
)

# rosidl already installs the Python package robotx_cv (with robotx_cv.msg); add our modules to it.
install(DIRECTORY ${PROJECT_NAME}/ DESTINATION ${PYTHON_INSTALL_DIR}/${PROJECT_NAME}
  PATTERN __pycache__ EXCLUDE)

install(PROGRAMS ${PROJECT_NAME}/detector.py ${PROJECT_NAME}/task1.py DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME})

ament_export_dependencies(rosidl_default_runtime)
ament_package()
