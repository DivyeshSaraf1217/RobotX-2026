import rclpy
from rclpy.node import Node
from mavros_msgs.msg import State
import serial

class MavrosLedController(Node):
    def __init__(self):
        super().__init__('mavros_led_controller')
        
        # Open serial port to Arduino. 
        # Change /dev/ttyUSB0 to /dev/ttyACM0 if using an Arduino Uno/Mega via USB
        try:
            self.arduino = serial.Serial('/dev/ttyTHS1', baudrate=115200, timeout=1)
            self.get_logger().info("Connected to Arduino on /dev/ttyTHS1")
        except serial.SerialException as e:
            self.get_logger().error(f"Serial connection failed: {e}")
            self.arduino = None

        self.subscription = self.create_subscription(
            State,
            '/mavros/state',
            self.state_callback,
            10
        )
        
        self.last_sent_cmd = None

    def state_callback(self, msg):
        mode = msg.mode.upper()
        
        # Map ArduPilot/PX4 modes to LED colors
        if mode in ["ALT_HOLD", "DEPTH_HOLD"]:
            cmd = 'Y'  # Yellow
        elif mode == "GUIDED":
            cmd = 'G'  # Green
        else:
            cmd = 'R'  # Red for all other modes (Manual, Stabilize, RTL, etc.)

        # Only send data over serial if the mode has changed to prevent flooding
        if cmd != self.last_sent_cmd and self.arduino and self.arduino.is_open:
            self.arduino.write(cmd.encode('utf-8'))
            self.last_sent_cmd = cmd
            self.get_logger().info(f"Mode changed to {mode} -> Sent '{cmd}'")

def main(args=None):
    rclpy.init(args=args)
    node = MavrosLedController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.arduino and node.arduino.is_open:
            node.arduino.write(b'R') # Reset to red on exit
            node.arduino.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()