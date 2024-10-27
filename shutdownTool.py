from PySide6.QtWidgets import QApplication,QMessageBox
from PySide6.QtUiTools import QUiLoader #UI加载工具
# from PySide6.QtCore import QTime,QFile  #实现倒计时
import time
import sys
from os import system   #关机、重启、休眠

# PySide6-uic mainWindow.ui -o mainWindow.py

class ShutdownTool:
    def __init__(self):
        # qfile_shutdown = QFile("UI/mainWindow.ui")
        # qfile_shutdown.open(QFile.ReadOnly)
        # qfile_shutdown.close()
        # self.ui = ui_loader.load(qfile_shutdown)

        self.countdown = 0  #倒计时，分钟
        self.countdown_switch = False    #倒计时开关
        self.debug = True               #调试开关，打开后，不会真正地执行关机/重启/休眠

        self.ui = ui_loader.load("UI/mainWindow.ui")
        self.ui.resize(640, 440)
        self.ui.pBTN_ShutdownNow.clicked.connect(self.shutdown_now)#立即关机
        self.ui.pBTN_ShutdownLater.clicked.connect(self.shutdown_later)#倒计时关机
        self.ui.pBTN_SleepNow.clicked.connect(self.sleep_now)#立即休眠
        self.ui.pBTN_SleepLater.clicked.connect(self.sleep_later)#倒计时休眠
        self.ui.pBTN_RestartNow.clicked.connect(self.restart_now)#立即重启
        self.ui.pBTN_ReStartLater.clicked.connect(self.restart_later)#倒计时重启
        self.ui.pBTN_Reset.clicked.connect(self.reset_countdown)#重置倒计时
        self.ui.DebugSwtich.stateChanged.connect(self.debug_on_off)#打开/关闭调试

    def shutdown_now(self):
        #立即关机
        if not self.debug:
            system("shutdown /s /t 0")
        else:
            print("立即关机")

    def shutdown_later(self):
        #倒计时关机
        self.ui.pBTN_ShutdownLater.setEnabled(False)
        self.ui.pBTN_SleepLater.setEnabled(False)
        self.ui.pBTN_ReStartLater.setEnabled(False)
        self.count_down()  # 倒计时
        if self.countdown_switch:
            print(f"倒计时关机：{self.countdown}分钟")
            if not self.debug:
                system("shutdown /s /t 0")
            else:
                print("倒计时关机")

    def sleep_now(self):
        #立即休眠
        if not self.debug:
            system("shutdown /h")
        else:
            print("立即休眠")

    def sleep_later(self):
        #倒计时休眠
        self.ui.pBTN_ShutdownLater.setEnabled(False)
        self.ui.pBTN_SleepLater.setEnabled(False)
        self.ui.pBTN_ReStartLater.setEnabled(False)
        self.count_down()  # 倒计时
        if self.countdown_switch:
            print(f"倒计时休眠：{self.countdown}分钟")
            if not self.debug:
                system("shutdown /h")
            else:
                print("倒计时休眠")

    def restart_now(self):
        #立即重启
        if not self.debug:
            system("shutdown /r /t 0")
        else:
            print("立即重启")

    def restart_later(self):
        #倒计时重启
        self.ui.pBTN_ShutdownLater.setEnabled(False)
        self.ui.pBTN_SleepLater.setEnabled(False)
        self.ui.pBTN_ReStartLater.setEnabled(False)
        self.count_down()  # 倒计时
        if self.countdown_switch:
            print(f"倒计时重启：{self.countdown}分钟")
            if not self.debug:
                system("shutdown /r /t 0")
            else:
                print("倒计时重启")

    def reset_countdown(self):
        #重置倒计时
        self.countdown = 0              #倒计时清零
        self.countdown_switch = False   #关闭倒计时开关
        self.ui.pBTN_ShutdownLater.setEnabled(True)
        self.ui.pBTN_SleepLater.setEnabled(True)
        self.ui.pBTN_ReStartLater.setEnabled(True)
        print("重置倒计时")

    def get_countdown(self):
        #获取倒计时
        countdown_cbox = self.ui.cBOX_CountDown.currentText()   #下拉框的倒计时
        countdown_text = self.ui.spinBox_CountDown.value()      #数字框的倒计时，本来就是int类型
        #转为数字
        if countdown_cbox.isdigit():
            countdown_cbox = int(countdown_cbox)
        else:
            self.show_warning_message("未选择倒计时！已默认倒计时为5分钟。") #弹窗提示
            countdown_cbox = 5  #默认是倒计时1分钟

        #优先使用文本框的倒计时
        if countdown_text != 0:
            self.countdown = countdown_text
        else:
            self.countdown = countdown_cbox
        #打开倒计时开关
        self.countdown_switch = True

    def count_down(self):
        #倒计时
        start_time = time.time()  # 获取当前时间（以秒为单位）
        self.get_countdown()  # 获取倒计时的值
        while True:
            elapsed_time = time.time() - start_time  # 计算经过的时间
            QApplication.processEvents()  # 【关键】处理事件，保持界面响应
            if elapsed_time >= self.countdown * 60:
                break  # 如果经过时间大于或等于分钟数*60，则退出循环

    def debug_on_off(self):
        #打开和关闭调试
        if self.ui.DebugSwtich.isChecked():
            self.debug = True
            self.ui.DebugSwtich.setText("调试已打开")
        else:
            self.debug = False
            self.ui.DebugSwtich.setText("调试已关闭")

    @staticmethod
    def show_warning_message(msg):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("提示")
        msg_box.setText(msg)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

if __name__ == '__main__':
    ui_loader = QUiLoader()  # PySide6的bug，需要在QApplication前先实例这个类
    app = QApplication(sys.argv)  # 创建应用
    shutdown_tool = ShutdownTool()
    shutdown_tool.ui.show()
    sys.exit(app.exec())  # 开始执行程序，并且进入消息循环等待

