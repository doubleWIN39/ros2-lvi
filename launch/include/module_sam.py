from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    lvi_sam_dir = get_package_share_directory('lvi_sam')

    # 确保这些文件在你的 config 文件夹里真实存在
    lidar_config = os.path.join(lvi_sam_dir, 'config', 'params_lidar.yaml')
    config_file = os.path.join(lvi_sam_dir, 'config', 'params_camera.yaml')
    pattern_file = os.path.join(lvi_sam_dir, 'config', 'brief_pattern.yaml')

    return LaunchDescription([
        # 1. 激光雷达投影
        Node(
            package='lvi_sam',
            executable='image_projection', # 去掉 _node
            name='image_projection',
            output='screen',
            parameters=[lidar_config]
        ),

        # 2. 特征提取
        Node(
            package='lvi_sam',
            executable='feature_extraction', # 去掉 _node
            name='feature_extraction',
            output='screen',
            parameters=[lidar_config]
        ),

        # 3. 地图优化
        Node(
            package='lvi_sam',
            executable='map_optmization', # 注意：根据你CMake里的拼写是 optmization
            name='map_optmization',
            output='screen',
            parameters=[lidar_config]
        ),

        # 4. IMU 预积分
        Node(
            package='lvi_sam',
            executable='imu_preintegration', # 去掉 _node
            name='imu_preintegration',
            output='screen',
            parameters=[lidar_config]
        ),

        # 5. 视觉估计器
        Node(
            package='lvi_sam',
            executable='visual_estimator', # 去掉 _node
            name='visual_estimator',
            output='screen',
            parameters=[config_file, pattern_file]
        ),

        # 6. 视觉特征提取
        Node(
            package='lvi_sam',
            executable='visual_feature', # 去掉 _node
            name='visual_feature',
            output='screen',
            parameters=[config_file, pattern_file]
        ),

        # 7. 视觉回环检测
        Node(
            package='lvi_sam',
            executable='visual_loop', # 去掉 _node
            name='visual_loop',
            output='screen',
            parameters=[config_file, pattern_file]
        )
    ])
