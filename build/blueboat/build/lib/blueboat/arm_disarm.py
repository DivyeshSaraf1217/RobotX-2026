import sys
import select
import termios
import tty
import threading
import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from mavros_msgs.msg import ManualControl
from mavros_msgs.srv import CommandBool

class BlueBoatTeleop(Node):
    def __init__(self):
        super().__init__('blueboat_teleop')
        
        # Define Best Effort QoS profile
        best_effort_qos = QoSProfile(
            depth=10, 
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST
        )
        
        # Apply the QoS profile to the publisher
        self.pub = self.create_publisher(ManualControl, '/mavros/manual_control/send', 10)
        self.arm_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        
        self.forward = 0.0
        self.steering = 0.0
        
        # Publish exactly at 20Hz asynchronously
        self.timer = self.create_timer(0.05, self.publish_command)

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
                self.get_logger().info("Success! Vehicle arm state changed. Wait 3 seconds before moving.")
            else:
                self.get_logger().warn("Failed to change arm state.")
        except Exception as e:
            self.get_logger().error(f"Service call failed: {e}")

    def publish_command(self):
        msg = ManualControl()
        msg.x = self.forward
        msg.y = 0.0
        msg.z = 500.0
        msg.r = self.steering
        msg.buttons = 0  # Required to prevent garbage data failsafes
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = BlueBoatTeleop()
    
    # Run ROS spin in a background thread so terminal inputs don't interrupt publishing
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,))
    spin_thread.start()
    
    settings = termios.tcgetattr(sys.stdin)
    
    node.get_logger().info("Threaded Terminal Teleop Started at 20Hz (Best Effort QoS).")
    node.get_logger().info("Controls: W=Forward | X=Backward | A/D=Steer | S=STOP (Center) | Q=Arm | E=Disarm | CTRL+C=Quit")

    try:
        while rclpy.ok():
            tty.setraw(sys.stdin.fileno())
            # We can safely block here now because the publisher runs in the background
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1) 
            if rlist:
                key = sys.stdin.read(1)
            else:
                key = ''
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

            if key:
                key = key.lower()
                
                if key == 'w':
                    node.forward = 500.0
                    print("\rForward Locked (150.0)", end="")
                elif key == 'x':
                    node.forward = -500.0
                    print("\rReverse Locked (-150.0)", end="")
                elif key == 'a':
                    node.steering = -500.0
                    print("\rLeft Steering Locked (-150.0)", end="")
                elif key == 'd':
                    node.steering = 500.0
                    print("\rRight Steering Locked (150.0)", end="")
                elif key == 's':
                    node.forward = 0.0
                    node.steering = 0.0
                    print("\rALL STOP (Centered)", end="")
                elif key == 'q':
                    print("\r", end="") # Clear line formatting
                    node.arm_vehicle(True)
                elif key == 'e':
                    print("\r", end="")
                    node.arm_vehicle(False)
                elif key == '\x03': 
                    print("\rCTRL+C detected. Shutting down...")
                    break

    except Exception as e:
        node.get_logger().error(f"Error: {e}")
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        spin_thread.join()

if __name__ == '__main__':
    main()