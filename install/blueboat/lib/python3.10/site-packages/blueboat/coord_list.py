import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from mavros_msgs.srv import CommandBool, SetMode
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import threading
import time
import math

class WaypointNavigatorNode(Node):
    def __init__(self):
        super().__init__('waypoint_navigator_node')
        
        # Define a Best Effort QoS profile to match MAVROS
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        # Position subscriber & setpoint publisher
        self.local_pos_sub = self.create_subscription(
            PoseStamped, '/mavros/local_position/pose', self.pose_callback, qos_profile)
            
        self.local_pos_pub = self.create_publisher(
            PoseStamped, '/mavros/setpoint_position/local', 10)
            
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0
        
        self.waypoints = []        # List of (x, y, z) tuples
        self.current_target = None # The specific (x, y, z) coordinate driving to
        
        self.state = 'IDLE' # States: IDLE, NAVIGATING, WAITING
        self.wait_start_time = 0.0
        self.arrival_radius = 1.0 # 3D Euclidean distance threshold in meters
        
        self.arm_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.mode_client = self.create_client(SetMode, '/mavros/set_mode')
        self.is_guided = False
        
        # 10Hz Control Loop
        self.timer = self.create_timer(0.1, self.control_loop)

    def arm_vehicle(self, arm_state):
        if self.arm_client.wait_for_service(timeout_sec=1.0):
            req = CommandBool.Request()
            req.value = arm_state
            self.arm_client.call_async(req)
            action = "ARMED" if arm_state else "DISARMED"
            self.get_logger().info(f"Requested vehicle to be {action}")

    def toggle_mode(self):
        if self.mode_client.wait_for_service(timeout_sec=1.0):
            req = SetMode.Request()
            if self.is_guided:
                req.custom_mode = "MANUAL"
                self.is_guided = False
            else:
                req.custom_mode = "GUIDED"
                self.is_guided = True
            self.mode_client.call_async(req)
            self.get_logger().info(f"Requested mode switch to {req.custom_mode}")

    def pose_callback(self, msg):
        """Updates current 3D position."""
        self.current_x = msg.pose.position.x
        self.current_y = msg.pose.position.y
        self.current_z = msg.pose.position.z

    def control_loop(self):
        """Streams targets and manages waypoint transitions."""
        if self.state == 'IDLE':
            return
            
        if self.current_target is None:
            return
            
        # 1. Broadcast the current 3D target coordinate
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "map"
        msg.pose.position.x = self.current_target[0]
        msg.pose.position.y = self.current_target[1]
        msg.pose.position.z = self.current_target[2]
        self.local_pos_pub.publish(msg)
        
        # 2. Check 3D Euclidean distance to target
        dist = math.sqrt(
            (self.current_target[0] - self.current_x)**2 + 
            (self.current_target[1] - self.current_y)**2 + 
            (self.current_target[2] - self.current_z)**2
        )
                         
        # 3. State Machine Logic
        if self.state == 'NAVIGATING':
            if dist <= self.arrival_radius:
                self.get_logger().info("Arrived at waypoint! Waiting 0 seconds...")
                self.state = 'WAITING'
                self.wait_start_time = time.time()
                
        elif self.state == 'WAITING':
            if time.time() - self.wait_start_time >= 0.0:
                if len(self.waypoints) > 0:
                    self.current_target = self.waypoints.pop(0)
                    self.state = 'NAVIGATING'
                    self.get_logger().info(
                        f"Moving to next waypoint: X={self.current_target[0]:.2f}, "
                        f"Y={self.current_target[1]:.2f}, Z={self.current_target[2]:.2f}"
                    )
                else:
                    self.state = 'IDLE'
                    self.get_logger().info("Mission Complete! Vehicle is holding at final coordinate.")

def user_input_thread(node):
    print("\n--- Sequential Waypoint Navigator ---")
    print("Commands:")
    print("  add <x> <y>      : Add a 2D coordinate (Z defaults to 0.0)")
    print("  add <x> <y> <z>  : Add a 3D coordinate (e.g. 'add 10 5 2.5')")
    print("  start            : Begin the mission")
    print("  clear            : Empty the waypoint queue")
    print("  q                : Arm")
    print("  e                : Disarm")
    print("  t                : Toggle Mode (MANUAL <-> GUIDED)")
    print("  x                : Exit program")
    
    while rclpy.ok():
        try:
            cmd_input = input("\nMission> ").strip().lower()
            parts = cmd_input.split()
            
            if not parts:
                continue
                
            cmd = parts[0]
            
            if cmd == 'x':
                print("Shutting down...")
                rclpy.shutdown()
                break
            elif cmd == 'q':
                node.arm_vehicle(True)
            elif cmd == 'e':
                node.arm_vehicle(False)
            elif cmd == 't':
                node.toggle_mode()
                
            elif cmd == 'add':
                # Automatic 2-axis or 3-axis parsing
                if len(parts) == 3:
                    x, y = float(parts[1]), float(parts[2])
                    z = 0.0
                    node.waypoints.append((x, y, z))
                    print(f"Added (2D) X:{x:.2f}, Y:{y:.2f}, Z:{z:.2f}. Queue size: {len(node.waypoints)}")
                elif len(parts) == 4:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    node.waypoints.append((x, y, z))
                    print(f"Added (3D) X:{x:.2f}, Y:{y:.2f}, Z:{z:.2f}. Queue size: {len(node.waypoints)}")
                else:
                    print("Usage: 'add <x> <y>' or 'add <x> <y> <z>'")
                
            elif cmd == 'start':
                if len(node.waypoints) == 0:
                    print("Error: No waypoints in queue! Type 'add <x> <y> [z]' first.")
                else:
                    print("Ensure vehicle is ARMED and in GUIDED mode! Starting mission...")
                    node.current_target = node.waypoints.pop(0)
                    node.state = 'NAVIGATING'
                    print(
                        f"Navigating to first waypoint: X={node.current_target[0]:.2f}, "
                        f"Y={node.current_target[1]:.2f}, Z={node.current_target[2]:.2f}"
                    )
                    
            elif cmd == 'clear':
                node.waypoints.clear()
                node.state = 'IDLE'
                print("Queue cleared and mission halted.")
                
            else:
                print("Invalid command.")
                
        except ValueError:
            print("Error: Coordinates must be numbers.")
        except Exception as e:
            print(f"Error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = WaypointNavigatorNode()
    
    ui_thread = threading.Thread(target=user_input_thread, args=(node,))
    ui_thread.daemon = True
    ui_thread.start()
    
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