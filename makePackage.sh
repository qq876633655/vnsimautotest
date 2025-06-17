#/bin/bash

# 要在宿主机上运行打包脚本
cd ../

# 函数用于打包文件夹，但排除 obj 文件夹
function package_gz_folder() {
  local folder_name=$1
  local package_name="${MyAppVersion}_${MyAppDate}_${folder_name}_release.tar.gz"
  
  if [ -d $folder_name ]; then
    # 检查并删除 ../ 目录下的 *.tar.gz 文件
    #echo "检查并删除 $SCRIPT_DIR 目录下的 *.tar.gz 文件"
    #find "$SCRIPT_DIR" -maxdepth 1 -name "*.tar.gz" -type f -exec rm -f {} \;
    rm -rf *_*_${folder_name}_release.tar.gz
    rm -rf "$folder_name"/*_*.txt
    echo "创建版本文件: $folder_name/${MyAppVersion}_${MyAppDate}.txt"
    touch "$folder_name/${MyAppVersion}_${MyAppDate}.txt"
    # 检查 MyContent 是否不为空
    if [ -n "$MyContent" ]; then
      echo "$MyContent" > "$folder_name/${MyAppVersion}_${MyAppDate}.txt"
    fi
    echo "开始打包 $folder_name"
    tar --exclude='.git*' --exclude='makePackage.sh' -cvzf "$package_name" "$folder_name"
    echo "打包完成: $package_name"
  else
    echo "未找到 $folder_name 文件夹"
  fi
}

function package_zip_folder() {
  local folder_name=$1
  local package_name="${MyAppVersion}_${MyAppDate}_${folder_name}_release.zip"
  
  if [ -d $folder_name ]; then
    rm -rf *_*_${folder_name}_release.zip
    echo "开始打包 $folder_name"
    zip -rP vn_simulation $package_name $folder_name -x "*/.git/*"
    echo "打包完成: $package_name"
  else
    echo "未找到 $folder_name 文件夹"
  fi
}

function help(){
    echo "[help] makePackage.sh MyAppVersion MyAppDate ex. makePackage.sh 5.2.0.0 241009"
    exit 1
}

if [ $# < 2 ]; then
    help
fi

MyAppVersion=$1
MyAppDate=$2
MyContent=$3

# 获取该文件的绝对路径
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
echo "脚本所在目录: $SCRIPT_DIR"

# 打包 sim_module_pkg, vn_wbt_assets, vn_wbt_project, add more here
package_gz_folder "sim_module_pkg"
package_zip_folder "vn_wbt_assets"
#package_gz_folder "vn_wbt_project"

