
import sys
import time

import ecal.core.core as ecal_core
from ecal.core.subscriber import ProtoSubscriber

import sys,os
# from src.src_test2 import Test2
sys.path.append(r'..')

# from proto_messages import transfer_pb2
from proto_messages import pose_pb2
from proto_messages import Vector3_pb2
from proto_messages import Quaternion_pb2
from proto_messages import transfer_pb2

import proto_messages.transfer_pb2 as transfer_pb2
from proto_messages import Quaternion_pb2
from proto_messages import transfer_pb2
#
import csv
import os
from datetime import datetime
from threading import Lock

from datetime import datetime


class DataWriter:
    def __init__(self):
        self.buffer = []
        self.lock = Lock()
        self.file_path = '/path/to/your/file.txt'
        self.flush_interval = 1000000  # Interval in ns
        self.last_flush_time = ecal_core.getmicroseconds()[1]
        self.pose_timestamp = 0
        self.position = [0,1,2]

    def callback(self,topic_name, pose_proto_msg, time):
        print(pose_proto_msg)

        # with self.lock:
        #     self.buffer.append(pose_proto_msg.position)

    def write_to_file(self):
        with open(self.file_path, 'a') as file:
            posewriter = csv.writer(file,)

    def listener(self):
        ecal_core.initialize(sys.argv, "Python Protobuf Subscriber")
        sub = ProtoSubscriber("webot/transfer", transfer_pb2.MTransfer)
        sub.set_callback(self.callback)

        while ecal_core.ok():
            if ecal_core.getmicroseconds()[1]- self.last_flush_time > self.flush_interval:
                # self.write_to_file()
                print(self.pose_timestamp)
                print(self.position)
                self.last_flush_time = ecal_core.getmicroseconds()[1]
            time.sleep(0.1)

        ecal_core.finalize()


if __name__ == "__main__":

    # writer = DataWriter()
    # writer.listener()
    print("ecal_core.getmicroseconds()[1]")

# import sys
# import time

# import ecal.core.core as ecal_core
# from ecal.core.subscriber import ProtoSubscriber

# import sys,os
# # from src.src_test2 import Test2
# sys.path.append(r'..')

# from proto_messages import transfer_pb2
from proto_messages import pose_pb2
from proto_messages import Vector3_pb2
from proto_messages import Quaternion_pb2
from proto_messages import transfer_pb2

# import csv
# import os
# from datetime import datetime
# from threading import Lock

from datetime import datetime

# class DataWriter:
#     def __init__(self):
#         self.buffer = []
#         self.lock = Lock()
#         self.file_path = '/path/to/your/file.txt'
#         self.flush_interval = 1000000  # Interval in ns
#         self.last_flush_time = ecal_core.getmicroseconds()[1]
#         self.pose_timestamp = 0
#         self.position = [0,1,2]

#     def callback(self,topic_name, pose_proto_msg, time):
#         print(pose_proto_msg)

#         # with self.lock:
#         #     self.buffer.append(pose_proto_msg.position)

#     def write_to_file(self):
#         with open(self.file_path, 'a') as file:
#             posewriter = csv.writer(file,)

#     def listener(self):
#         ecal_core.initialize(sys.argv, "Python Protobuf Subscriber")
#         sub = ProtoSubscriber("webot/transfer", transfer_pb2.MTransfer)
#         sub.set_callback(self.callback)

#         while ecal_core.ok():
#             if ecal_core.getmicroseconds()[1]- self.last_flush_time > self.flush_interval:
#                 # self.write_to_file()
#                 print(self.pose_timestamp)
#                 print(self.position)
#                 self.last_flush_time = ecal_core.getmicroseconds()[1]
#             time.sleep(0.1)

#         ecal_core.finalize()


# if __name__ == "__main__":

#     writer = DataWriter()
#     writer.listener()
#     # print(ecal_core.getmicroseconds()[1])