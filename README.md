manual control teleop is the node that publishes into manual control topic...can be used for both UUV and USV (vehicle runs in manual mode)

Teleop_test node is the node that publishes cmd velocity. for some reason it doesnt work properly on UUV. angular vel commands work but linear vel commands do not work on UUV.

teleop_cmdvel_rov is the node that publishes velocity commands for UUV. it uses a slightly different method where it publishes into setpoint raw rather than setpoint velocity.

local_pub_one is to publish one local coordinate to the vehicle. it works very well with the USV but with UUV there are reliability issues. 

coord_list is to publish a list of local coordinates to the vehicle. Works very well with USV but remains untested with UUV. 

movement recorder is supposed to track the coordinates while i remote operate the vehicle and saves those coordinates. then it can replay the recorded path and mimic what i did with remote operation

rov programmer is a block programming code where you can input a path in the form of strings - for example "z-0.5 t2 w4 l90 d4" means to go to a depth of 0.5m, hold 2 seconds (t-hold) forward for seconds, turn clockwise 90 degrees, strafe left for 4 seconds. all the detailed input can be found in the menu in the code.


To turn on ZED zamera stream on Blueboat - 
ros2 launch zed_wrapper zed_camera.launch.py camera_model:=zed2

To turn on Lidar-
ros2 launch rslidar_sdk start.py

for both camera and lidar just rosbag the relevant topics

Mavros - 
For blueboat the port is 14560 - 
ros2 launch mavros apm.launch   fcu_url:=udp://:14560@ tgt_system:=2   tgt_component:=1   namespace:=blueboat

For bluerov the port is 14570 - 
ros2 launch mavros apm.launch   fcu_url:=udp://:14570@ 

For realsense camera on ROV -   
ros2 launch realsense2_camera rs_launch.py enable_depth:=false rgb_camera.color_profile:=640x480x30
To convert raw image to compressed image - 
ros2 run image_transport republish raw compressed --ros-args --remap in:=/camera/camera/color/image_raw --remap out:=/cv_camera/image
