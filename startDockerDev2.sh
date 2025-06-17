#!/bin/bash

# === 基础路径定义 ===
HOST_ROOT_DIR=/home/visionnav/VNSim
DOCK_ROOT_DIR=/home/visionnav

HOST_PROCESS_DIR=$HOST_ROOT_DIR/sim_module_pkg
DOCK_PROCESS_DIR=/usr/local/webots/projects/default

HOST_WORKSPACE_DIR=$HOST_ROOT_DIR/workspace
HOST_AGV_SERIVCE_CONFIG_DIR=/home/visionnav/AGVServices/general/config

HOST_ECAL_CONFIG_DIR=/usr/local/etc/ecal
DOCK_ECAL_CONFIG_DIR=/usr/local/etc/ecal

# === 创建必要目录 ===
mkdir -p $HOST_ROOT_DIR/logs
mkdir -p $HOST_PROCESS_DIR/controllers
mkdir -p $HOST_PROCESS_DIR/libraries
mkdir -p $HOST_PROCESS_DIR/configs
mkdir -p $HOST_PROCESS_DIR/robots

# === 检查必要路径 ===
if [ ! -d $HOST_AGV_SERIVCE_CONFIG_DIR ]; then
	echo "ERROR: $HOST_AGV_SERIVCE_CONFIG_DIR not exist"
	exit 1
fi

# === 启动容器（前台保持运行）===
docker run -d --rm --privileged --gpus all \
	-e NVIDIA_DRIVER_CAPABILITIES=all \
	-e NVIDIA_VISIBLE_DEVICES=all \
	-e "DISPLAY=$DISPLAY" \
	-v /etc/localtime:/etc/localtime \
	-v $HOST_ROOT_DIR/logs:$DOCK_ROOT_DIR/logs \
	-v $HOST_PROCESS_DIR:$DOCK_ROOT_DIR/sim_module_pkg \
	-v $HOST_PROCESS_DIR/controllers:$DOCK_PROCESS_DIR/controllers \
	-v $HOST_PROCESS_DIR/libraries:$DOCK_PROCESS_DIR/libraries \
	-v $HOST_PROCESS_DIR/configs:$DOCK_PROCESS_DIR/configs \
	-v $HOST_ROOT_DIR/vn_wbt_assets:$DOCK_ROOT_DIR/.vn_simulation/vn_wbt_assets \
	-v $HOST_ROOT_DIR/vn_wbt_project:$DOCK_ROOT_DIR/vn_wbt_project \
	-v $HOST_AGV_SERIVCE_CONFIG_DIR:$DOCK_ROOT_DIR/AGVServices/general/config \
	-v $HOST_ROOT_DIR/vnsimautotest:$DOCK_ROOT_DIR/vnsimautotest \
	-v $HOST_WORKSPACE_DIR:$DOCK_ROOT_DIR/workspace \
	-v /tmp/.X11-unix:/tmp/.X11-unix \
	-v $HOST_ECAL_CONFIG_DIR:$DOCK_ECAL_CONFIG_DIR \
	--ipc=host \
	--pid=host \
	--network=host \
	--name vnsim_dev \
	simulation:latest tail -f /dev/null