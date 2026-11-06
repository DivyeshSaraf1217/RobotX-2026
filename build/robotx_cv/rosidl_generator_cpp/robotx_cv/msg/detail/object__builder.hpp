// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from robotx_cv:msg/Object.idl
// generated code does not contain a copyright notice

#ifndef ROBOTX_CV__MSG__DETAIL__OBJECT__BUILDER_HPP_
#define ROBOTX_CV__MSG__DETAIL__OBJECT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "robotx_cv/msg/detail/object__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace robotx_cv
{

namespace msg
{

namespace builder
{

class Init_Object_position
{
public:
  explicit Init_Object_position(::robotx_cv::msg::Object & msg)
  : msg_(msg)
  {}
  ::robotx_cv::msg::Object position(::robotx_cv::msg::Object::_position_type arg)
  {
    msg_.position = std::move(arg);
    return std::move(msg_);
  }

private:
  ::robotx_cv::msg::Object msg_;
};

class Init_Object_distance
{
public:
  explicit Init_Object_distance(::robotx_cv::msg::Object & msg)
  : msg_(msg)
  {}
  Init_Object_position distance(::robotx_cv::msg::Object::_distance_type arg)
  {
    msg_.distance = std::move(arg);
    return Init_Object_position(msg_);
  }

private:
  ::robotx_cv::msg::Object msg_;
};

class Init_Object_colour
{
public:
  explicit Init_Object_colour(::robotx_cv::msg::Object & msg)
  : msg_(msg)
  {}
  Init_Object_distance colour(::robotx_cv::msg::Object::_colour_type arg)
  {
    msg_.colour = std::move(arg);
    return Init_Object_distance(msg_);
  }

private:
  ::robotx_cv::msg::Object msg_;
};

class Init_Object_light_id
{
public:
  explicit Init_Object_light_id(::robotx_cv::msg::Object & msg)
  : msg_(msg)
  {}
  Init_Object_colour light_id(::robotx_cv::msg::Object::_light_id_type arg)
  {
    msg_.light_id = std::move(arg);
    return Init_Object_colour(msg_);
  }

private:
  ::robotx_cv::msg::Object msg_;
};

class Init_Object_light
{
public:
  explicit Init_Object_light(::robotx_cv::msg::Object & msg)
  : msg_(msg)
  {}
  Init_Object_light_id light(::robotx_cv::msg::Object::_light_type arg)
  {
    msg_.light = std::move(arg);
    return Init_Object_light_id(msg_);
  }

private:
  ::robotx_cv::msg::Object msg_;
};

class Init_Object_found
{
public:
  explicit Init_Object_found(::robotx_cv::msg::Object & msg)
  : msg_(msg)
  {}
  Init_Object_light found(::robotx_cv::msg::Object::_found_type arg)
  {
    msg_.found = std::move(arg);
    return Init_Object_light(msg_);
  }

private:
  ::robotx_cv::msg::Object msg_;
};

class Init_Object_part
{
public:
  explicit Init_Object_part(::robotx_cv::msg::Object & msg)
  : msg_(msg)
  {}
  Init_Object_found part(::robotx_cv::msg::Object::_part_type arg)
  {
    msg_.part = std::move(arg);
    return Init_Object_found(msg_);
  }

private:
  ::robotx_cv::msg::Object msg_;
};

class Init_Object_parent
{
public:
  explicit Init_Object_parent(::robotx_cv::msg::Object & msg)
  : msg_(msg)
  {}
  Init_Object_part parent(::robotx_cv::msg::Object::_parent_type arg)
  {
    msg_.parent = std::move(arg);
    return Init_Object_part(msg_);
  }

private:
  ::robotx_cv::msg::Object msg_;
};

class Init_Object_bbox
{
public:
  explicit Init_Object_bbox(::robotx_cv::msg::Object & msg)
  : msg_(msg)
  {}
  Init_Object_parent bbox(::robotx_cv::msg::Object::_bbox_type arg)
  {
    msg_.bbox = std::move(arg);
    return Init_Object_parent(msg_);
  }

private:
  ::robotx_cv::msg::Object msg_;
};

class Init_Object_score
{
public:
  explicit Init_Object_score(::robotx_cv::msg::Object & msg)
  : msg_(msg)
  {}
  Init_Object_bbox score(::robotx_cv::msg::Object::_score_type arg)
  {
    msg_.score = std::move(arg);
    return Init_Object_bbox(msg_);
  }

private:
  ::robotx_cv::msg::Object msg_;
};

class Init_Object_class_name
{
public:
  Init_Object_class_name()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Object_score class_name(::robotx_cv::msg::Object::_class_name_type arg)
  {
    msg_.class_name = std::move(arg);
    return Init_Object_score(msg_);
  }

private:
  ::robotx_cv::msg::Object msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::robotx_cv::msg::Object>()
{
  return robotx_cv::msg::builder::Init_Object_class_name();
}

}  // namespace robotx_cv

#endif  // ROBOTX_CV__MSG__DETAIL__OBJECT__BUILDER_HPP_
