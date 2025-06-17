import os
import subprocess

docker_path = "/home/visionnav/VNSim/vnsimautotest/startDockerDev2.sh"


process = subprocess.Popen(["bash", docker_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,text=True)

print(process.stdout)
print(process.stderr)