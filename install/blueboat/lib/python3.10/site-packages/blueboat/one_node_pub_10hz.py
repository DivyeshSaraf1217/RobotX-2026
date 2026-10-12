import sys
import select
import termios
import tty
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from sensor_msgs.msg import NavSatFix
from geographic_msgs.msg import GeoPoseStamped
from mavros_msgs.srv import CommandBool, SetMode
import threading

class BlueBoatCommanderNode(Node):
    def __init__(self):
        super().__init__('blueboat_commander_node')
        
        # --- SUBSCRIBERS ---
        self.gps_sub = self.create_subscription(
            NavSatFix, '/mavros/global_position/global', self.gps_callback, 10)
        self.local_pos_sub = self.create_subscription(
            PoseStamped, '/mavros/local_position/pose', self.local_pos_callback, 10)
            
        # --- PUBLISHERS ---
        self.cmd_vel_pub = self.create_publisher(
            Twist, '/mavros/setpoint_velocity/cmd_vel_unstamped', 10)
        self.global_pos_pub = self.create_publisher(
            GeoPoseStamped, '/mavros/setpoint_position/global', 10)
        self.local_pos_pub = self.create_publisher(
            PoseStamped, '/mavros/setpoint_position/local', 10)
            
        # --- SERVICES ---
        self.arm_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.mode_client = self.create_client(SetMode, '/mavros/set_mode')

        # --- STATE VARIABLES ---
        self.current_lat = 0.0
        self.current_lon = 0.0
        self.has_gps = False
        
        self.current_local_x = 0.0
        self.current_local_y = 0.0
        self.current_local_z = 0.0
        
        # Navigation State Machine ('none', 'teleop', 'global', 'local')
        self.active_mode = 'none' 
        
        # Target Variables
        self.target_linear = 0.0
        self.target_angular = 0.0
        self.target_lat = 0.0
        self.target_lon = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        
        # 10Hz Master Control Loop
        self.timer = self.create_timer(0.1, self.control_loop_callback)

    def gps_callback(self, msg):
        self.current_lat = msg.latitude
        self.current_lon = msg.longitude
        if msg.latitude != 0.0 and msg.longitude != 0.0:
            self.has_gps = True

    def local_pos_callback(self, msg):
        self.current_local_x = msg.pose.position.x
        self.current_local_y = msg.pose.position.y
        self.current_local_z = msg.pose.position.z

    def control_loop_callback(self):
        """Continuously streams the active command at 10Hz to prevent packet drop/timeouts."""
        if self.active_mode == 'teleop':
            msg = Twist()
            msg.linear.x = self.target_linear
            msg.angular.z = self.target_angular
            self.cmd_vel_pub.publish(msg)
            
        elif self.active_mode == 'global':
            msg = GeoPoseStamped()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "map"
            msg.pose.position.latitude = self.target_lat
            msg.pose.position.longitude = self.target_lon
            msg.pose.position.altitude = 0.0
            self.global_pos_pub.publish(msg)
            
        elif self.active_mode == 'local':
            msg = PoseStamped()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "map"
            msg.pose.position.x = self.target_x
            msg.pose.position.y = self.target_y
            msg.pose.position.z = 0.0
            self.local_pos_pub.publish(msg)

    def set_mode_and_arm(self):
        if self.mode_client.wait_for_service(timeout_sec=1.0):
            req_mode = SetMode.Request()
            req_mode.custom_mode = "GUIDED"
            self.mode_client.call_async(req_mode)
            
        if self.arm_client.wait_for_service(timeout_sec=1.0):
            req_arm = CommandBool.Request()
            req_arm.value = True
            self.arm_client.call_async(req_arm)
        self.get_logger().info("Requested GUIDED mode and ARMED.")

    def disarm(self):
        self.active_mode = 'none' # Stop streaming movement commands when disarming
        
        # Send one explicit stop command just to be safe
        self.cmd_vel_pub.publish(Twist())
        
        if self.arm_client.wait_for_service(timeout_sec=1.0):
            req_arm = CommandBool.Request()
            req_arm.value = False
            self.arm_client.call_async(req_arm)
        self.get_logger().info("Requested DISARM and halted command streams.")

    def send_global_waypoint(self, lat, lon):
        self.target_lat = lat
        self.target_lon = lon
        self.active_mode = 'global' # Background timer takes over immediately
        self.get_logger().info(f"Streaming GPS target: Lat {lat}, Lon {lon}")

    def send_local_waypoint(self, x, y):
        self.target_x = x
        self.target_y = y
        self.active_mode = 'local' # Background timer takes over immediately
        self.get_logger().info(f"Streaming Local target: X(East) {x}m, Y(North) {y}m")

