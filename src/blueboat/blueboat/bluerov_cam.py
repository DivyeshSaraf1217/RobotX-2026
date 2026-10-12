#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from sensor_msgs.msg import CompressedImage

class BlueROVCameraNode(Node):
    def __init__(self):
        super().__init__('bluerov_camera_publisher')

        self.declare_parameter('rtsp_url', 'rtsp://192.168.2.2:8554/video_stream__dev_video0')
        self.declare_parameter('topic_name', '/bluerov2/camera/color/image_raw/compressed')
        self.declare_parameter('frame_id', 'camera_optical_link')
        self.declare_parameter('jpeg_quality', 80)

        rtsp_url = self.get_parameter('rtsp_url').value
        topic_name = self.get_parameter('topic_name').value
        self.frame_id = self.get_parameter('frame_id').value
        self.jpeg_quality = self.get_parameter('jpeg_quality').value

        self.publisher_ = self.create_publisher(CompressedImage, topic_name, 10)

        # 1. Reliable GStreamer pipeline with TCP transport and auto-decoding
        gst_pipeline = (
            f"rtspsrc location={rtsp_url} protocols=tcp latency=200 ! "
            "rtph264depay ! h264parse ! avdec_h264 ! "
            "videoconvert ! video/x-raw, format=BGR ! "
            "appsink drop=true sync=false max-buffers=1"
        )

        self.get_logger().info(f"Opening RTSP stream: {rtsp_url}")
        
        # Try GStreamer first, fallback to standard FFmpeg backend if GStreamer fails
        self.cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

        if not self.cap.isOpened():
            self.get_logger().warn("GStreamer backend failed. Falling back to native OpenCV RTSP reader...")
            self.cap = cv2.VideoCapture(rtsp_url)

        if not self.cap.isOpened():
            self.get_logger().error(f"Failed to connect to RTSP stream at: {rtsp_url}")
            return

        self.timer = self.create_timer(1.0 / 30.0, self.timer_callback)
        self.get_logger().info(f"Publishing stream to: {topic_name}")

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.get_logger().warn("Waiting for incoming RTSP frames...", throttle_duration_sec=2)
            return

        # Encode to JPEG
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality]
        success, encoded_img = cv2.imencode('.jpg', frame, encode_param)
        if not success:
            return

        # Publish sensor_msgs/CompressedImage
        msg = CompressedImage()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id
        msg.format = "jpeg"
        msg.data = np.array(encoded_img).tobytes()

        self.publisher_.publish(msg)

    def destroy_node(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = BlueROVCameraNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()