# from signalrcore.hub_connection_builder import HubConnectionBuilder
# import time
# import logging
#
# hub_url = 'ws://127.0.0.1:24311/signalr'
#
# hub_connection = HubConnectionBuilder()\
#     .with_url(hub_url)\
#     .configure_logging(logging.DEBUG)\
#     .build()
#
# def on_receive(data):
#     print(data)
#
# hub_connection.on('receive', on_receive)
#
# hub_connection.start()
# print('connect success')
# hub_connection.send('11', ['11', '22'])
# import requests
import time

# try:
#     while True:
#         time.sleep(1)
# except KeyboardInterrupt:
#     print("Closing hub connection")
#     hub_connection.stop()

# import subprocess
#
# SUDO_PWD = '123'
# cmd = "sudo -S /home/visionnav/AGVServices/AGVPro/startupRobotune.sh"
# result = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
#                           text=True)
# result.stdin.write("123\n")
# result.stdin.flush()
# print(result.stdout)
import sys
import site
import os
import ecal.core.core as ecal_core
from Cython import returns


def find_null_byte_files():
    site_packages_paths = site.getsitepackages()
    bad_files = []

    print("正在扫描以下 site-packages 路径：")
    for path in site_packages_paths:
        print(" -", path)

        for root, dirs, files in os.walk(path):
            for filename in files:
                if filename.endswith(".py"):
                    print(filename)
                    file_path = os.path.join(root, filename)
                    try:
                        with open(file_path, "rb") as f:
                            content = f.read()
                            if b"\x00" in content:
                                bad_files.append(file_path)
                    except Exception as e:
                        print("无法读取文件:", file_path, "| 错误:", e)

    if bad_files:
        print("\n以下 Python 文件中包含空字节，可能已损坏：")
        for f in bad_files:
            print(" -", f)
    else:
        print("\n未发现包含空字节的 Python 文件。")


if __name__ == "__main__":
    # find_null_byte_files()
    import time
    if time.time() -( float("1751346646487") / 1000) > 3:
        pass