# ==========================================================
# USER INTERFACE THREAD
# ==========================================================
def print_menu():
    print("\n" + "="*40)
    print(" 🚢 BLUEBOAT UNIFIED COMMANDER 🚢")
    print("="*40)
    print(" s       : Show current GPS & Local Position (Status)")
    print(" a / d   : Arm / Disarm thruster power")
    print(" g <lat> <lon> : Drive to global coordinate (GPS)")
    print(" l <x> <y>   : Drive to local coordinate (meters)")
    print(" t       : Enter WASD manual control mode (Teleop)")
    print(" q       : Exit program (Quit)")
    print(" m       : Show this menu")
    print("="*40)

def teleop_loop(node):
    """Takes over the terminal for raw WASD keystrokes."""
    print("\n--- TELEOP MODE ACTIVE ---")
    print("W/X : Speed Up/Down (0.1 m/s)")
    print("A/D : Turn Left/Right (0.1 rad/s)")
    print("S   : ALL STOP")
    print("Q   : Quit Teleop & Return to Menu")
    print("Note: Make sure you have ARMED the boat first!")
    
    node.active_mode = 'teleop'
    
    settings = termios.tcgetattr(sys.stdin)
    try:
        while rclpy.ok():
            tty.setraw(sys.stdin.fileno())
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            key = sys.stdin.read(1) if rlist else ''
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

            if key:
                key = key.lower()
                if key == 'w':
                    node.target_linear = round(node.target_linear + 0.1, 1)
                    print(f"\rSpeed: {node.target_linear} m/s | Turn: {node.target_angular} rad/s    ", end='')
                elif key == 'x':
                    node.target_linear = round(node.target_linear - 0.1, 1)
                    print(f"\rSpeed: {node.target_linear} m/s | Turn: {node.target_angular} rad/s    ", end='')
                elif key == 'a':
                    node.target_angular = round(node.target_angular + 0.1, 1)
                    print(f"\rSpeed: {node.target_linear} m/s | Turn: {node.target_angular} rad/s    ", end='')
                elif key == 'd':
                    node.target_angular = round(node.target_angular - 0.1, 1)
                    print(f"\rSpeed: {node.target_linear} m/s | Turn: {node.target_angular} rad/s    ", end='')
                elif key == 's':
                    node.target_linear = 0.0
                    node.target_angular = 0.0
                    print(f"\rALL STOP                                           ", end='')
                elif key == 'q':
                    # Stop the boat immediately
                    node.target_linear = 0.0
                    node.target_angular = 0.0
                    node.cmd_vel_pub.publish(Twist()) # Force one final zero-publish
                    node.active_mode = 'none' # Stop the timer loop
                    print("\nExiting Teleop Mode...")
                    break
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

def user_interface_thread(node):
    print_menu()
    while rclpy.ok():
        try:
            cmd_input = input("\nBlueBoat> ").strip().lower()
            parts = cmd_input.split()
            
            if not parts:
                continue
                
            cmd = parts[0]
            
            if cmd == 'q':
                print("Shutting down...")
                rclpy.shutdown()
                break
                
            elif cmd == 's':
                print(f"\n[GLOBAL] Lat: {node.current_lat:.6f}, Lon: {node.current_lon:.6f} (GPS Lock: {node.has_gps})")
                print(f"[LOCAL]  X (East): {node.current_local_x:.2f}m, Y (North): {node.current_local_y:.2f}m")
                
            elif cmd == 'a':
                node.set_mode_and_arm()
                
            elif cmd == 'd':
                node.disarm()
                
            elif cmd == 't':
                teleop_loop(node)
                print_menu()
                
            elif cmd == 'g':
                if len(parts) == 3:
                    lat, lon = float(parts[1]), float(parts[2])
                    node.send_global_waypoint(lat, lon)
                else:
                    print("Usage: g <latitude> <longitude>")
                    
            elif cmd == 'l':
                if len(parts) == 3:
                    x, y = float(parts[1]), float(parts[2])
                    node.send_local_waypoint(x, y)
                else:
                    print("Usage: l <x_meters> <y_meters>")
                    
            elif cmd in ['h', 'm']:
                print_menu()
                
            else:
                print("Unknown command. Type 'm' for options.")
                
        except ValueError:
            print("Error: Ensure coordinates are numbers (e.g. 'g 1.29 103.85')")
        except Exception as e:
            print(f"Error reading input: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = BlueBoatCommanderNode()
    
    ui_thread = threading.Thread(target=user_interface_thread, args=(node,))
    ui_thread.daemon = True
    ui_thread.start()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.active_mode = 'none'
        node.cmd_vel_pub.publish(Twist()) # Failsafe stop
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()