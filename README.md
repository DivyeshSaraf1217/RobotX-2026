manual control teleop is the node that publishes into manual control topic...can be used for both UUV and USV (vehicle runs in manual mode)

Teleop_test node is the node that publishes cmd velocity. for some reason it doesnt work properly on UUV. angular vel commands work but linear vel commands do not work on UUV.

teleop_cmdvel_rov is the node that publishes velocity commands for UUV. it uses a slightly different method where it publishes into setpoint raw rather than setpoint velocity.

local_pub_one is to publish one local coordinate to the vehicle. it works very well with the USV but with UUV there are reliability issues. 

coord_list is to publish a list of local coordinates to the vehicle. Works very well with USV but remains untested with UUV. 

movement recorder is supposed to track the coordinates while i remote operate the vehicle and saves those coordinates. then it can replay the recorded path and mimic what i did with remote operation
