from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    arg = LaunchConfiguration
    return LaunchDescription([
        DeclareLaunchArgument('config', default_value='usv_task1',
                              description='<vehicle>_task1 in config/, or a .yaml path; outputs on /<vehicle>/task1/'),
        DeclareLaunchArgument('model', default_value='', description='Override the model of the config'),
        DeclareLaunchArgument('camera_info', default_value='',
                              description='Fallback calibration .yaml until camera_info_topic arrives, '
                                          'default config/camera/bull_camera.yaml'),
        DeclareLaunchArgument('image_topic', default_value='/image_raw/compressed'),
        DeclareLaunchArgument('camera_info_topic', default_value='/camera_info'),
        DeclareLaunchArgument('depth_topic', default_value='/depth/image_raw',
                              description='Depth image aligned to the colour image (16UC1 mm or 32FC1 m)'),
        DeclareLaunchArgument('conf', default_value='-1.0', description='Min score; < 0: the config\'s conf'),
        DeclareLaunchArgument('rate', default_value='15.0', description='Detections per second, on the newest frame'),
        DeclareLaunchArgument('debug_image', default_value='false',
                              description='Publish /<vehicle>/task1/debug_image/compressed'),
        DeclareLaunchArgument('ros_frame', default_value='true',
                              description='Deproject to the ROS camera body frame (x forward, y left, z up); '
                                          'false: optical frame (x right, y down, z forward)'),

        Node(
            package='robotx_cv',
            executable='task1.py',
            output='screen',
            parameters=[{
                'config': arg('config'),
                'model': arg('model'),
                'camera_info': arg('camera_info'),
                'image_topic': arg('image_topic'),
                'camera_info_topic': arg('camera_info_topic'),
                'depth_topic': arg('depth_topic'),
                'conf': ParameterValue(arg('conf'), value_type=float),
                'rate': ParameterValue(arg('rate'), value_type=float),
                'debug_image': ParameterValue(arg('debug_image'), value_type=bool),
                'ros_frame': ParameterValue(arg('ros_frame'), value_type=bool),
            }],
        ),
    ])
