from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    arg = LaunchConfiguration
    return LaunchDescription([
        DeclareLaunchArgument('env', default_value='coco',
                              description='uuv | usv | uav | coco, or a config .yaml path. '
                                          'Outputs go to /<env>/cv/objects'),
        DeclareLaunchArgument('model', default_value='', description='Override the model of the env'),
        DeclareLaunchArgument('camera_info', default_value='',
                              description='Fallback calibration .yaml until camera_info_topic arrives, '
                                          'default config/camera/bull_camera.yaml'),
        DeclareLaunchArgument('image_topic', default_value='/image_raw/compressed'),
        DeclareLaunchArgument('camera_info_topic', default_value='/camera_info'),
        DeclareLaunchArgument('conf', default_value='-1.0', description='Min score; < 0: the env\'s conf, else 0.25'),
        DeclareLaunchArgument('rate', default_value='15.0', description='Detections per second, on the newest frame'),
        DeclareLaunchArgument('debug_image', default_value='false',
                              description='Publish /<env>/cv/debug_image/compressed with boxes drawn'),

        Node(
            package='robotx_cv',
            executable='detector.py',
            output='screen',
            parameters=[{
                'env': arg('env'),
                'model': arg('model'),
                'camera_info': arg('camera_info'),
                'image_topic': arg('image_topic'),
                'camera_info_topic': arg('camera_info_topic'),
                # Typed so `conf:=1` or `rate:=10` are not passed as int.
                'conf': ParameterValue(arg('conf'), value_type=float),
                'rate': ParameterValue(arg('rate'), value_type=float),
                'debug_image': ParameterValue(arg('debug_image'), value_type=bool),
            }],
        ),
    ])
