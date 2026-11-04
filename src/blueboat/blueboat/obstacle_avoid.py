"""
Simple lidar obstacle avoidance that sits between the waypoint node and MAVROS.

  coord_list  --(/nav/setpoint_in)-->  obstacle_avoid  --(/mavros/setpoint_position/local)--> MAVROS

Run coord_list with its output remapped (no code change needed):
  ros2 run blueboat coord_list --ros-args -r /mavros/setpoint_position/local:=/nav/setpoint_in

Behaviour:
  CLEAR     : forward setpoints from the waypoint node unchanged.
  STOP      : obstacle inside the stop corridor -> hold current position for stop_hold_s.
  AVOID     : sidestep toward the freer side (left/right), then go back to CLEAR when
              the path is clear again. The waypoint node keeps its current target, so the
              boat resumes the waypoint after the sidestep.
  Failsafe  : no lidar data for lidar_timeout_s -> hold position.

Lidar frame assumed: x forward, y left, z up (RoboSense default). Use yaw_offset_deg if
the sensor is mounted rotated.
"""
import math
import time

import numpy as np
import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2


class ObstacleAvoid(Node):
    def __init__(self):
        super().__init__('obstacle_avoid')

        self.declare_parameter('cloud_topic', '/rslidar_points')
        self.declare_parameter('stop_dist', 2.0)         # m, obstacle closer than this -> stop
        self.declare_parameter('corridor_half_width', 0.8)  # m, half width of boat path to check
        self.declare_parameter('side_check_dist', 4.0)   # m, range used to pick the freer side
        self.declare_parameter('min_z', -0.3)            # m, lidar frame; reject water/own hull below
        self.declare_parameter('max_z', 2.0)
        self.declare_parameter('min_range', 0.8)         # m, ignore points on the boat itself
        self.declare_parameter('min_points', 8)          # points needed to count as an obstacle
        self.declare_parameter('stop_hold_s', 1.5)
        self.declare_parameter('sidestep_dist', 2.0)     # m, how far to sidestep
        self.declare_parameter('sidestep_angle_deg', 60.0)  # away from current heading
        self.declare_parameter('avoid_timeout_s', 10.0)
        self.declare_parameter('arrival_radius', 0.6)
        self.declare_parameter('lidar_timeout_s', 1.0)
        self.declare_parameter('yaw_offset_deg', 0.0)

        self.p = lambda n: self.get_parameter(n).value

        mavros_qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,
                                history=HistoryPolicy.KEEP_LAST, depth=10)
        self.create_subscription(PoseStamped, '/mavros/local_position/pose',
                                 self.pose_cb, mavros_qos)
        self.create_subscription(PoseStamped, '/nav/setpoint_in', self.setpoint_cb, 10)
        self.create_subscription(PointCloud2, self.p('cloud_topic'),
                                 self.cloud_cb, qos_profile_sensor_data)
        self.out_pub = self.create_publisher(PoseStamped, '/mavros/setpoint_position/local', 10)

        self.x = self.y = self.z = self.yaw = 0.0
        self.have_pose = False
        self.requested = None          # last setpoint from waypoint node
        self.blocked = False
        self.left_free = self.right_free = 0.0
        self.last_cloud = 0.0

        self.state = 'CLEAR'
        self.state_since = time.time()
        self.hold_pose = None
        self.avoid_target = None

        self.create_timer(0.1, self.loop)
        self.get_logger().info('obstacle_avoid ready (waiting for lidar + pose)')

    # ---------- inputs ----------
    def pose_cb(self, msg):
        p, q = msg.pose.position, msg.pose.orientation
        self.x, self.y, self.z = p.x, p.y, p.z
        self.yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
        self.have_pose = True

    def setpoint_cb(self, msg):
        self.requested = msg

    def cloud_cb(self, msg):
        self.last_cloud = time.time()
        pts = point_cloud2.read_points(msg, field_names=('x', 'y', 'z'), skip_nans=True)
        if pts.dtype.names:  # structured array (Humble)
            pts = np.stack([pts['x'], pts['y'], pts['z']], axis=1)
        pts = np.asarray(pts, dtype=np.float32)
        if pts.size == 0:
            self.blocked, self.left_free, self.right_free = False, 99.0, 99.0
            return

        off = math.radians(self.p('yaw_offset_deg'))
        if off:
            c, s = math.cos(off), math.sin(off)
            pts = np.stack([c * pts[:, 0] - s * pts[:, 1],
                            s * pts[:, 0] + c * pts[:, 1], pts[:, 2]], axis=1)

        rng = np.hypot(pts[:, 0], pts[:, 1])
        ok = (rng > self.p('min_range')) & (pts[:, 2] > self.p('min_z')) & \
             (pts[:, 2] < self.p('max_z')) & (pts[:, 0] > 0.0)
        pts = pts[ok]

        in_corr = (pts[:, 0] < self.p('stop_dist')) & \
                  (np.abs(pts[:, 1]) < self.p('corridor_half_width'))
        self.blocked = int(in_corr.sum()) >= self.p('min_points')

        # clearance on each side: nearest point in a forward-side wedge (bigger = freer)
        d = self.p('side_check_dist')
        near = pts[(pts[:, 0] < d) & (np.abs(pts[:, 1]) < d)]
        left = near[near[:, 1] > 0.3]
        right = near[near[:, 1] < -0.3]
        self.left_free = float(np.min(np.hypot(left[:, 0], left[:, 1]))) if len(left) else 99.0
        self.right_free = float(np.min(np.hypot(right[:, 0], right[:, 1]))) if len(right) else 99.0

    # ---------- outputs ----------
    def publish(self, x, y, z):
        m = PoseStamped()
        m.header.stamp = self.get_clock().now().to_msg()
        m.header.frame_id = 'map'
        m.pose.position.x, m.pose.position.y, m.pose.position.z = x, y, z
        self.out_pub.publish(m)

    def set_state(self, s):
        if s != self.state:
            self.get_logger().info(f'{self.state} -> {s}')
        self.state, self.state_since = s, time.time()

    def loop(self):
        if not self.have_pose:
            return
        now = time.time()

        # failsafe: lidar lost -> hold position
        if now - self.last_cloud > self.p('lidar_timeout_s'):
            if self.requested is not None:
                self.get_logger().warn('No lidar data - holding position', throttle_duration_sec=2.0)
                self.publish(self.x, self.y, self.z)
            return

        if self.state == 'CLEAR':
            if self.blocked and self.requested is not None:
                self.hold_pose = (self.x, self.y, self.z)
                self.set_state('STOP')
            elif self.requested is not None:
                self.out_pub.publish(self.requested)

        elif self.state == 'STOP':
            self.publish(*self.hold_pose)
            if now - self.state_since >= self.p('stop_hold_s'):
                if not self.blocked:
                    self.set_state('CLEAR')
                    return
                # pick freer side (more clearance); tie -> right (COLREGS-style)
                sign = 1.0 if self.left_free > self.right_free else -1.0
                ang = self.yaw + sign * math.radians(self.p('sidestep_angle_deg'))
                d = self.p('sidestep_dist')
                self.avoid_target = (self.x + d * math.cos(ang), self.y + d * math.sin(ang), self.z)
                self.get_logger().info(
                    f"Avoiding {'LEFT' if sign > 0 else 'RIGHT'} "
                    f'(left_free={self.left_free:.1f}m right_free={self.right_free:.1f}m)')
                self.set_state('AVOID')

        elif self.state == 'AVOID':
            self.publish(*self.avoid_target)
            dist = math.hypot(self.avoid_target[0] - self.x, self.avoid_target[1] - self.y)
            timed_out = now - self.state_since > self.p('avoid_timeout_s')
            if dist <= self.p('arrival_radius') or timed_out:
                if timed_out:
                    self.get_logger().warn('Avoid timed out')
                self.set_state('CLEAR' if not self.blocked else 'STOP')
                if self.state == 'STOP':
                    self.hold_pose = (self.x, self.y, self.z)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoid()
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
