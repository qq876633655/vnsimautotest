import time
from common.utils import axis_angle_to_rpy
from src.ecal_data import get_pose_stream, get_pose_once, start_ecal_listener

start_ecal_listener()


while True:
    time.sleep(2)
    pose = get_pose_once()
    print(pose)


# import multiprocessing
# import time
# import ecal.core.core as ecal_core
# from ecal.core.subscriber import ProtoSubscriber
# from src.proto_messages import pose_pb2
#
# def callback(topic_name, pose_msg, time):
#     global latest_pose
#     latest_pose = pose_msg
#
# ecal_core.initialize(sys.argv, "Simple Topic Waiter")
# sub = ProtoSubscriber("svc/pose", pose_pb2.Pose)
# sub.set_callback(callback)
# try:
#     while ecal_core.ok():
#         current_time = time.time()
#         # 每2秒打印一次最新消息
#         if current_time - last_print_time >= 2 and latest_pose is not None:
#             print(latest_pose)
#             # print(f"位置: x={latest_pose.position.x}, y={latest_pose.position.y}, z={latest_pose.position.z}")
#             last_print_time = current_time
#         time.sleep(0.1)  # 短暂休眠以减少CPU使用
#
# except KeyboardInterrupt:
#     print("用户中断...")
#
# finally:
#     # 清理
#     ecal_core.finalize()