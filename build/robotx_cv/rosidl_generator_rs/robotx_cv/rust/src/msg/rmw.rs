#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "robotx_cv__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__robotx_cv__msg__Object() -> *const std::ffi::c_void;
}

#[link(name = "robotx_cv__rosidl_generator_c")]
extern "C" {
    fn robotx_cv__msg__Object__init(msg: *mut Object) -> bool;
    fn robotx_cv__msg__Object__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Object>, size: usize) -> bool;
    fn robotx_cv__msg__Object__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Object>);
    fn robotx_cv__msg__Object__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Object>, out_seq: *mut rosidl_runtime_rs::Sequence<Object>) -> bool;
}

// Corresponds to robotx_cv__msg__Object
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// One detected object.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Object {

    // This member is not documented.
    #[allow(missing_docs)]
    pub class_name: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub score: f32,

    /// pixels, original image; center.theta = rotation (rad), 0 if upright
    pub bbox: vision_msgs::msg::rmw::BoundingBox2D,

    /// Part of another object (dock.py: window / dock_indicator of a dock_face), else -1 and ''.
    /// index in ObjectArray.objects of the whole object
    pub parent: i32,

    /// window_left | window_right | indicator
    pub part: rosidl_runtime_rs::String,

    /// part seen in the image; false: placed from the layout
    pub found: bool,

    /// LED state, '' if the class has no LED:
    /// red | green | blue (steady), <colour>_flash, seq_<c1>_<c2>, off, unknown
    pub light: rosidl_runtime_rs::String,

    /// same light across frames, -1 if no LED
    pub light_id: i32,

    /// this frame only: red | green | blue | off, '' if not read / can't tell
    pub colour: rosidl_runtime_rs::String,

    /// m, camera to object, NaN if unknown
    pub distance: f32,

    /// m, camera optical frame (x right, y down, z forward), NaN if unknown
    pub position: geometry_msgs::msg::rmw::Point,

}



impl Default for Object {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !robotx_cv__msg__Object__init(&mut msg as *mut _) {
        panic!("Call to robotx_cv__msg__Object__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Object {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robotx_cv__msg__Object__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robotx_cv__msg__Object__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robotx_cv__msg__Object__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Object {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Object where Self: Sized {
  const TYPE_NAME: &'static str = "robotx_cv/msg/Object";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__robotx_cv__msg__Object() }
  }
}


#[link(name = "robotx_cv__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__robotx_cv__msg__ObjectArray() -> *const std::ffi::c_void;
}

#[link(name = "robotx_cv__rosidl_generator_c")]
extern "C" {
    fn robotx_cv__msg__ObjectArray__init(msg: *mut ObjectArray) -> bool;
    fn robotx_cv__msg__ObjectArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ObjectArray>, size: usize) -> bool;
    fn robotx_cv__msg__ObjectArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ObjectArray>);
    fn robotx_cv__msg__ObjectArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ObjectArray>, out_seq: *mut rosidl_runtime_rs::Sequence<ObjectArray>) -> bool;
}

// Corresponds to robotx_cv__msg__ObjectArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ObjectArray {
    /// same stamp as the source image
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub objects: rosidl_runtime_rs::Sequence<super::super::msg::rmw::Object>,

}



impl Default for ObjectArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !robotx_cv__msg__ObjectArray__init(&mut msg as *mut _) {
        panic!("Call to robotx_cv__msg__ObjectArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ObjectArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robotx_cv__msg__ObjectArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robotx_cv__msg__ObjectArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robotx_cv__msg__ObjectArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ObjectArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ObjectArray where Self: Sized {
  const TYPE_NAME: &'static str = "robotx_cv/msg/ObjectArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__robotx_cv__msg__ObjectArray() }
  }
}


#[link(name = "robotx_cv__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__robotx_cv__msg__Detection() -> *const std::ffi::c_void;
}

#[link(name = "robotx_cv__rosidl_generator_c")]
extern "C" {
    fn robotx_cv__msg__Detection__init(msg: *mut Detection) -> bool;
    fn robotx_cv__msg__Detection__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Detection>, size: usize) -> bool;
    fn robotx_cv__msg__Detection__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Detection>);
    fn robotx_cv__msg__Detection__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Detection>, out_seq: *mut rosidl_runtime_rs::Sequence<Detection>) -> bool;
}

// Corresponds to robotx_cv__msg__Detection
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// One detected object, any vehicle / task.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Detection {
    /// model class (light_beacon, robobuoy, ...)
    pub class_name: rosidl_runtime_rs::String,

    /// model confidence, this frame
    pub score: f32,

    /// same object across frames, -1 if not tracked
    pub id: i32,

    /// pixels, original image; center.theta = rotation (rad), 0 if upright
    pub bbox: vision_msgs::msg::rmw::BoundingBox2D,

    /// Confirmed state of a tracked object, '' if its class has none. Task 1 robobuoy, its light beacon:
    /// off | flashing_red | flashing_green | flashing_blue | solid_blue | unknown (not confirmed yet)
    pub state: rosidl_runtime_rs::String,

    /// m, camera to object, NaN if unknown
    pub distance: f32,

    /// m, from the depth image at the box centroid, ROS body axes (x forward, y left, z up; task1 ros_frame:=false: optical x right, y down, z forward), NaN if unknown
    pub position: geometry_msgs::msg::rmw::Point,

}



impl Default for Detection {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !robotx_cv__msg__Detection__init(&mut msg as *mut _) {
        panic!("Call to robotx_cv__msg__Detection__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Detection {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robotx_cv__msg__Detection__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robotx_cv__msg__Detection__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robotx_cv__msg__Detection__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Detection {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Detection where Self: Sized {
  const TYPE_NAME: &'static str = "robotx_cv/msg/Detection";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__robotx_cv__msg__Detection() }
  }
}


#[link(name = "robotx_cv__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__robotx_cv__msg__DetectionArray() -> *const std::ffi::c_void;
}

#[link(name = "robotx_cv__rosidl_generator_c")]
extern "C" {
    fn robotx_cv__msg__DetectionArray__init(msg: *mut DetectionArray) -> bool;
    fn robotx_cv__msg__DetectionArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<DetectionArray>, size: usize) -> bool;
    fn robotx_cv__msg__DetectionArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<DetectionArray>);
    fn robotx_cv__msg__DetectionArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<DetectionArray>, out_seq: *mut rosidl_runtime_rs::Sequence<DetectionArray>) -> bool;
}

// Corresponds to robotx_cv__msg__DetectionArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct DetectionArray {
    /// same stamp and frame_id as the source image
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub detections: rosidl_runtime_rs::Sequence<super::super::msg::rmw::Detection>,

}



impl Default for DetectionArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !robotx_cv__msg__DetectionArray__init(&mut msg as *mut _) {
        panic!("Call to robotx_cv__msg__DetectionArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for DetectionArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robotx_cv__msg__DetectionArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robotx_cv__msg__DetectionArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { robotx_cv__msg__DetectionArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for DetectionArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for DetectionArray where Self: Sized {
  const TYPE_NAME: &'static str = "robotx_cv/msg/DetectionArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__robotx_cv__msg__DetectionArray() }
  }
}


