// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from robotx_cv:msg/Detection.idl
// generated code does not contain a copyright notice

#ifndef ROBOTX_CV__MSG__DETAIL__DETECTION__BUILDER_HPP_
#define ROBOTX_CV__MSG__DETAIL__DETECTION__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "robotx_cv/msg/detail/detection__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace robotx_cv
{

namespace msg
{

namespace builder
{

class Init_Detection_position
{
public:
  explicit Init_Detection_position(::robotx_cv::msg::Detection & msg)
  : msg_(msg)
  {}
  ::robotx_cv::msg::Detection position(::robotx_cv::msg::Detection::_position_type arg)
  {
    msg_.position = std::move(arg);
    return std::move(msg_);
  }

private:
  ::robotx_cv::msg::Detection msg_;
};

class Init_Detection_distance
{
public:
  explicit Init_Detection_distance(::robotx_cv::msg::Detection & msg)
  : msg_(msg)
  {}
  Init_Detection_position distance(::robotx_cv::msg::Detection::_distance_type arg)
  {
    msg_.distance = std::move(arg);
    return Init_Detection_position(msg_);
  }

private:
  ::robotx_cv::msg::Detection msg_;
};

class Init_Detection_state
{
public:
  explicit Init_Detection_state(::robotx_cv::msg::Detection & msg)
  : msg_(msg)
  {}
  Init_Detection_distance state(::robotx_cv::msg::Detection::_state_type arg)
  {
    msg_.state = std::move(arg);
    return Init_Detection_distance(msg_);
  }

private:
  ::robotx_cv::msg::Detection msg_;
};

class Init_Detection_bbox
{
public:
  explicit Init_Detection_bbox(::robotx_cv::msg::Detection & msg)
  : msg_(msg)
  {}
  Init_Detection_state bbox(::robotx_cv::msg::Detection::_bbox_type arg)
  {
    msg_.bbox = std::move(arg);
    return Init_Detection_state(msg_);
  }

private:
  ::robotx_cv::msg::Detection msg_;
};

class Init_Detection_id
{
public:
  explicit Init_Detection_id(::robotx_cv::msg::Detection & msg)
  : msg_(msg)
  {}
  Init_Detection_bbox id(::robotx_cv::msg::Detection::_id_type arg)
  {
    msg_.id = std::move(arg);
    return Init_Detection_bbox(msg_);
  }

private:
  ::robotx_cv::msg::Detection msg_;
};

class Init_Detection_score
{
public:
  explicit Init_Detection_score(::robotx_cv::msg::Detection & msg)
  : msg_(msg)
  {}
  Init_Detection_id score(::robotx_cv::msg::Detection::_score_type arg)
  {
    msg_.score = std::move(arg);
    return Init_Detection_id(msg_);
  }

private:
  ::robotx_cv::msg::Detection msg_;
};

class Init_Detection_class_name
{
public:
  Init_Detection_class_name()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Detection_score class_name(::robotx_cv::msg::Detection::_class_name_type arg)
  {
    msg_.class_name = std::move(arg);
    return Init_Detection_score(msg_);
  }

private:
  ::robotx_cv::msg::Detection msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::robotx_cv::msg::Detection>()
{
  return robotx_cv::msg::builder::Init_Detection_class_name();
}

}  // namespace robotx_cv

#endif  // ROBOTX_CV__MSG__DETAIL__DETECTION__BUILDER_HPP_
