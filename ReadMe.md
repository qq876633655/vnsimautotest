## 如何安装python ecal5.12.0的whl
1. 下载whl文件，如：ecal5-5.12.0-1focal-cp38-cp38-linux_x86_64.whl
2. 安装：python3.8 -m pip install ecal5-5.12.0-1focal-cp38-cp38-linux_x86_64.whl

## 如何安装protobuf
注意：ecal5 5.12.0 has requirement protobuf<=3.20,>=3.6.1
1. python3.8 -m pip install protobuf==3.6.1

## 如何生成protobuf的产物

ecal 官网教程
https://eclipse-ecal.github.io/ecal/getting_started/hello_world_python_proto.html


# 使用流程

1. 手动配置好AGV程序以及启动好对应的webots场景
    - 后续要写程序替换模块，一个zip包绑定一个webots场景
2. 重定位测试（robotune接口）
3. 进行动态任务流程的逐条测试（失败了就要重启webots）


# 运行层级设计

1. 指定运行哪些用例，然后逐条运行用例 —— 搁置
    - 单个用例运行需要读取动态任务流程 —— 简化（动态任务列表所有任务当作一个用例）
        - 动态任务流程执行并启动监控脚本
        - 返回结果
        