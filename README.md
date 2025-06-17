### 仿真助手

##### 开发：
使用VScode的Black Formatter的插件来进行python程序的格式化


##### 打包：
###### 步骤 1: 安装PyInstaller
如果你还没有安装PyInstaller，可以通过以下命令安装：
```bash
sudo apt update
sudo apt install python3-pip
sudo pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
```

###### 步骤 2: 使用PyInstaller打包
在你的项目目录中，运行以下命令来打包你的Python脚本：
```bash
pyinstaller --onefile VN_WebotsLauncherX.py
```
###### 步骤 3: 运行打包后的应用程序

在`dist`文件夹中，找到生成的可执行文件，通常文件名与你的脚本名相同，但扩展名为`.exe`（在Linux系统中，它可能只是脚本名）。你可以通过以下命令运行它：
```bash
./VN_WebotsLauncherX
```
