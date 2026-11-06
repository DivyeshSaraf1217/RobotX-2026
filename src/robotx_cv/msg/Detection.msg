# One detected object, any vehicle / task.
string class_name                 # model class (light_beacon, robobuoy, ...)
float32 score                     # model confidence, this frame
int32 id                          # same object across frames, -1 if not tracked
vision_msgs/BoundingBox2D bbox    # pixels, original image; center.theta = rotation (rad), 0 if upright
# Confirmed state of a tracked object, '' if its class has none. Task 1 robobuoy, its light beacon:
# off | flashing_red | flashing_green | flashing_blue | solid_blue | unknown (not confirmed yet)
string state
float32 distance                  # m, camera to object, NaN if unknown
geometry_msgs/Point position      # m, from the depth image at the box centroid, ROS body axes (x forward, y left, z up; task1 ros_frame:=false: optical x right, y down, z forward), NaN if unknown
