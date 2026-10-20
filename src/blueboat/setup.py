from setuptools import find_packages, setup

package_name = 'blueboat'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='divy',
    maintainer_email='divyeshsaraff@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'manual_control_teleop=blueboat.manual_control_teleop:main',
            'teleop_guided=blueboat.teleop_test:main',
            'local_pub_one=blueboat.local_pub_onee:main',
            'rviz_mapper=blueboat.rviz_mapper:main',
            'coord_list=blueboat.coord_list:main',
            'movement_recorder=blueboat.movement_recorder:main',
            'rov_teleop=blueboat.teleop_cmdvel_rov:main',
            'neopixel_light=blueboat.mavros_serial_led_controller:main',
            'rov_programmer=blueboat.rov_programmer:main'
        ],
    },
)
