import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from mavros_msgs.srv import CommandBool, SetMode
import threading

class LocalPublisherNode(Node):
    def __init__(self):
        super().__init__('local_publisher_node')
        
        self.local_pos_pub = self.create_publisher(
            PoseStamped, 
            '/mavros/setpoint_position/local', 
            10)
            
        self.target_x = 0.0
        self.target_y = 0.0
        self.is_publishing = False
        
        self.arm_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.mode_client = self.create_client(SetMode, '/mavros/set_mode')
        self.is_guided = False
        
        # 10Hz Timer to constantly stream the position
        self.timer = self.create_timer(0.1, self.publish_target)

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

    def publish_target(self):
        """Continuously streams the target coordinate at 10Hz."""
        if self.is_publishing:
            msg = PoseStamped()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "map"
            
            msg.pose.position.x = self.target_x
            msg.pose.position.y = self.target_y
            msg.pose.position.z = 0.0
            
            self.local_pos_pub.publish(msg)

def user_input_thread(node):
    print("\n--- Local Coordinate Publisher ---")
    print("Commands:")
    print("  <x> <y> : Stream coordinate (e.g. '10 5')")
    print("  q       : Arm")
    print("  e       : Disarm")
    print("  t       : Toggle Mode (MANUAL <-> GUIDED)")
    print("  x       : Exit program")
    
    while rclpy.ok():
        try:
            cmd = input("\nEnter command: ").strip().lower()
            
            if cmd == 'x':
                print("Shutting down...")
                rclpy.shutdown()
                break
            elif cmd == 'q':
                node.arm_vehicle(True)
                continue
            elif cmd == 'e':
                node.arm_vehicle(False)
                continue
            elif cmd == 't':
                node.toggle_mode()
                continue
                
            parts = cmd.split()
            if len(parts) == 2:
                node.target_x = float(parts[0])
                node.target_y = float(parts[1])
                node.is_publishing = True
                print(f"[STREAMING] Continuously sending X: {node.target_x}, Y: {node.target_y} at 10Hz...")
            else:
                print("Invalid input. Type two numbers separated by a space.")
                
        except ValueError:
            print("Error: Ensure coordinates are numbers (e.g., '5.5 -2.0')")
        except Exception as e:
            pass

def main(args=None):
    rclpy.init(args=args)
    node = LocalPublisherNode()
    
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