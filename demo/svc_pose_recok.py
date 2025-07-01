
import sys
import time

import ecal.core.core as ecal_core
from ecal.core.subscriber import ProtoSubscriber

# Import the "hello_world_pb2.py" file that we have just generated from the
# proto_messages directory 
# import proto_messages.hello_world_pb2 as hello_world_pb2
import sim_data_flow.pose_pb2 as pose_pb2

import csv
import os
from datetime import datetime
from threading import Lock


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
        # print("timestamp {} \nposition {}orientation {}".format(pose_proto_msg.timestamp
#                                     , pose_proto_msg.position
#                                     , pose_proto_msg.orientation))
        self.pose_timestamp = pose_proto_msg.timestamp
        self.position[0] = pose_proto_msg.position.x
        self.position[1] = pose_proto_msg.position.y
        self.position[2] = pose_proto_msg.position.z
        # with self.lock:
        #     self.buffer.append(pose_proto_msg.position)
        
    def write_to_file(self):
        with open(self.file_path, 'a') as file:
            posewriter = csv.writer(file,)

    def listener(self):
        ecal_core.initialize(sys.argv, "Python Protobuf Subscriber")
        sub = ProtoSubscriber("svc/pose"
                    , pose_pb2.Pose)
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

    writer = DataWriter()
    writer.listener()
    # print(ecal_core.getmicroseconds()[1])