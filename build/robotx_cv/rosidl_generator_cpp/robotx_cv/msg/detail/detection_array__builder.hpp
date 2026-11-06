// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from robotx_cv:msg/DetectionArray.idl
// generated code does not contain a copyright notice

#ifndef ROBOTX_CV__MSG__DETAIL__DETECTION_ARRAY__BUILDER_HPP_
#define ROBOTX_CV__MSG__DETAIL__DETECTION_ARRAY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "robotx_cv/msg/detail/detection_array__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace robotx_cv
{

namespace msg
{

namespace builder
{

class Init_DetectionArray_detections
{
public:
  explicit Init_DetectionArray_detections(::robotx_cv::msg::DetectionArray & msg)
  : msg_(msg)
  {}
  ::robotx_cv::msg::DetectionArray detections(::robotx_cv::msg::DetectionArray::_detections_type arg)
  {
    msg_.detections = std::move(arg);
    return std::move(msg_);
  }

private:
  ::robotx_cv::msg::DetectionArray msg_;
};

class Init_DetectionArray_header
{
public:
  Init_DetectionArray_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_DetectionArray_detections header(::robotx_cv::msg::DetectionArray::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_DetectionArray_detections(msg_);
  }

private:
  ::robotx_cv::msg::DetectionArray msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::robotx_cv::msg::DetectionArray>()
{
  return robotx_cv::msg::builder::Init_DetectionArray_header();
}

}  // namespace robotx_cv

#endif  // ROBOTX_CV__MSG__DETAIL__DETECTION_ARRAY__BUILDER_HPP_
