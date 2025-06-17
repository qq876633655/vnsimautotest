#!/bin/bash

# 获取该文件的绝对路径
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
echo "脚本所在目录: $SCRIPT_DIR"

HOST_ROOT_DIR="/home/visionnav"
HOST_PROCESS_DIR="$HOST_ROOT_DIR/sim_module_pkg"

# 确保目标目录存在
mkdir -p "$HOST_PROCESS_DIR"
MAKE_PACKAGE_ROOT_DIR=${HOST_ROOT_DIR}/sim_module_pkg/

# 复制 startDocker.sh 脚本到目标目录
cp -r "$SCRIPT_DIR/startDocker.sh" "$HOST_PROCESS_DIR"

# 删除本地编译导致的 build 文件夹残留
rm -rf build
# 使用 PyInstaller 打包 Python 脚本
pyinstaller --onefile \
            --name simulate_assistant \
            --distpath "$HOST_PROCESS_DIR" \
            --add-binary "$SCRIPT_DIR/scripts/VN_WebotsLauncherX.py:." \
            "$SCRIPT_DIR/scripts/VN_WebotsLauncherX.py"

# # 使用 PyInstaller 打包 Python 脚本, VNSimAutoTest
# pyinstaller --onefile \
#             --name simulate_assistant_flask \
#             --distpath "$HOST_PROCESS_DIR" \
#             --add-binary "$SCRIPT_DIR/scripts/VNSim_http_flaskClass.py:." \
#             "$SCRIPT_DIR/scripts/VNSim_http_flaskClass.py"            

cp ${SCRIPT_DIR}/makePackage.sh ${MAKE_PACKAGE_ROOT_DIR}

