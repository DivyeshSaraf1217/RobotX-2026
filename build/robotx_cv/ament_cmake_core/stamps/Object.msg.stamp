# One detected object.
string class_name
float32 score
vision_msgs/BoundingBox2D bbox    # pixels, original image; center.theta = rotation (rad), 0 if upright

# Part of another object (dock.py: window / dock_indicator of a dock_face), else -1 and ''.
int32 parent                      # index in ObjectArray.objects of the whole object
string part                       # window_left | window_right | indicator
bool found                        # part seen in the image; false: placed from the layout

# LED state, '' if the class has no LED:
# red | green | blue (steady), <colour>_flash, seq_<c1>_<c2>, off, unknown
string light
int32 light_id                    # same light across frames, -1 if no LED
string colour                     # this frame only: red | green | blue | off, '' if not read / can't tell

float32 distance                  # m, camera to object, NaN if unknown
geometry_msgs/Point position      # m, camera optical frame (x right, y down, z forward), NaN if unknown
