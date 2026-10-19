#!/usr/bin/env python3

import sys
import re
import math
import time
import select
import termios
import tty
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import PositionTarget
from mavros_msgs.srv import CommandBool, SetMode


class ROVBlockProgrammer(Node):
    def __init__(self):
        super().__init__('rov_block_programmer')

        # Publisher & Service Clients
        self.pub = self.create_publisher(PositionTarget, '/mavros/setpoint_raw/local', 10)
        self.arm_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.mode_client = self.create_client(SetMode, '/mavros/set_mode')

        # Subscriber for MAVROS Local Position Pose (Position & Orientation feedback)
        self.pose_sub = self.create_subscription(
            PoseStamped,
            '/mavros/local_position/pose',
            self.pose_callback,
            qos_profile_sensor_data
        )

        # 1479: Ignore PX, PY, PZ, AFX, AFY, AFZ, YAW. Only Vel + YawRate.
        self.type_mask = 1479

        # Current active velocity targets
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
        self.wz = 0.0

        # Depth / Altitude Hold (Z-Fix) state & parameters
        self.current_z = 0.0
        self.pose_received = False
        self.default_z = 0.0
        self.target_z = 0.0
        self.z_hold_active = False

        self.kp_z = 0.8
        self.max_vz = 0.4
        self.z_tolerance = 0.05
        self.z_deadband = 0.02
        self.z_timeout = 10.0

        # Heading / Yaw Hold (Yaw-Fix) state & parameters
        self.current_yaw = 0.0        # Current heading in radians (-pi to pi)
        self.target_yaw = 0.0         # Locked heading target in radians
        self.yaw_hold_active = False  # Active during linear moves and delays

        self.kp_yaw = 1.5             # Proportional gain for heading hold / turns
        self.max_wz = 0.6             # Max yaw rate clamp (rad/s)
        self.yaw_deadband = 0.03      # Deadband to prevent twitching (~1.7 degrees)
        self.yaw_tolerance = math.radians(2.0)  # Target reached tolerance for degree turns (2 degrees)
        self.yaw_timeout = 8.0        # Max seconds to wait on a turn block before moving on

        # Block Programmer parameters & storage
        self.block_speed = 0.2        # Default speed for movement blocks
        self.block_duration = 1.0     # Default duration per movement block (seconds)
        self.path_blocks = []         # List of programmed block tokens

        self.is_guided = False
        self.settings = termios.tcgetattr(sys.stdin)

        # Valid 4-DOF block commands
        self.valid_cmds = {
            'w': 'FORWARD (+vx)',
            'x': 'BACKWARD (-vx)',
            'a': 'SWAY LEFT (+vy)',
            'd': 'SWAY RIGHT (-vy)',
            'i': 'DESCEND / DOWN (-vz)',
            'k': 'ASCEND / UP (+vz)',
            's': 'HOLD / STOP XY (0.0)',
            'p': 'PAUSE / HOLD XY (0.0)'
        }

    # =========================================================================
    # MAVROS Callbacks, Service Calls & Setpoint Publishing
    # =========================================================================

    def pose_callback(self, msg: PoseStamped):
        self.current_z = msg.pose.position.z
        
        # Extract Yaw from quaternion (orientation)
        q = msg.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)
        
        self.pose_received = True

    def arm_vehicle(self, arm_state):
        if not self.arm_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('Arming service not available! Is MAVROS running?')
            return None

        req = CommandBool.Request(value=arm_state)
        future = self.arm_client.call_async(req)
        future.add_done_callback(self.arm_response_callback)

        action = "Arming" if arm_state else "Disarming"
        self.get_logger().info(f"{action} requested...")
        return future

    def arm_response_callback(self, future):
        try:
            response = future.result()
            if response.success:
                self.get_logger().info("Success! Vehicle arm state changed.")
            else:
                self.get_logger().warn("Failed to change arm state.")
        except Exception as e:
            self.get_logger().error(f"Arming service call failed: {e}")

    def toggle_mode(self):
        if not self.mode_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('SetMode service not available!')
            return None

        req = SetMode.Request()
        if self.is_guided:
            req.custom_mode = "MANUAL"
            self.is_guided = False
        else:
            req.custom_mode = "GUIDED"
            self.is_guided = True

        self.get_logger().info(f"Switching to {req.custom_mode} mode...")
        future = self.mode_client.call_async(req)
        future.add_done_callback(self.mode_response_callback)
        return future

    def mode_response_callback(self, future):
        try:
            response = future.result()
            if response.mode_sent:
                self.get_logger().info("Success! Flight mode changed.")
            else:
                self.get_logger().warn("Failed to change flight mode.")
        except Exception as e:
            self.get_logger().error(f"Mode service call failed: {e}")

    def reset_velocities(self):
        """Zeroes all 4-DOF velocities and disables active holds."""
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
        self.wz = 0.0
        self.z_hold_active = False
        self.yaw_hold_active = False

    def compute_depth_hold_vz(self):
        if not self.pose_received:
            return 0.0
        error = self.target_z - self.current_z
        if abs(error) <= self.z_deadband:
            return 0.0
        raw_vz = self.kp_z * error
        return round(max(-self.max_vz, min(self.max_vz, raw_vz)), 3)

    def compute_yaw_hold_wz(self):
        if not self.pose_received:
            return 0.0
        
        error = self.target_yaw - self.current_yaw
        while error > math.pi:
            error -= 2.0 * math.pi
        while error < -math.pi:
            error += 2.0 * math.pi

        if abs(error) <= self.yaw_deadband:
            return 0.0

        raw_wz = self.kp_yaw * error
        return round(max(-self.max_wz, min(self.max_wz, raw_wz)), 3)

    def apply_block_velocity(self, cmd):
        self.vx = 0.0
        self.vy = 0.0
        self.wz = 0.0
        spd = self.block_speed

        # Translation (Surge & Sway)
        if cmd == 'w':
            self.vx = spd
        elif cmd == 'x':
            self.vx = -spd
        elif cmd == 'a':
            self.vy = spd
        elif cmd == 'd':
            self.vy = -spd

        # Manual Depth Override Blocks
        elif cmd == 'i':
            self.vz = -spd
            return
        elif cmd == 'k':
            self.vz = spd
            return

        # Z-Hold update
        if self.z_hold_active:
            self.vz = self.compute_depth_hold_vz()
        else:
            self.vz = 0.0

        # Yaw-Hold update for linear/hold blocks
        if self.yaw_hold_active:
            self.wz = self.compute_yaw_hold_wz()
        else:
            self.wz = 0.0

    def publish_command(self):
        if self.z_hold_active:
            self.vz = self.compute_depth_hold_vz()
        if self.yaw_hold_active:
            self.wz = self.compute_yaw_hold_wz()

        m = PositionTarget()
        m.header.stamp = self.get_clock().now().to_msg()
        m.header.frame_id = 'base_link'
        m.coordinate_frame = PositionTarget.FRAME_BODY_NED
        m.type_mask = self.type_mask

        m.velocity.x = float(self.vx)
        m.velocity.y = float(self.vy)
        m.velocity.z = float(self.vz)
        m.yaw_rate = float(self.wz)

        self.pub.publish(m)

    # =========================================================================
    # Non-Blocking Terminal I/O
    # =========================================================================

    def get_key_with_heartbeat(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        key = sys.stdin.read(1) if rlist else ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)

        self.publish_command()
        rclpy.spin_once(self, timeout_sec=0.0)
        return key

    def read_line_with_heartbeat(self, prompt):
        sys.stdout.write(prompt)
        sys.stdout.flush()
        buf = []

        while rclpy.ok():
            key = self.get_key_with_heartbeat()
            if not key:
                continue

            if key == '\x03':  # CTRL+C
                raise KeyboardInterrupt
            elif key in ('\r', '\n'):
                sys.stdout.write('\n')
                sys.stdout.flush()
                return ''.join(buf).strip()
            elif key in ('\x7f', '\x08'):  # Backspace
                if buf:
                    buf.pop()
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            elif key.isprintable():
                buf.append(key)
                sys.stdout.write(key)
                sys.stdout.flush()
        return ''

    # =========================================================================
    # Block Programming & Parsing Functions (Supports z<depth>, t<seconds>, j<deg>, l<deg>)
    # =========================================================================

    def parse_sequence(self, seq_str):
        """
        Parses strings containing:
          - Depth targets: 'z-0.8'
          - Delay tokens: 't3'
          - Yaw turn tokens in degrees: 'j90' (turn left 90°), 'l45' (turn right 45°)
          - Standard movement blocks: 'w3', 'a2'
        """
        pattern = r'(z\s*[-+]?\d*\.?\d+)|(t\s*\d*\.?\d+)|(j\s*[-+]?\d*\.?\d*)|(l\s*[-+]?\d*\.?\d*)|([wxaiksp])\s*(\d*)'
        matches = re.findall(pattern, seq_str.lower())
        parsed = []

        for z_token, t_token, j_token, l_token, move_cmd, count_str in matches:
            if z_token:
                val = float(z_token[1:].strip())
                parsed.append(f"z{val:.2f}")
            elif t_token:
                val = float(t_token[1:].strip())
                parsed.append(f"t{val:.2f}")
            elif j_token:
                deg_str = j_token[1:].strip()
                deg = float(deg_str) if deg_str else 45.0  # Default to 45° if just 'j'
                parsed.append(f"j{deg:.1f}")
            elif l_token:
                deg_str = l_token[1:].strip()
                deg = float(deg_str) if deg_str else 45.0  # Default to 45° if just 'l'
                parsed.append(f"l{deg:.1f}")
            elif move_cmd:
                count = int(count_str) if count_str else 1
                parsed.extend([move_cmd] * count)

        return parsed

    def set_path(self, seq_str):
        blocks = self.parse_sequence(seq_str)
        if not blocks:
            self.get_logger().warn("No valid block commands found in input.")
            return
        self.path_blocks = blocks
        self.get_logger().info(f"Path programmed ({len(self.path_blocks)} blocks): {' -> '.join(self.path_blocks)}")

    def append_path(self, seq_str):
        blocks = self.parse_sequence(seq_str)
        if not blocks:
            self.get_logger().warn("No valid block commands found to append.")
            return
        self.path_blocks.extend(blocks)
        self.get_logger().info(f"Appended {len(blocks)} block(s). Total: {len(self.path_blocks)}")

    def insert_block(self, index, seq_str):
        blocks = self.parse_sequence(seq_str)
        if not blocks:
            self.get_logger().warn("No valid block commands found to insert.")
            return
        index = max(0, min(index, len(self.path_blocks)))
        self.path_blocks[index:index] = blocks
        self.get_logger().info(f"Inserted {len(blocks)} block(s) at index {index}.")

    def replace_block(self, index, cmd_str):
        blocks = self.parse_sequence(cmd_str)
        if not blocks or index < 0 or index >= len(self.path_blocks):
            self.get_logger().warn("Invalid index or command for replacement.")
            return
        self.path_blocks[index] = blocks[0]
        self.get_logger().info(f"Replaced index {index} with '{blocks[0]}'.")

    def delete_block(self, index):
        if 0 <= index < len(self.path_blocks):
            removed = self.path_blocks.pop(index)
            self.get_logger().info(f"Removed block '{removed}' at index {index}.")
        else:
            self.get_logger().warn("Index out of range.")

    def clear_path(self):
        self.path_blocks.clear()
        self.get_logger().info("Path cleared.")

    def configure_parameters(self, speed=None, duration=None, default_z=None, kp_z=None, kp_yaw=None, z_timeout=None):
        if speed is not None and speed > 0.0:
            self.block_speed = round(float(speed), 2)
        if duration is not None and duration > 0.0:
            self.block_duration = round(float(duration), 2)
        if default_z is not None:
            self.default_z = round(float(default_z), 2)
        if kp_z is not None and kp_z > 0.0:
            self.kp_z = round(float(kp_z), 2)
        if kp_yaw is not None and kp_yaw > 0.0:
            self.kp_yaw = round(float(kp_yaw), 2)
        if z_timeout is not None and z_timeout > 0.0:
            self.z_timeout = round(float(z_timeout), 1)

        self.get_logger().info(
            f"Updated -> Speed: {self.block_speed} | Duration: {self.block_duration}s | "
            f"Default Z: {self.default_z}m | Kp_z: {self.kp_z} | Kp_yaw: {self.kp_yaw} | Z-Timeout: {self.z_timeout}s"
        )

    # =========================================================================
    # Path Execution (Supports Depth, Delays, Degree Turns, and Heading Hold)
    # =========================================================================

    def execute_path(self):
        if not self.path_blocks:
            self.get_logger().warn("Path is empty! Program a path first.")
            return

        if not self.pose_received:
            self.get_logger().warn(
                "No /mavros/local_position/pose received yet! Z and Yaw holds will output 0.0 until pose arrives."
            )
        else:
            self.target_yaw = self.current_yaw

        total = len(self.path_blocks)
        self.target_z = self.default_z
        self.z_hold_active = True
        self.yaw_hold_active = True

        self.get_logger().info(
            f"=== STARTING PATH ({total} blocks | Initial Z: {self.target_z:.2f}m | Locked Yaw: {math.degrees(self.target_yaw):.1f}deg) ==="
        )
        self.get_logger().info("Press SPACE or 'S' at any time for Immediate Emergency Stop.")

        for idx, cmd in enumerate(self.path_blocks):
            # Case 1: Depth Target Block (e.g., 'z-0.80')
            if cmd.startswith('z'):
                new_z = float(cmd[1:])
                self.target_z = new_z
                self.vx = 0.0
                self.vy = 0.0
                self.wz = 0.0
                self.z_hold_active = True
                self.yaw_hold_active = True

                self.get_logger().info(
                    f"[Step {idx + 1}/{total}] SET DEPTH TARGET -> z = {self.target_z:.2f}m "
                    f"(Current Z: {self.current_z:.2f}m | Yaw Lock: {math.degrees(self.target_yaw):.1f}deg)"
                )

                start_time = time.monotonic()
                reached = False
                while (time.monotonic() - start_time) < self.z_timeout and rclpy.ok():
                    key = self.get_key_with_heartbeat()
                    if key == '\x03':
                        raise KeyboardInterrupt
                    elif key and key.lower() in (' ', 's'):
                        self.reset_velocities()
                        for _ in range(5):
                            self.publish_command()
                        self.get_logger().warn("!!! EMERGENCY ABORT TRIGGERED BY USER (ALL STOP) !!!")
                        return

                    if self.pose_received and abs(self.target_z - self.current_z) <= self.z_tolerance:
                        reached = True
                        self.get_logger().info(
                            f" -> Target depth {self.target_z:.2f}m reached! (Current Z: {self.current_z:.2f}m)"
                        )
                        break

                if not reached:
                    self.get_logger().warn(f" -> Depth timeout ({self.z_timeout}s) before reaching {self.target_z:.2f}m. Moving on...")

            # Case 2: Delay / Wait Block (e.g., 't3' for 3 seconds)
            elif cmd.startswith('t'):
                delay_sec = float(cmd[1:])
                self.vx = 0.0
                self.vy = 0.0
                self.wz = 0.0
                self.z_hold_active = True
                self.yaw_hold_active = True

                self.get_logger().info(
                    f"[Step {idx + 1}/{total}] DELAY / WAIT -> {delay_sec}s "
                    f"(Holding Depth Z={self.target_z:.2f}m & Yaw={math.degrees(self.target_yaw):.1f}deg)"
                )

                start_time = time.monotonic()
                while (time.monotonic() - start_time) < delay_sec and rclpy.ok():
                    key = self.get_key_with_heartbeat()
                    if key == '\x03':
                        raise KeyboardInterrupt
                    elif key and key.lower() in (' ', 's'):
                        self.reset_velocities()
                        for _ in range(5):
                            self.publish_command()
                        self.get_logger().warn("!!! EMERGENCY ABORT TRIGGERED BY USER (ALL STOP) !!!")
                        return

            # Case 3: Degree Turn Block (e.g., 'j90' for turn left 90°, 'l45' for turn right 45°)
            elif cmd.startswith('j') or cmd.startswith('l'):
                turn_deg = float(cmd[1:])
                turn_rad = math.radians(turn_deg)

                self.vx = 0.0
                self.vy = 0.0
                self.z_hold_active = True
                self.yaw_hold_active = True

                # Update target_yaw: Left (j) adds degrees, Right (l) subtracts degrees
                if cmd.startswith('j'):
                    self.target_yaw += turn_rad
                else:
                    self.target_yaw -= turn_rad

                # Normalize target_yaw to range [-pi, pi]
                while self.target_yaw > math.pi:
                    self.target_yaw -= 2.0 * math.pi
                while self.target_yaw < -math.pi:
                    self.target_yaw += 2.0 * math.pi

                direction = "LEFT" if cmd.startswith('j') else "RIGHT"
                self.get_logger().info(
                    f"[Step {idx + 1}/{total}] TURN {direction} -> {turn_deg}° "
                    f"(New Target Heading: {math.degrees(self.target_yaw):.1f}° | Timeout: {self.yaw_timeout}s)"
                )

                start_time = time.monotonic()
                reached = False
                while (time.monotonic() - start_time) < self.yaw_timeout and rclpy.ok():
                    key = self.get_key_with_heartbeat()
                    if key == '\x03':
                        raise KeyboardInterrupt
                    elif key and key.lower() in (' ', 's'):
                        self.reset_velocities()
                        for _ in range(5):
                            self.publish_command()
                        self.get_logger().warn("!!! EMERGENCY ABORT TRIGGERED BY USER (ALL STOP) !!!")
                        return

                    if self.pose_received:
                        error = self.target_yaw - self.current_yaw
                        while error > math.pi:
                            error -= 2.0 * math.pi
                        while error < -math.pi:
                            error += 2.0 * math.pi

                        if abs(error) <= self.yaw_tolerance:
                            reached = True
                            self.get_logger().info(
                                f" -> Heading {math.degrees(self.target_yaw):.1f}° reached! (Current Yaw: {math.degrees(self.current_yaw):.1f}°)"
                            )
                            break

                if not reached:
                    self.get_logger().warn(f" -> Turn timeout ({self.yaw_timeout}s) before reaching target heading. Moving on...")

            # Case 4: Standard 4-DOF Movement Block ('w', 'x', 'a', 'd', 'i', 'k', 's', 'p')
            else:
                if cmd in ('i', 'k'):
                    self.z_hold_active = False
                else:
                    self.z_hold_active = True

                self.yaw_hold_active = True  # Active heading hold for w, x, a, d, s, p

                self.apply_block_velocity(cmd)
                desc = self.valid_cmds.get(cmd, 'UNKNOWN')
                self.get_logger().info(
                    f"[Step {idx + 1}/{total}] '{cmd.upper()}' ({desc}) | "
                    f"Z: {self.target_z:.2f}m | Yaw Target: {math.degrees(self.target_yaw):.1f}° | "
                    f"vx={self.vx} vy={self.vy} vz={self.vz} wz={self.wz}"
                )

                start_time = time.monotonic()
                while (time.monotonic() - start_time) < self.block_duration and rclpy.ok():
                    if cmd in ('i', 'k'):
                        self.apply_block_velocity(cmd)
                    key = self.get_key_with_heartbeat()
                    if key == '\x03':
                        raise KeyboardInterrupt
                    elif key and key.lower() in (' ', 's'):
                        self.reset_velocities()
                        for _ in range(5):
                            self.publish_command()
                        self.get_logger().warn("!!! EMERGENCY ABORT TRIGGERED BY USER (ALL STOP) !!!")
                        return

                if cmd in ('i', 'k') and self.pose_received:
                    self.target_z = round(self.current_z, 2)
                    self.z_hold_active = True

        # Option B: Stop all thrusters and disable holds when run finishes
        self.reset_velocities()
        for _ in range(5):
            self.publish_command()
            time.sleep(0.02)
        self.get_logger().info("=== PATH EXECUTION COMPLETE: ALL VELOCITIES SET TO 0.0 (HOLDS OFF) ===")

    # =========================================================================
    # Interactive Menus
    # =========================================================================

    def print_status_banner(self):
        path_display = (
            " ".join([f"[{i}:{c}]" for i, c in enumerate(self.path_blocks)])
            if self.path_blocks else "(Empty)"
        )
        mode_str = "GUIDED" if self.is_guided else "MANUAL (Assumed)"
        pose_str = f"Z={self.current_z:.2f}m, Yaw={math.degrees(self.current_yaw):.1f}°" if self.pose_received else "WAITING FOR POSE..."
        print("\n" + "=" * 82)
        print("         4-DOF ROV BLOCK PROGRAMMER (DEPTH, DEGREE TURNS & DELAYS)")
        print("=" * 82)
        print(f" Mode Tracked : {mode_str} | Speed: {self.block_speed} | Block Duration: {self.block_duration}s")
        print(f" Live Pose    : {pose_str}")
        print(f" Controllers  : Kp_z={self.kp_z}, Kp_yaw={self.kp_yaw} | Default Z={self.default_z:.2f}m")
        print(f" Current Path : {path_display}")
        print("-" * 82)
        print(" Syntax       : z<val> (Depth)         | t<sec> (Delay e.g. t2.0)")
        print("                j<deg> (Turn Left e.g. j90) | l<deg> (Turn Right e.g. l45)")
        print("                W/X (Fwd/Back)           | A/D (Sway L/R) | I/K (Up/Down)")
        print("                Example Path: z-1.0 w3 j90 a2 t1.5 l45 w2 z0.0")
        print("-" * 82)
        print(" [1] Program New Path          [2] Edit / Adjust Path      [3] Configure Gains/Params")
        print(" [Z] Set Default Start Depth   [R] Run / Execute Path      [C] Clear Path")
        print(" [SPACE] ALL STOP (0.0)        [T] Toggle MANUAL/GUIDED    [Q/E] Arm / Disarm ROV")
        print(" [CTRL+C] Quit (Triggers Auto-Stop & Auto-Disarm Failsafe)")
        print("=" * 82)

    def handle_edit_submenu(self):
        print("\n--- EDIT PATH SUBMENU ---")
        print(" [A] Append to end | [I] Insert at index | [M] Modify/Replace index | [D] Delete index | [B] Back")
        choice = self.read_line_with_heartbeat("Select edit action: ").lower()

        if choice == 'a':
            seq = self.read_line_with_heartbeat("Enter blocks to append (e.g. j90 t2.0 w2): ")
            self.append_path(seq)
        elif choice == 'i':
            idx_str = self.read_line_with_heartbeat("Enter index to insert before: ")
            seq = self.read_line_with_heartbeat("Enter blocks to insert (e.g. l90 w2): ")
            if idx_str.isdigit():
                self.insert_block(int(idx_str), seq)
        elif choice == 'm':
            idx_str = self.read_line_with_heartbeat("Enter index to replace: ")
            seq = self.read_line_with_heartbeat("Enter new block (e.g. j90 or t3.0 or z-1.2): ")
            if idx_str.isdigit():
                self.replace_block(int(idx_str), seq)
        elif choice == 'd':
            idx_str = self.read_line_with_heartbeat("Enter index to delete: ")
            if idx_str.isdigit():
                self.delete_block(int(idx_str))


