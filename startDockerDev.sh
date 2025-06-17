#!/bin/bash
HOST_ROOT_DIR=/home/visionnav/VNSim
DOCK_ROOT_DIR=/home/visionnav

HOST_PROCESS_DIR=$HOST_ROOT_DIR/sim_module_pkg
DOCK_PROCESS_DIR=/usr/local/webots/projects/default

HOST_WORKSPACE_DIR=$HOST_ROOT_DIR/workspace
HOST_AGV_SERIVCE_CONFIG_DIR=/home/visionnav/AGVServices/general/config

HOST_ECAL_CONFIG_DIR=/usr/local/etc/ecal
DOCK_ECAL_CONFIG_DIR=/usr/local/etc/ecal

# 检查容器外要映射的目录是否存在，不存在就创建
if [ ! -d $HOST_ROOT_DIR/logs ]; then
	mkdir -p $HOST_ROOT_DIR/logs
fi 
if [ ! -d $HOST_PROCESS_DIR ]; then
	mkdir -p $HOST_PROCESS_DIR
fi 
if [ ! -d $HOST_PROCESS_DIR/controllers ]; then
	mkdir -p $HOST_PROCESS_DIR/controllers
fi 
if [ ! -d $HOST_PROCESS_DIR/libraries ]; then
	mkdir -p $HOST_PROCESS_DIR/libraries
fi 
if [ ! -d $HOST_PROCESS_DIR/configs ]; then
	mkdir -p $HOST_PROCESS_DIR/configs
fi 
if [ ! -d $HOST_PROCESS_DIR/robots ]; then
	mkdir -p $HOST_PROCESS_DIR/robots
fi 
# 检查容器外要映射的目录是否存在，不存在就报错推出
if [ ! -d $HOST_AGV_SERIVCE_CONFIG_DIR ]; then
	echo "ERROR: $HOST_AGV_SERIVCE_CONFIG_DIR not exist"
	exit 1
fi
if [ ! -d $HOST_PROCESS_DIR/libraries ]; then
	echo "ERROR: $HOST_PROCESS_DIR/libraries not exist"
	exit 1
fi
if [ ! -d $HOST_PROCESS_DIR/controllers ]; then
	echo "ERROR: $HOST_PROCESS_DIR/controllers not exist"
	exit 1
fi
if [ ! -d $HOST_PROCESS_DIR/configs ]; then
	echo "ERROR: $HOST_PROCESS_DIR/configs not exist"
	exit 1
fi

docker run -it --rm --privileged --gpus all \
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
	 --ipc=host\
	 --pid=host \
	 --network=host \
	 simulation:latest /bin/bash
