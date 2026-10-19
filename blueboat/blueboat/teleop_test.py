import sys
import select
import termios
import tty
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from mavros_msgs.srv import CommandBool, SetMode

class BlueBoatIncrementalTeleop(Node):
    def __init__(self):
        super().__init__('blueboat_teleop')
        
        self.pub = self.create_publisher(Twist, '/mavros/setpoint_velocity/cmd_vel_unstamped', 10)
        self.arm_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.mode_client = self.create_client(SetMode, '/mavros/set_mode')
        
        self.target_linear_vel = 0.0
        self.target_angular_vel = 0.0
        
        # We will assume the script starts while the boat is in MANUAL mode
        self.is_guided = False

    def arm_vehicle(self, arm_state):
        if not self.arm_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('Arming service not available! Is MAVROS running?')
            return
        
        req = CommandBool.Request()
        req.value = arm_state
        future = self.arm_client.call_async(req)
        future.add_done_callback(self.arm_response_callback)
        
        action = "Arming" if arm_state else "Disarming"
        self.get_logger().info(f"Sending {action} command...")

    def arm_response_callback(self, future):
        try:
            response = future.result()
            if response.success:
                self.get_logger().info("Success! Vehicle arm state changed.")
            else:
                self.get_logger().warn("Failed to change arm state.")
        except Exception as e:
            self.get_logger().error(f"Service call failed: {e}")

    def toggle_mode(self):
        if not self.mode_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('SetMode service not available!')
            return
            
        req = SetMode.Request()
        
        # Toggle between ArduRover's MANUAL and GUIDED modes
        if self.is_guided:
            req.custom_mode = "MANUAL"
            self.is_guided = False
            self.get_logger().info("Switching to MANUAL mode...")
        else:
            req.custom_mode = "GUIDED"
            self.is_guided = True
            self.get_logger().info("Switching to GUIDED mode...")
            
        future = self.mode_client.call_async(req)
        future.add_done_callback(self.mode_response_callback)

    def mode_response_callback(self, future):
        try:
            response = future.result()
            if response.mode_sent:
                self.get_logger().info("Success! Flight mode changed.")
            else:
                self.get_logger().warn("Failed to change flight mode.")
        except Exception as e:
            self.get_logger().error(f"Mode Service call failed: {e}")

    def publish_command(self):
        msg = Twist()
        msg.linear.x = self.target_linear_vel
        msg.angular.z = self.target_angular_vel
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = BlueBoatIncrementalTeleop()
    
    settings = termios.tcgetattr(sys.stdin)
    
    node.get_logger().info("Incremental CMD_VEL Teleop Started.")
    node.get_logger().info("CONTROLS:")
    node.get_logger().info(" W/X : Increase/Decrease Forward Speed by 0.1 m/s")
    node.get_logger().info(" A/D : Increase/Decrease Turn Speed by 0.1 rad/s")
    node.get_logger().info(" S   : ALL STOP (0 m/s)")
    node.get_logger().info(" T   : Toggle Mode (MANUAL <-> GUIDED)")
    node.get_logger().info(" Q/E : Arm / Disarm")
    node.get_logger().info(" CTRL+C to Quit")

    try:
        while rclpy.ok():
            tty.setraw(sys.stdin.fileno())
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1) 
            if rlist:
                key = sys.stdin.read(1)
            else:
                key = ''
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

            if key:
                key = key.lower()
                
                # Speed increments
                if key == 'w':
                    node.target_linear_vel = round(node.target_linear_vel + 0.1, 1)
                    node.get_logger().info(f"Speed increased: {node.target_linear_vel} m/s")
                elif key == 'x':
                    node.target_linear_vel = round(node.target_linear_vel - 0.1, 1)
                    node.get_logger().info(f"Speed decreased: {node.target_linear_vel} m/s")
                elif key == 'a':
                    node.target_angular_vel = round(node.target_angular_vel + 0.1, 1)
                    node.get_logger().info(f"Turn left rate: {node.target_angular_vel} rad/s")
                elif key == 'd':
                    node.target_angular_vel = round(node.target_angular_vel - 0.1, 1)
                    node.get_logger().info(f"Turn right rate: {node.target_angular_vel} rad/s")
                
                # Instant Stop
                elif key == 's':
                    node.target_linear_vel = 0.0
                    node.target_angular_vel = 0.0
                    node.get_logger().info("ALL STOP (0.0 m/s)")
                
                # System Controls
                elif key == 't':
                    node.toggle_mode()
                elif key == 'q':
                    node.arm_vehicle(True)
                elif key == 'e':
                    node.arm_vehicle(False)
                
                # Exit
                elif key == '\x03': # CTRL+C
                    node.get_logger().info("CTRL+C detected. Shutting down...")
                    break
            
            node.publish_command()
            rclpy.spin_once(node, timeout_sec=0.0)

    except Exception as e:
        node.get_logger().error(f"Error: {e}")
    finally:
        # Failsafe: stop the boat before exiting
        node.target_linear_vel = 0.0
        node.target_angular_vel = 0.0
        node.publish_command()
        
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()