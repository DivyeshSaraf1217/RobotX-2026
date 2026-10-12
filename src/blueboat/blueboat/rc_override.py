#!/usr/bin/env python3

import sys
import threading
import termios
import tty
import rclpy
from rclpy.node import Node
from mavros_msgs.msg import OverrideRCIn
from mavros_msgs.srv import CommandBool, SetMode


class BlueBoatTeleop(Node):
    def __init__(self):
        super().__init__('blueboat_teleop')

        # ---------------- Mutex & State ---------------- #
        self.lock = threading.Lock()
        
        # PWM Constants
        self.PWM_NEUTRAL = 1500
        self.PWM_FORWARD = 1750
        self.PWM_REVERSE = 1250
        self.PWM_LEFT = 1250
        self.PWM_RIGHT = 1750

        # Protected state variables
        self.throttle_pwm = self.PWM_NEUTRAL  # CH 3
        self.steering_pwm = self.PWM_NEUTRAL  # CH 1
        self.is_armed = False

        # ---------------- MAVROS Interfaces ---------------- #
        self.rc_pub = self.create_publisher(OverrideRCIn, '/mavros/rc/override', 10)
        self.arm_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.set_mode_client = self.create_client(SetMode, '/mavros/set_mode')

        # ---------------- 10 Hz Decoupled Timer ---------------- #
        # Fires precisely every 0.1s in the ROS background thread
        self.timer = self.create_timer(0.1, self.publish_command_callback)

        self.get_logger().info("Threaded BlueBoat Teleop Node Initialized.")
        self.get_logger().info("MAVROS 10 Hz publishing timer decoupled from terminal I/O.")
        self.get_logger().info("Controls: W=Forward | X=Reverse | A=Left | D=Right | S=STOP | Q=Arm | E=Disarm | T=Manual | CTRL+C=Quit")

    def update_setpoints(self, throttle: int, steering: int):
        """Thread-safe update of vehicle motion setpoints."""
        with self.lock:
            self.throttle_pwm = throttle
            self.steering_pwm = steering

    def publish_command_callback(self):
        """Timer callback: strictly publishes at 10 Hz."""
        with self.lock:
            throttle = self.throttle_pwm
            steering = self.steering_pwm

        msg = OverrideRCIn()
        msg.channels = [0] * 18

        # ArduPilot Channel Routing:
        # CH 1 (index 0): Steering / Roll
        # CH 3 (index 2): Throttle / Pitch
        msg.channels[0] = steering
        msg.channels[2] = throttle

        self.rc_pub.publish(msg)

    def arm_vehicle(self, arm_state: bool):
        """Asynchronously commands vehicle ARM/DISARM state."""
        if not self.arm_client.wait_for_service(timeout_sec=0.5):
            self.get_logger().warn("Arming service unavailable!")
            return

        action_str = "Arming" if arm_state else "Disarming"
        self.get_logger().info(f"Sending {action_str} request...")

        req = CommandBool.Request()
        req.value = arm_state
        future = self.arm_client.call_async(req)
        future.add_done_callback(lambda f: self._arm_done_callback(f, arm_state))

    def _arm_done_callback(self, future, requested_state):
        try:
            res = future.result()
            state_str = "ARMED" if requested_state else "DISARMED"
            if res.success:
                self.is_armed = requested_state
                self.get_logger().info(f"Vehicle state changed: {state_str}")
            else:
                self.get_logger().warn(f"Vehicle REJECTED {state_str} command.")
        except Exception as e:
            self.get_logger().error(f"Arming service exception: {e}")

    def set_manual_mode(self):
        """Commands flight controller into MANUAL mode."""
        if not self.set_mode_client.wait_for_service(timeout_sec=0.5):
            self.get_logger().warn("SetMode service unavailable!")
            return

        req = SetMode.Request()
        req.custom_mode = "MANUAL"
        future = self.set_mode_client.call_async(req)
        future.add_done_callback(self._mode_done_callback)

    def _mode_done_callback(self, future):
        try:
            res = future.result()
            if res.mode_sent:
                self.get_logger().info("Mode set: MANUAL")
            else:
                self.get_logger().warn("Failed to set MANUAL mode.")
        except Exception as e:
            self.get_logger().error(f"SetMode exception: {e}")

    def emergency_disarm_and_release(self):
        """Releases all overrides and synchronizes a disarm request on exit."""
        self.get_logger().warn("Disarming vehicle and releasing RC override...")

        # 1. Release all RC overrides
        release_msg = OverrideRCIn()
        release_msg.channels = [0] * 18
        self.rc_pub.publish(release_msg)

        # 2. Synchronous disarm
        if self.arm_client.wait_for_service(timeout_sec=1.0):
            req = CommandBool.Request()
            req.value = False
            future = self.arm_client.call_async(req)
            rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)


def keyboard_input_loop(node: BlueBoatTeleop, original_settings):
    """Runs on the main thread, exclusively capturing keyboard events."""
    try:
        while rclpy.ok():
            # Put stdin into raw mode for instant single-char reads
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
            # Restore line settings immediately to keep logs legible
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original_settings)

            if not key:
                continue

            key = key.lower()

            if key == 'w':
                node.update_setpoints(throttle=node.PWM_FORWARD, steering=node.steering_pwm)
                node.get_logger().info("Throttle: FORWARD (1750 µs)")
            elif key == 'x':
                node.update_setpoints(throttle=node.PWM_REVERSE, steering=node.steering_pwm)
                node.get_logger().info("Throttle: REVERSE (1250 µs)")
            elif key == 'a':
                node.update_setpoints(throttle=node.throttle_pwm, steering=node.PWM_LEFT)
                node.get_logger().info("Steer: LEFT (1250 µs)")
            elif key == 'd':
                node.update_setpoints(throttle=node.throttle_pwm, steering=node.PWM_RIGHT)
                node.get_logger().info("Steer: RIGHT (1750 µs)")
            elif key == 's':
                node.update_setpoints(throttle=node.PWM_NEUTRAL, steering=node.PWM_NEUTRAL)
                node.get_logger().info("ALL STOP: Neutral (1500 µs)")
            elif key == 'q':
                node.arm_vehicle(True)
            elif key == 'e':
                node.update_setpoints(throttle=node.PWM_NEUTRAL, steering=node.PWM_NEUTRAL)
                node.arm_vehicle(False)
            elif key == 't':
                node.set_manual_mode()
            elif key == '\x03':  # CTRL+C
                node.get_logger().info("Exit key detected.")
                break

    except Exception as e:
        node.get_logger().error(f"Terminal loop error: {e}")
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original_settings)


def main(args=None):
    rclpy.init(args=args)
    node = BlueBoatTeleop()

    # Save original terminal mode
    original_settings = termios.tcgetattr(sys.stdin)

    # Spin ROS 2 executor in a daemon background thread
    ros_spin_thread = threading.Thread(
        target=rclpy.spin, 
        args=(node,), 
        daemon=True
    )
    ros_spin_thread.start()

    try:
        # Run terminal listener on the main thread
        keyboard_input_loop(node, original_settings)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original_settings)
        node.emergency_disarm_and_release()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        ros_spin_thread.join(timeout=1.0)


if __name__ == '__main__':
    main()