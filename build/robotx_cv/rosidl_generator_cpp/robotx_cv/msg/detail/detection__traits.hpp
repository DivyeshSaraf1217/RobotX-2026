// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from robotx_cv:msg/Detection.idl
// generated code does not contain a copyright notice

#ifndef ROBOTX_CV__MSG__DETAIL__DETECTION__TRAITS_HPP_
#define ROBOTX_CV__MSG__DETAIL__DETECTION__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "robotx_cv/msg/detail/detection__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'bbox'
#include "vision_msgs/msg/detail/bounding_box2_d__traits.hpp"
// Member 'position'
#include "geometry_msgs/msg/detail/point__traits.hpp"

namespace robotx_cv
{

namespace msg
{

inline void to_flow_style_yaml(
  const Detection & msg,
  std::ostream & out)
{
  out << "{";
  // member: class_name
  {
    out << "class_name: ";
    rosidl_generator_traits::value_to_yaml(msg.class_name, out);
    out << ", ";
  }

  // member: score
  {
    out << "score: ";
    rosidl_generator_traits::value_to_yaml(msg.score, out);
    out << ", ";
  }

  // member: id
  {
    out << "id: ";
    rosidl_generator_traits::value_to_yaml(msg.id, out);
    out << ", ";
  }

  // member: bbox
  {
    out << "bbox: ";
    to_flow_style_yaml(msg.bbox, out);
    out << ", ";
  }

  // member: state
  {
    out << "state: ";
    rosidl_generator_traits::value_to_yaml(msg.state, out);
    out << ", ";
  }

  // member: distance
  {
    out << "distance: ";
    rosidl_generator_traits::value_to_yaml(msg.distance, out);
    out << ", ";
  }

  // member: position
  {
    out << "position: ";
    to_flow_style_yaml(msg.position, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Detection & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: class_name
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "class_name: ";
    rosidl_generator_traits::value_to_yaml(msg.class_name, out);
    out << "\n";
  }

  // member: score
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "score: ";
    rosidl_generator_traits::value_to_yaml(msg.score, out);
    out << "\n";
  }

  // member: id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "id: ";
    rosidl_generator_traits::value_to_yaml(msg.id, out);
    out << "\n";
  }

  // member: bbox
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "bbox:\n";
    to_block_style_yaml(msg.bbox, out, indentation + 2);
  }

  // member: state
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "state: ";
    rosidl_generator_traits::value_to_yaml(msg.state, out);
    out << "\n";
  }

  // member: distance
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "distance: ";
    rosidl_generator_traits::value_to_yaml(msg.distance, out);
    out << "\n";
  }

  // member: position
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "position:\n";
    to_block_style_yaml(msg.position, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Detection & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace robotx_cv

namespace rosidl_generator_traits
{

[[deprecated("use robotx_cv::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const robotx_cv::msg::Detection & msg,
  std::ostream & out, size_t indentation = 0)
{
  robotx_cv::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use robotx_cv::msg::to_yaml() instead")]]
inline std::string to_yaml(const robotx_cv::msg::Detection & msg)
{
  return robotx_cv::msg::to_yaml(msg);
}

template<>
inline const char * data_type<robotx_cv::msg::Detection>()
{
  return "robotx_cv::msg::Detection";
}

template<>
inline const char * name<robotx_cv::msg::Detection>()
{
  return "robotx_cv/msg/Detection";
}

template<>
struct has_fixed_size<robotx_cv::msg::Detection>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<robotx_cv::msg::Detection>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<robotx_cv::msg::Detection>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ROBOTX_CV__MSG__DETAIL__DETECTION__TRAITS_HPP_
