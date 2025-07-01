import math

def quaternion_to_euler(q):
    w = q[0]
    x = q[1]
    y = q[2]
    z = q[3]
    yaw = math.atan2(2*(w*z + x*y), 1 - 2*(y*y + z*z))
    pitch = math.asin(2*(w*y - x*z))
    roll = math.atan2(2*(w*x + y*z), 1 - 2*(x*x + y*y))
    return roll, pitch, yaw

# 示例四元数
quaternion = [0, 0.7068252, 0, 0.7073883]
 
# 转换为旋转轴和角度
roll, pitch, yaw = quaternion_to_euler(quaternion)
 
print(f"Rotation {roll, pitch, yaw}")