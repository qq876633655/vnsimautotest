import subprocess

password = "123"
shutdown_path = "/home/visionnav/AGVServices/AGVPro/shutdown.sh"
result = subprocess.run(["sudo","-S", shutdown_path],input=password + "\n", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print(result.stdout)
