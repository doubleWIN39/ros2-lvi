cmake_minimum_required(VERSION 3.8)
project(lvi_sam)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_BUILD_TYPE "Release")

# --- Dependencies ---
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(image_transport REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(pcl_conversions REQUIRED)
find_package(PCL REQUIRED COMPONENTS kdtree filters)
find_package(OpenCV REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(Ceres REQUIRED)
find_package(GTSAM REQUIRED)
find_package(Boost REQUIRED COMPONENTS atomic filesystem program_options system timer)
find_package(OpenMP REQUIRED)
find_package(rosbag2_cpp REQUIRED)
find_package(lvi_sam_msgs REQUIRED)

# --- Include Directories ---
include_directories(
  include
  ${PCL_INCLUDE_DIRS}
  ${EIGEN3_INCLUDE_DIR}
  ${OpenCV_INCLUDE_DIRS}
  ${CERES_INCLUDE_DIRS}
  ${Boost_INCLUDE_DIRS}
  ${GTSAM_INCLUDE_DIR}
  ${rclcpp_INCLUDE_DIRS}
  ${lvi_sam_msgs_INCLUDE_DIRS}
)

link_directories(
  ${PCL_LIBRARY_DIRS}
  ${OpenCV_LIBRARY_DIRS}
  ${GTSAM_LIBRARY_DIRS}
)

add_definitions(${PCL_DEFINITIONS})

# ==============================================================================
# Visual Modules (相机模型与视觉惯性里程计)
# ==============================================================================

# 1. 构建相机模型库
file(GLOB_RECURSE camera_model_src "src/visual_odometry/visual_feature/camera_models/*.cc")
add_library(camera_model_lib STATIC ${camera_model_src})
ament_target_dependencies(camera_model_lib rclcpp OpenCV Eigen3)

# 2. 定义源文件集合
file(GLOB_RECURSE visual_feature_files "src/visual_odometry/visual_feature/*.cpp")
file(GLOB_RECURSE visual_estimator_files "src/visual_odometry/visual_estimator/*.cpp")
file(GLOB_RECURSE visual_loop_files "src/visual_odometry/visual_loop/*.cpp")

# 3. visual_feature (去掉了 _node)
add_executable(visual_feature ${visual_feature_files})
target_link_libraries(visual_feature camera_model_lib ${PCL_LIBRARIES} ${OpenCV_LIBS} ${CERES_LIBRARIES})
ament_target_dependencies(visual_feature rclcpp std_msgs sensor_msgs geometry_msgs nav_msgs visualization_msgs cv_bridge tf2 tf2_geometry_msgs pcl_conversions lvi_sam_msgs)

# 4. visual_estimator (去掉了 _node)
add_executable(visual_estimator ${visual_estimator_files})
target_link_libraries(visual_estimator camera_model_lib ${PCL_LIBRARIES} ${OpenCV_LIBS} ${CERES_LIBRARIES})
ament_target_dependencies(visual_estimator rclcpp std_msgs sensor_msgs geometry_msgs nav_msgs visualization_msgs cv_bridge tf2 tf2_geometry_msgs pcl_conversions lvi_sam_msgs)

# 5. visual_loop (去掉了 _node)
add_executable(visual_loop ${visual_loop_files})
target_link_libraries(visual_loop camera_model_lib ${PCL_LIBRARIES} ${OpenCV_LIBS} ${CERES_LIBRARIES})
ament_target_dependencies(visual_loop rclcpp std_msgs sensor_msgs geometry_msgs nav_msgs visualization_msgs cv_bridge tf2 tf2_geometry_msgs pcl_conversions lvi_sam_msgs)


# ==============================================================================
# Lidar Modules (激光雷达里程计与优化)
# ==============================================================================

# 1. imu_preintegration
add_executable(imu_preintegration src/lidar_odometry/imuPreintegration.cpp)
target_link_libraries(imu_preintegration ${PCL_LIBRARIES} ${OpenCV_LIBRARIES} gtsam Boost::timer Boost::atomic)
ament_target_dependencies(imu_preintegration rclcpp std_msgs sensor_msgs geometry_msgs nav_msgs visualization_msgs cv_bridge tf2 tf2_geometry_msgs pcl_conversions lvi_sam_msgs rosbag2_cpp)

# 2. image_projection
add_executable(image_projection src/lidar_odometry/imageProjection.cpp)
target_link_libraries(image_projection ${PCL_LIBRARIES} ${OpenCV_LIBRARIES})
ament_target_dependencies(image_projection rclcpp std_msgs sensor_msgs geometry_msgs nav_msgs visualization_msgs cv_bridge tf2 tf2_geometry_msgs pcl_conversions lvi_sam_msgs rosbag2_cpp)

# 3. feature_extraction
add_executable(feature_extraction src/lidar_odometry/featureExtraction.cpp)
target_link_libraries(feature_extraction ${PCL_LIBRARIES} ${OpenCV_LIBRARIES})
ament_target_dependencies(feature_extraction rclcpp std_msgs sensor_msgs geometry_msgs nav_msgs visualization_msgs cv_bridge tf2 tf2_geometry_msgs pcl_conversions lvi_sam_msgs rosbag2_cpp)

# 4. map_optimization
add_executable(map_optmization src/lidar_odometry/mapOptmization.cpp)
target_compile_options(map_optmization PRIVATE -fopenmp)
target_link_libraries(map_optmization ${PCL_LIBRARIES} ${OpenCV_LIBRARIES} gtsam Boost::timer OpenMP::OpenMP_CXX Boost::atomic)
ament_target_dependencies(map_optmization rclcpp std_msgs sensor_msgs geometry_msgs nav_msgs visualization_msgs cv_bridge tf2 tf2_geometry_msgs pcl_conversions lvi_sam_msgs rosbag2_cpp)

# 5. pcap_publisher
add_executable(pcap_publisher src/lidar_odometry/pcap_publisher_node.cpp)
target_link_libraries(pcap_publisher ${PCL_LIBRARIES} ${OpenCV_LIBRARIES} pcap gtsam Boost::timer Boost::atomic)
ament_target_dependencies(pcap_publisher rclcpp std_msgs sensor_msgs geometry_msgs nav_msgs visualization_msgs cv_bridge tf2 tf2_geometry_msgs pcl_conversions lvi_sam_msgs rosbag2_cpp image_transport)

# 6. trajectory
add_executable(trajectory src/lidar_odometry/trajectory2D.cpp)
target_link_libraries(trajectory ${PCL_LIBRARIES} ${OpenCV_LIBRARIES} gtsam Boost::timer Boost::atomic)
ament_target_dependencies(trajectory rclcpp std_msgs sensor_msgs geometry_msgs nav_msgs visualization_msgs cv_bridge tf2 tf2_geometry_msgs pcl_conversions lvi_sam_msgs rosbag2_cpp image_transport)

# ==============================================================================
# Install & Package
# ==============================================================================

# 安装目标名必须与上面 add_executable 定义的一致
install(TARGETS
  visual_feature visual_estimator visual_loop
  imu_preintegration image_projection feature_extraction
  map_optmization pcap_publisher trajectory
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch urdf rviz config DESTINATION share/${PROJECT_NAME})

ament_export_dependencies(rosidl_default_runtime)
ament_package()
