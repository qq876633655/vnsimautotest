import psutil
import os
import signal
def kill_process():
    pro = psutil.process_iter(['pid', 'name', 'cmdline'])
    for i in pro:
        if i.info['name'] == 'python3':
            if i.info['cmdline'][-1].split("/")[-1] == "process_csv_linux.py":
                os.kill(i.info['pid'], signal.SIGTERM)

if __name__ == '__main__':
    kill_process()

