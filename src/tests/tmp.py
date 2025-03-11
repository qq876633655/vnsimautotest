import math
import numpy as np
 
def quat_to_axis_angle(quat):
    # 四元数标准化
    quat = quat / np.linalg.norm(quat)
    
    # 实部对应角度
    angle = 2 * math.acos(quat[0])
    
    # 虚部对应旋转轴
    axis = quat[1:]/math.sin(angle/2)
    
    return axis, angle
 
# 示例四元数
quaternion = np.array([0.35535, 0.46194, 0.13583, 0.80175])
 
# 转换为旋转轴和角度
axis, angle = quat_to_axis_angle(quaternion)
 
print(f"Rotation axis: {axis}, Angle: {angle}")