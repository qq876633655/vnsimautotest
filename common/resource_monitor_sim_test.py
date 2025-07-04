import os
import psutil
import csv
import time
import datetime
import multiprocessing

class ResourceMonitor:
    def __init__(self, interval=5):
        self.interval = interval
        self.process_names = [
            "AGVPro",
            "VN.ConfigCenter.dll",
            "VN.Robotune.dll",
            "3dslam",
            "3DSlamPrinter",
            "AGVPerceptionServer",
            "general.dll"
        ]
        self.process = None
        self.stop_event = multiprocessing.Event()

    def start(self):
        self.process = multiprocessing.Process(target=self._monitor_loop)
        self.process.start()

    def stop(self):
        self.stop_event.set()
        if self.process:
            self.process.join()

    def _monitor_loop(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        log_dir = os.path.join("../logs", timestamp)
        os.makedirs(log_dir, exist_ok=True)

        system_csv = open(os.path.join(log_dir, "system.csv"), mode='w', newline='')
        system_writer = csv.writer(system_csv)
        system_writer.writerow(["time", "cpu_percent", "memory_percent", "disk_percent", "net_sent_kb", "net_recv_kb"])

        process_files = {}
        for pname in self.process_names:
            f = open(os.path.join(log_dir, f"{pname}_stats.csv"), mode='w', newline='')
            w = csv.writer(f)
            w.writerow(["time", "pid", "cpu_percent", "memory_mb", "read_mb", "write_mb", "threads", "connections"])
            process_files[pname] = (f, w)

        # net_last = psutil.net_io_counters()

        try:
            while not self.stop_event.is_set():
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # --- 系统资源 ---
                cpu = psutil.cpu_percent(interval=1)
                mem = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent
                net_now = psutil.net_io_counters()
                # net_sent = (net_now.bytes_sent - net_last.bytes_sent) / 1024
                # net_recv = (net_now.bytes_recv - net_last.bytes_recv) / 1024
                # net_last = net_now
                # print(cpu, mem, disk, net_now.bytes_sent, net_now.bytes_recv)
                system_writer.writerow([now, cpu, mem, disk, round(net_now.bytes_sent, 2), round(net_now.bytes_recv, 2)])
                system_csv.flush()

                # --- 进程资源（支持进程启停） ---
                found_processes = {pname: False for pname in self.process_names}

                for proc in psutil.process_iter(['pid', 'name']):
                    pname = proc.info['name']
                    if pname not in self.process_names:
                        continue
                    try:
                        with proc.oneshot():
                            cpu = proc.cpu_percent(interval=1)
                            mem = proc.memory_info().rss / 1024 / 1024
                            io = proc.io_counters()
                            read_mb = io.read_bytes / 1024 / 1024
                            write_mb = io.write_bytes / 1024 / 1024
                            threads = proc.num_threads()
                            conns = len(proc.net_connections(kind='all'))
                            process_files[pname][1].writerow([
                                now, proc.pid, cpu, round(mem, 2), round(read_mb, 2), round(write_mb, 2), threads, conns
                            ])
                            process_files[pname][0].flush()
                            found_processes[pname] = True
                    except Exception:
                        continue

                # --- 写入未找到的进程时间戳 ---
                for pname, found in found_processes.items():
                    if not found:
                        process_files[pname][1].writerow([now])
                        process_files[pname][0].flush()

                time.sleep(self.interval)

        finally:
            system_csv.close()
            for f, _ in process_files.values():
                f.close()


if __name__ == '__main__':
    rm = ResourceMonitor()
    rm.start()
    time.sleep(60)
    rm.stop()