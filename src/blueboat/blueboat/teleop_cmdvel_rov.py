#!/usr/bin/env python3

import sys
import select
import termios
import tty
import rclpy
from rclpy.node import Node
from mavros_msgs.msg import PositionTarget
from mavros_msgs.srv import CommandBool, SetMode

class PositionTargetTeleop(Node):
    def __init__(self):
        super().__init__('pos_target_teleop')
        
        self.pub = self.create_publisher(PositionTarget, '/mavros/setpoint_raw/local', 10)
        self.arm_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.mode_client = self.create_client(SetMode, '/mavros/set_mode')
        
        # 1479: Ignore PX, PY, PZ, AFX, AFY, AFZ, YAW. Only Vel + YawRate.
        self.type_mask = 1479
        
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
        self.wz = 0.0
        
        self.is_guided = False

    def arm_vehicle(self, arm_state):
        if not self.arm_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('Arming service not available!')
            return
        
        req = CommandBool.Request(value=arm_state)
        fut = self.arm_client.call_async(req)
        
        action = "Arming" if arm_state else "Disarming"
        self.get_logger().info(f"{action} requested...")

    def toggle_mode(self):
        if not self.mode_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('SetMode service not available!')
            return
            
        req = SetMode.Request()
        if self.is_guided:
            req.custom_mode = "MANUAL"
            self.is_guided = False
        else:
            req.custom_mode = "GUIDED"
            self.is_guided = True
            
        self.get_logger().info(f"Switching to {req.custom_mode} mode...")
        self.mode_client.call_async(req)

    def publish_command(self):
        m = PositionTarget()
        m.header.stamp = self.get_clock().now().to_msg()
        m.header.frame_id = 'base_link'
        m.coordinate_frame = PositionTarget.FRAME_BODY_NED
        m.type_mask = self.type_mask
        
        # Inject velocities (matching land test FLU logic)
        m.velocity.x = self.vx
        m.velocity.y = self.vy
        m.velocity.z = self.vz
        m.yaw_rate = self.wz
        
        self.pub.publish(m)

def main(args=None):
    rclpy.init(args=args)
    node = PositionTargetTeleop()
    settings = termios.tcgetattr(sys.stdin)
    
    node.get_logger().info("4-DOF PositionTarget Teleop Started.")
    node.get_logger().info("W/S: Forward/Back | A/D: Sway Left/Right | I/K: Up/Down | J/L: Yaw Left/Right")
    node.get_logger().info("SPACE: ALL STOP | T: Toggle Mode | Q/E: Arm/Disarm | CTRL+C: Quit")

    try:
        while rclpy.ok():
            tty.setraw(sys.stdin.fileno())
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1) 
            key = sys.stdin.read(1) if rlist else ''
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

            if key:
                k = key.lower()
                step = 0.1
                
                # Translation
                if k == 'w': node.vx = round(node.vx + step, 1)
                elif k == 's': node.vx = round(node.vx - step, 1)
                elif k == 'a': node.vy = round(node.vy + step, 1)
                elif k == 'd': node.vy = round(node.vy - step, 1)
                
                # Depth (Note: Land test used negative Z for UP)
                elif k == 'i': node.vz = round(node.vz - step, 1)
                elif k == 'k': node.vz = round(node.vz + step, 1)
                
                # Rotation
                elif k == 'j': node.wz = round(node.wz + step, 1)
                elif k == 'l': node.wz = round(node.wz - step, 1)
                
                # System & Safety
                elif k == ' ': 
                    node.vx = node.vy = node.vz = node.wz = 0.0
                    node.get_logger().info("ALL STOP")
                elif k == 't': node.toggle_mode()
                elif k == 'q': node.arm_vehicle(True)
                elif k == 'e': node.arm_vehicle(False)
                elif key == '\x03': break
                
                if k in 'wsadikjl':
                    node.get_logger().info(f"Target: vx={node.vx} vy={node.vy} vz={node.vz} wz={node.wz}")
            
            node.publish_command()
            rclpy.spin_once(node, timeout_sec=0.0)

    except Exception as e:
        node.get_logger().error(f"Error: {e}")
    finally:
        node.vx = node.vy = node.vz = node.wz = 0.0
        for _ in range(5):
            node.publish_command()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()