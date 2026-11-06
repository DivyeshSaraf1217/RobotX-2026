// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from robotx_cv:msg/Object.idl
// generated code does not contain a copyright notice

#ifndef ROBOTX_CV__MSG__DETAIL__OBJECT__STRUCT_HPP_
#define ROBOTX_CV__MSG__DETAIL__OBJECT__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'bbox'
#include "vision_msgs/msg/detail/bounding_box2_d__struct.hpp"
// Member 'position'
#include "geometry_msgs/msg/detail/point__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__robotx_cv__msg__Object __attribute__((deprecated))
#else
# define DEPRECATED__robotx_cv__msg__Object __declspec(deprecated)
#endif

namespace robotx_cv
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Object_
{
  using Type = Object_<ContainerAllocator>;

  explicit Object_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : bbox(_init),
    position(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->class_name = "";
      this->score = 0.0f;
      this->parent = 0l;
      this->part = "";
      this->found = false;
      this->light = "";
      this->light_id = 0l;
      this->colour = "";
      this->distance = 0.0f;
    }
  }

  explicit Object_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : class_name(_alloc),
    bbox(_alloc, _init),
    part(_alloc),
    light(_alloc),
    colour(_alloc),
    position(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->class_name = "";
      this->score = 0.0f;
      this->parent = 0l;
      this->part = "";
      this->found = false;
      this->light = "";
      this->light_id = 0l;
      this->colour = "";
      this->distance = 0.0f;
    }
  }

  // field types and members
  using _class_name_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _class_name_type class_name;
  using _score_type =
    float;
  _score_type score;
  using _bbox_type =
    vision_msgs::msg::BoundingBox2D_<ContainerAllocator>;
  _bbox_type bbox;
  using _parent_type =
    int32_t;
  _parent_type parent;
  using _part_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _part_type part;
  using _found_type =
    bool;
  _found_type found;
  using _light_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _light_type light;
  using _light_id_type =
    int32_t;
  _light_id_type light_id;
  using _colour_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _colour_type colour;
  using _distance_type =
    float;
  _distance_type distance;
  using _position_type =
    geometry_msgs::msg::Point_<ContainerAllocator>;
  _position_type position;

  // setters for named parameter idiom
  Type & set__class_name(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->class_name = _arg;
    return *this;
  }
  Type & set__score(
    const float & _arg)
  {
    this->score = _arg;
    return *this;
  }
  Type & set__bbox(
    const vision_msgs::msg::BoundingBox2D_<ContainerAllocator> & _arg)
  {
    this->bbox = _arg;
    return *this;
  }
  Type & set__parent(
    const int32_t & _arg)
  {
    this->parent = _arg;
    return *this;
  }
  Type & set__part(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->part = _arg;
    return *this;
  }
  Type & set__found(
    const bool & _arg)
  {
    this->found = _arg;
    return *this;
  }
  Type & set__light(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->light = _arg;
    return *this;
  }
  Type & set__light_id(
    const int32_t & _arg)
  {
    this->light_id = _arg;
    return *this;
  }
  Type & set__colour(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->colour = _arg;
    return *this;
  }
  Type & set__distance(
    const float & _arg)
  {
    this->distance = _arg;
    return *this;
  }
  Type & set__position(
    const geometry_msgs::msg::Point_<ContainerAllocator> & _arg)
  {
    this->position = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    robotx_cv::msg::Object_<ContainerAllocator> *;
  using ConstRawPtr =
    const robotx_cv::msg::Object_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<robotx_cv::msg::Object_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<robotx_cv::msg::Object_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      robotx_cv::msg::Object_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<robotx_cv::msg::Object_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      robotx_cv::msg::Object_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<robotx_cv::msg::Object_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<robotx_cv::msg::Object_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<robotx_cv::msg::Object_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__robotx_cv__msg__Object
    std::shared_ptr<robotx_cv::msg::Object_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__robotx_cv__msg__Object
    std::shared_ptr<robotx_cv::msg::Object_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Object_ & other) const
  {
    if (this->class_name != other.class_name) {
      return false;
    }
    if (this->score != other.score) {
      return false;
    }
    if (this->bbox != other.bbox) {
      return false;
    }
    if (this->parent != other.parent) {
      return false;
    }
    if (this->part != other.part) {
      return false;
    }
    if (this->found != other.found) {
      return false;
    }
    if (this->light != other.light) {
      return false;
    }
    if (this->light_id != other.light_id) {
      return false;
    }
    if (this->colour != other.colour) {
      return false;
    }
    if (this->distance != other.distance) {
      return false;
    }
    if (this->position != other.position) {
      return false;
    }
    return true;
  }
  bool operator!=(const Object_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Object_

// alias to use template instance with default allocator
using Object =
  robotx_cv::msg::Object_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace robotx_cv

#endif  // ROBOTX_CV__MSG__DETAIL__OBJECT__STRUCT_HPP_