def main(args=None):
    rclpy.init(args=args)
    node = ROVBlockProgrammer()

    node.print_status_banner()

    try:
        while rclpy.ok():
            key = node.get_key_with_heartbeat()
            if not key:
                continue

            if key == '\x03':  # CTRL+C
                node.get_logger().info("CTRL+C detected. Initiating shutdown failsafes...")
                break

            k = key.lower()

            if k == '1':
                seq = node.read_line_with_heartbeat(
                    "\nEnter new path (e.g. z-1.0 w3 j90 a2 t2.0 l90 w2 z0): "
                )
                node.set_path(seq)
                node.print_status_banner()

            elif k == '2':
                node.handle_edit_submenu()
                node.print_status_banner()

            elif k == '3':
                spd_str = node.read_line_with_heartbeat(f"\nEnter block speed [current: {node.block_speed}]: ")
                dur_str = node.read_line_with_heartbeat(f"Enter block duration (s) [current: {node.block_duration}]: ")
                kp_z_str = node.read_line_with_heartbeat(f"Enter Z-Hold Kp gain [current: {node.kp_z}]: ")
                kp_yaw_str = node.read_line_with_heartbeat(f"Enter Yaw-Hold Kp gain [current: {node.kp_yaw}]: ")
                try:
                    spd = float(spd_str) if spd_str else None
                    dur = float(dur_str) if dur_str else None
                    kp_z = float(kp_z_str) if kp_z_str else None
                    kp_yaw = float(kp_yaw_str) if kp_yaw_str else None
                    node.configure_parameters(speed=spd, duration=dur, kp_z=kp_z, kp_yaw=kp_yaw)
                except ValueError:
                    node.get_logger().warn("Invalid numeric input. Keeping previous parameters.")
                node.print_status_banner()

            elif k == 'z':
                z_str = node.read_line_with_heartbeat(
                    f"\nEnter default starting Z target (0.0 = surface) "
                    f"[current: {node.default_z}m, live Z: {node.current_z:.2f}m]: "
                )
                try:
                    if z_str:
                        node.configure_parameters(default_z=float(z_str))
                except ValueError:
                    node.get_logger().warn("Invalid depth value.")
                node.print_status_banner()

            elif k == 'r':
                node.execute_path()
                node.print_status_banner()

            elif k == 'c':
                node.clear_path()
                node.print_status_banner()

            elif k == ' ':
                node.reset_velocities()
                node.publish_command()
                node.get_logger().info("ALL STOP (All velocities = 0.0, Holds OFF)")

            elif k == 't':
                node.toggle_mode()

            elif k == 'q':
                node.arm_vehicle(True)

            elif k == 'e':
                node.arm_vehicle(False)

    except KeyboardInterrupt:
        node.get_logger().info("KeyboardInterrupt caught. Running failsafe shutdown...")
    except Exception as e:
        node.get_logger().error(f"Unexpected runtime error: {e}")
    finally:
        node.reset_velocities()
        for _ in range(5):
            node.publish_command()
            time.sleep(0.02)

        if rclpy.ok():
            node.get_logger().warn("Failsafe: Disarming ROV before node exit...")
            disarm_future = node.arm_vehicle(False)
            if disarm_future is not None:
                timeout_start = time.monotonic()
                while not disarm_future.done() and (time.monotonic() - timeout_start) < 1.5:
                    rclpy.spin_once(node, timeout_sec=0.05)

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, node.settings)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()