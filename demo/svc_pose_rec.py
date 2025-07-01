
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
        self.flush_interval = 10  # Interval in seconds
        self.last_flush_time = 0

    def callback(self,topic_name, pose_proto_msg, time):
          # print("timestamp {} \nposition {}orientation {}".format(pose_proto_msg.timestamp
  #                                     , pose_proto_msg.position
  #                                     , pose_proto_msg.orientation))
        with self.lock:
            self.buffer.append(pose_proto_msg.position)
        
    def write_to_file(self):
        with self.lock:
            with open(self.file_path, 'a') as file:
                for data in self.buffer:
                    file.write(data + '\n')
            self.buffer = []

    def listener(self):
        ecal_core.initialize(sys.argv, "Python Protobuf Subscriber")
        sub = ProtoSubscriber("svc/pose"
                    , pose_pb2.Pose)
        sub.set_callback(self.callback)

        # rospy.init_node('data_writer_node', anonymous=True)
        # rospy.Subscriber('your_topic', String, self.callback)
        # rate = rospy.Rate(1)  # Check interval (1 Hz)
        while ecal_core.ok():
          time.sleep(0.1)

        ecal_core.finalize()

        while not rospy.is_shutdown():
            if rospy.Time.now() - self.last_flush_time > rospy.Duration(self.flush_interval):
                self.write_to_file()
                self.last_flush_time = rospy.Time.now()
            rate.sleep()



# Callback for receiving messages
def callback(topic_name, pose_proto_msg, time):
  # print(topic_name)
  # print("timestamp {} \nposition {}orientation {}".format(pose_proto_msg.timestamp
  #                                     , pose_proto_msg.position
  #                                     , pose_proto_msg.orientation))
  # 10Hz record pose
  write_to_csv(pose_proto_msg.position)
  # pass
  
def get_new_filename():
    now = datetime.now()
    return now.strftime('%Y%m%d_%H%M%S') + '.csv'

def write_to_csv(data, file_size_limit=100 * 1024 * 1024):
    file_count = 0
    filename = get_new_filename()
    filepath = os.path.join(os.getcwd(), filename)
    
    while True:
        if os.path.exists(filepath) and os.path.getsize(filepath) >= file_size_limit:
            file_count += 1
            filename = get_new_filename()
            filepath = os.path.join(os.getcwd(), filename)
        
        with open(filepath, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)

if __name__ == "__main__":
  # initialize eCAL API. The name of our Process will be
  # "Python Protobuf Subscriber"
  ecal_core.initialize(sys.argv, "Python Protobuf Subscriber")

  # Create a Protobuf Publisher that publishes on the topic
  # "hello_world_python_protobuf_topic". The second parameter tells eCAL which
  # datatype we are expecting to receive on that topic.
  sub = ProtoSubscriber("svc/pose"
                      , pose_pb2.Pose)

  # Set the Callback
  sub.set_callback(callback)

  
  # Just don't exit
  while ecal_core.ok():
    print('OK')
    write_to_csv(pose_proto_msg.position)
    time.sleep(0.1)
  
  # finalize eCAL API
  ecal_core.finalize()