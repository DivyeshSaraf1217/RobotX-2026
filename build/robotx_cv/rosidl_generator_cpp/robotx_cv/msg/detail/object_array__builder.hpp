// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from robotx_cv:msg/ObjectArray.idl
// generated code does not contain a copyright notice

#ifndef ROBOTX_CV__MSG__DETAIL__OBJECT_ARRAY__BUILDER_HPP_
#define ROBOTX_CV__MSG__DETAIL__OBJECT_ARRAY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "robotx_cv/msg/detail/object_array__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace robotx_cv
{

namespace msg
{

namespace builder
{

class Init_ObjectArray_objects
{
public:
  explicit Init_ObjectArray_objects(::robotx_cv::msg::ObjectArray & msg)
  : msg_(msg)
  {}
  ::robotx_cv::msg::ObjectArray objects(::robotx_cv::msg::ObjectArray::_objects_type arg)
  {
    msg_.objects = std::move(arg);
    return std::move(msg_);
  }

private:
  ::robotx_cv::msg::ObjectArray msg_;
};

class Init_ObjectArray_header
{
public:
  Init_ObjectArray_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ObjectArray_objects header(::robotx_cv::msg::ObjectArray::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_ObjectArray_objects(msg_);
  }

private:
  ::robotx_cv::msg::ObjectArray msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::robotx_cv::msg::ObjectArray>()
{
  return robotx_cv::msg::builder::Init_ObjectArray_header();
}

}  // namespace robotx_cv

#endif  // ROBOTX_CV__MSG__DETAIL__OBJECT_ARRAY__BUILDER_HPP_
