from datetime import datetime
from threading import Thread
import psutil
import logging
from logging.handlers import RotatingFileHandler
import os
import time
import csv
import subprocess


class ProcessRecode:

    def __init__(self):
        log_dir = "./logs/"
        os.makedirs(log_dir, exist_ok=True)

        self.logger = logging.getLogger('ProcessRecode')
        self.logger.setLevel(logging.INFO)

        max_size = 10 * 1024 * 1024  # 设置日志文件的最大大小为10MB
        backup_count = 20  # 设置日志文件的最大备份数量为20
        log_file_path = os.path.join(log_dir, 'processRecode.log')
        handler = RotatingFileHandler(
            log_file_path, maxBytes=max_size, backupCount=backup_count
        )
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.init_csv()

    def get_process_pids(self):
        process_list = ["AGVPro", "VN.ConfigCenter.dll", "VN.Robotune.dll", 
                        "3dslam", "3DSlamPrinter", "AGVPerceptionServer", 
                        "general.dll"]
        
        process_dict = {}
        for process_name in process_list:
            try:
                cmd = f"ps -aux |grep -w {process_name} |grep -v grep |awk '{{print $2}}' | tail -n 1"
                # print(cmd)
                pid = subprocess.check_output(cmd, shell=True, text=True)
                # print(pid)
                process_dict[process_name] = pid
            except subprocess.CalledProcessError as e:
                print(f"Error: {e}")
        # print(process_dict)
        return process_dict
    
    def init_csv(self):
        csv_dir = "./csv"
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)

        self.system_csv = f"./{csv_dir}/system_stats.csv"
        if os.path.exists(self.system_csv):
            os.remove(self.system_csv)
    
        with open(self.system_csv, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp','Name', 'CPU Usage (%)', 'Memory Usage (%)', 'Disk Usage (%)', 'Net Read (Bytes)', 'Net Send (Bytes)'])

        process_list = self.get_process_pids().keys()
        self.csv_files = {process_name: f"./{csv_dir}/{process_name}_stats.csv" for process_name in process_list}
        for process_name, file_name in self.csv_files.items():
            if os.path.exists(file_name):
                os.remove(file_name)
            with open(file_name, mode='w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Timestamp', 'PID','Name', 'CPU Usage (%)', 'Memory Usage (MB)', 'Disk Read (Bytes)', 'Disk Write (Bytes)'])

    def get_socket_count(self, proc):
        try:
            # 获取进程的所有网络连接
            connections = proc.connections(kind='all')
            return len(connections)
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            self.logger.warning(f"Cannot access sockets for PID {proc.pid}: {e}")
            return 0   

    def get_temperature_info(self):
        try:
            if not hasattr(psutil, "sensors_temperatures"):
                self.logger.error("Error: platform not supported")
                return
            
            temps = psutil.sensors_temperatures()
            if not temps:
                self.logger.error("Error: can't read any temperature")
                return

            for name, entries in temps.items():
                for entry in entries:
                    label = entry.label or name
                    self.logger.info(f"{name}: {label:20} {entry.current} °C")

        except Exception as e:
            self.logger.error(f"An error occurred while getting temperature info: {e}")       

    def thread_function_proc(self, proc, process_name, pid):
        try:
            #proc_info = proc.info
            cpu_usage = proc.cpu_percent(interval=1)
            memory_percent = proc.memory_percent()
            memory_info = proc.memory_info()
            memory_usage = memory_info.rss / 1024 / 1024
            io_counters = proc.io_counters()
            # 线程数量
            thread_count = proc.num_threads()
            # 获取套接字数量
            socket_count = self.get_socket_count(proc)
            pid = proc.pid

            log_message = (f"PID: {pid}, Name: {process_name}, "
                        f"CPU: {cpu_usage}%, Memory: {memory_percent:.2f}%, "
                        f"Disk Read Bytes: {io_counters.read_bytes / 1024:.2f}KB, "
                        f"Disk Write Bytes: {io_counters.write_bytes / 1024:.2f}KB, "
                        f"Thread Count: {thread_count}, "
                        f"Socket Count: {socket_count}")
            
            self.logger.info(log_message)
            timestamp = f"'{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
            with open(self.csv_files[process_name], mode='a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([timestamp, pid, process_name, cpu_usage, memory_usage, io_counters.read_bytes, io_counters.write_bytes])
                csvfile.flush()

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            self.logger.warning(f"Error processing process {proc.pid}: {e}")

    def thread_function_system(self):
        try:
            # 系统资源使用情况
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_usage = psutil.disk_usage('/')
            net_io_counters = psutil.net_io_counters()
            
            self.logger.info(f'System CPU Usage: {cpu_usage}%, Memory Usage: {memory.percent}%, Disk Usage: {disk_usage.percent}%, '
                        f'Network Sent: {net_io_counters.bytes_sent / 1024:.2f}KB, '
                        f'Network Received: {net_io_counters.bytes_recv / 1024:.2f}KB')
            
            timestamp = f"'{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
            with open(self.system_csv, mode='a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                print(cpu_usage, memory.percent, disk_usage.percent, net_io_counters.bytes_recv,
                                net_io_counters.bytes_sent)
                writer.writerow([timestamp, "system", cpu_usage, memory.percent, disk_usage.percent, net_io_counters.bytes_recv,
                                net_io_counters.bytes_sent])
                csvfile.flush()

            self.get_temperature_info()
        except Exception as e:
            self.logger.error(f"Error during system monitoring: {e}")                

    def log_process_info(self):
        threads = []

        system_thread = Thread(target=self.thread_function_system)
        system_thread.start()
        threads.append(system_thread)

        for process_name, process_pid in self.get_process_pids().items():
            if process_pid:
                try:
                    proc = psutil.Process(int(process_pid))
                    thread = Thread(target=self.thread_function_proc, args=(proc, process_name, process_pid))
                    thread.start()
                    threads.append(thread)
                except psutil.NoSuchProcess:
                    print(f"Process with PID {process_pid} does not exist.")
                except psutil.AccessDenied:
                    print(f"Access to process {process_pid} is denied.")
                except psutil.ZombieProcess:
                    print(f"Process with PID {process_pid} is a zombie process.")

        # for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'cmdline']):
        #     try:
        #         cmdline_str = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
        #         if cmdline_str or "sh -c" in cmdline_str:
        #             continue

        #         print("cmdline_str: ", cmdline_str)
        #         for process_name in self.get_process_list():
        #             if "AGVPro" in cmdline_str and "pmDaemonPId" in cmdline_str:
        #                 thread = Thread(target=self.thread_function_proc, args=(proc, process_name))
        #                 thread.start()
        #                 threads.append(thread)  
        #                 break                      
        #     except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        #         self.logger.warning(f"Cannot access process info for PID {proc.pid}: {e}")

        # print(f"len thread: {len(threads)}")
        for thread in threads:
            thread.join(1.1)

    def start_recode(self):
        while True:
            self.log_process_info()
            self.logger.info("-------------------")
            time.sleep(2)


if __name__ == '__main__':
    process_recode = ProcessRecode()
    process_recode.start_recode()
