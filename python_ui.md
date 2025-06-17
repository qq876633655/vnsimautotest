在 Ubuntu 20.04 下使用 Python 3 来创建 Qt UI，你可以使用 `PyQt5` 或 `PySide2` 这两个库，它们提供了 Python 绑定，允许你使用 Qt 的功能来创建图形用户界面（GUI）。以下是使用 `PyQt5` 的基本步骤：

1. **安装 PyQt5**:
   首先，你需要安装 `PyQt5`。你可以使用 pip 来安装它：
   ```bash
   pip3 install pyqt5
   pip3 install PyQt5-tools
   ```

2. **设计 UI**:
   使用 Qt Designer 来设计你的 UI。Qt Designer 是 Qt 提供的一个可视化工具，允许你拖放组件来设计 UI。它通常与 Qt SDK 一起提供，但你也可以在 Ubuntu 上单独安装它：
   ```bash
   sudo apt-get install qt5-default qttools5-dev-tools
   ```

3. **转换 UI 文件**:
   使用 Qt Designer 设计完 UI 后，你需要将 `.ui` 文件转换为 Python 代码。这可以通过 `pyuic5` 命令行工具完成：
   ```bash
   pyuic5 -x your_design.ui -o your_design.py
   ```
   这将生成一个 Python 文件，包含了 UI 的代码。

4. **编写 Python 脚本**:
   创建一个 Python 脚本，导入 `your_design.py` 中的 UI 类，并使用它来创建窗口：
   ```python
   import sys
   from PyQt5.QtWidgets import QApplication, QMainWindow
   from your_design import Ui_MainWindow  # 导入转换后的 UI 类

   class MainWindow(QMainWindow, Ui_MainWindow):
       def __init__(self):
           super().__init__()
           self.setupUi(self)  # 设置 UI

   if __name__ == "__main__":
       app = QApplication(sys.argv)
       window = MainWindow()
       window.show()
       sys.exit(app.exec_())
   ```

5. **运行你的程序**:
   保存你的 Python 脚本并运行它：
   ```bash
   python3 your_script.py
   ```

这将启动你的应用程序，显示你使用 Qt Designer 设计的 UI。

