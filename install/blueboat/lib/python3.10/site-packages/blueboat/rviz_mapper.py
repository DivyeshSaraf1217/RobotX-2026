import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class PathVisualizerNode(Node):
    def __init__(self):
        super().__init__('path_visualizer_node')
        
        # Define a Best Effort QoS profile to match MAVROS
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        # Listen to where the boat is right now
        self.pose_sub = self.create_subscription(
            PoseStamped, 
            '/mavros/local_position/pose', 
            self.pose_callback, 
            qos_profile)
            
        # Publish the full path line for RViz to draw
        self.path_pub = self.create_publisher(
            Path, 
            '/boat_trajectory', 
            10)
            
        self.path_msg = Path()
        self.get_logger().info("Path Visualizer started! Open RViz2 and subscribe to /boat_trajectory")

    def pose_callback(self, msg):
        # Keep the frame_id identical to the incoming pose (usually 'map' or 'odom')
        self.path_msg.header = msg.header 
        
        # Add the current location to our list of dots
        self.path_msg.poses.append(msg)
        
        # Limit the path to the last 5000 points so your computer's RAM doesn't fill up
        # on very long missions. (5000 points at 10Hz = about 8 minutes of trailing history)
        if len(self.path_msg.poses) > 5000:
            self.path_msg.poses.pop(0)
            
        # Publish the updated path to RViz
        self.path_pub.publish(self.path_msg)

def main(args=None):
    rclpy.init(args=args)
    node = PathVisualizerNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()