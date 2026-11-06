#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to robotx_cv__msg__Object
/// One detected object.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Object {

    // This member is not documented.
    #[allow(missing_docs)]
    pub class_name: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub score: f32,

    /// pixels, original image; center.theta = rotation (rad), 0 if upright
    pub bbox: vision_msgs::msg::BoundingBox2D,

    /// Part of another object (dock.py: window / dock_indicator of a dock_face), else -1 and ''.
    /// index in ObjectArray.objects of the whole object
    pub parent: i32,

    /// window_left | window_right | indicator
    pub part: std::string::String,

    /// part seen in the image; false: placed from the layout
    pub found: bool,

    /// LED state, '' if the class has no LED:
    /// red | green | blue (steady), <colour>_flash, seq_<c1>_<c2>, off, unknown
    pub light: std::string::String,

    /// same light across frames, -1 if no LED
    pub light_id: i32,

    /// this frame only: red | green | blue | off, '' if not read / can't tell
    pub colour: std::string::String,

    /// m, camera to object, NaN if unknown
    pub distance: f32,

    /// m, camera optical frame (x right, y down, z forward), NaN if unknown
    pub position: geometry_msgs::msg::Point,

}



impl Default for Object {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Object::default())
  }
}

impl rosidl_runtime_rs::Message for Object {
  type RmwMsg = super::msg::rmw::Object;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        class_name: msg.class_name.as_str().into(),
        score: msg.score,
        bbox: vision_msgs::msg::BoundingBox2D::into_rmw_message(std::borrow::Cow::Owned(msg.bbox)).into_owned(),
        parent: msg.parent,
        part: msg.part.as_str().into(),
        found: msg.found,
        light: msg.light.as_str().into(),
        light_id: msg.light_id,
        colour: msg.colour.as_str().into(),
        distance: msg.distance,
        position: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(msg.position)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        class_name: msg.class_name.as_str().into(),
      score: msg.score,
        bbox: vision_msgs::msg::BoundingBox2D::into_rmw_message(std::borrow::Cow::Borrowed(&msg.bbox)).into_owned(),
      parent: msg.parent,
        part: msg.part.as_str().into(),
      found: msg.found,
        light: msg.light.as_str().into(),
      light_id: msg.light_id,
        colour: msg.colour.as_str().into(),
      distance: msg.distance,
        position: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(&msg.position)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      class_name: msg.class_name.to_string(),
      score: msg.score,
      bbox: vision_msgs::msg::BoundingBox2D::from_rmw_message(msg.bbox),
      parent: msg.parent,
      part: msg.part.to_string(),
      found: msg.found,
      light: msg.light.to_string(),
      light_id: msg.light_id,
      colour: msg.colour.to_string(),
      distance: msg.distance,
      position: geometry_msgs::msg::Point::from_rmw_message(msg.position),
    }
  }
}


// Corresponds to robotx_cv__msg__ObjectArray

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ObjectArray {
    /// same stamp as the source image
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub objects: Vec<super::msg::Object>,

}



impl Default for ObjectArray {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::ObjectArray::default())
  }
}

impl rosidl_runtime_rs::Message for ObjectArray {
  type RmwMsg = super::msg::rmw::ObjectArray;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        objects: msg.objects
          .into_iter()
          .map(|elem| super::msg::Object::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        objects: msg.objects
          .iter()
          .map(|elem| super::msg::Object::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      objects: msg.objects
          .into_iter()
          .map(super::msg::Object::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to robotx_cv__msg__Detection
/// One detected object, any vehicle / task.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Detection {
    /// model class (light_beacon, robobuoy, ...)
    pub class_name: std::string::String,

    /// model confidence, this frame
    pub score: f32,

    /// same object across frames, -1 if not tracked
    pub id: i32,

    /// pixels, original image; center.theta = rotation (rad), 0 if upright
    pub bbox: vision_msgs::msg::BoundingBox2D,

    /// Confirmed state of a tracked object, '' if its class has none. Task 1 robobuoy, its light beacon:
    /// off | flashing_red | flashing_green | flashing_blue | solid_blue | unknown (not confirmed yet)
    pub state: std::string::String,

    /// m, camera to object, NaN if unknown
    pub distance: f32,

    /// m, from the depth image at the box centroid, ROS body axes (x forward, y left, z up; task1 ros_frame:=false: optical x right, y down, z forward), NaN if unknown
    pub position: geometry_msgs::msg::Point,

}



impl Default for Detection {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Detection::default())
  }
}

impl rosidl_runtime_rs::Message for Detection {
  type RmwMsg = super::msg::rmw::Detection;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        class_name: msg.class_name.as_str().into(),
        score: msg.score,
        id: msg.id,
        bbox: vision_msgs::msg::BoundingBox2D::into_rmw_message(std::borrow::Cow::Owned(msg.bbox)).into_owned(),
        state: msg.state.as_str().into(),
        distance: msg.distance,
        position: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(msg.position)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        class_name: msg.class_name.as_str().into(),
      score: msg.score,
      id: msg.id,
        bbox: vision_msgs::msg::BoundingBox2D::into_rmw_message(std::borrow::Cow::Borrowed(&msg.bbox)).into_owned(),
        state: msg.state.as_str().into(),
      distance: msg.distance,
        position: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(&msg.position)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      class_name: msg.class_name.to_string(),
      score: msg.score,
      id: msg.id,
      bbox: vision_msgs::msg::BoundingBox2D::from_rmw_message(msg.bbox),
      state: msg.state.to_string(),
      distance: msg.distance,
      position: geometry_msgs::msg::Point::from_rmw_message(msg.position),
    }
  }
}


// Corresponds to robotx_cv__msg__DetectionArray

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct DetectionArray {
    /// same stamp and frame_id as the source image
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub detections: Vec<super::msg::Detection>,

}



impl Default for DetectionArray {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::DetectionArray::default())
  }
}

impl rosidl_runtime_rs::Message for DetectionArray {
  type RmwMsg = super::msg::rmw::DetectionArray;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        detections: msg.detections
          .into_iter()
          .map(|elem| super::msg::Detection::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        detections: msg.detections
          .iter()
          .map(|elem| super::msg::Detection::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      detections: msg.detections
          .into_iter()
          .map(super::msg::Detection::from_rmw_message)
          .collect(),
    }
  }
}


