from PySide6.QtWidgets import QApplication,QMessageBox
from PySide6.QtUiTools import QUiLoader #UI加载工具
import sys
from GameAuto1 import *

class GameAutoGUI:
    def __init__(self):
        # 实例自动化类
        self.gameAuto = Automation()
        if self.gameAuto.initSelf():
            # 初始化成功，开始自动化
            self.gameAuto.auto_play()


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


if __name__ == '__main__':
    ui_loader = QUiLoader()  # PySide6的bug，需要在QApplication前先实例这个类
    app = QApplication(sys.argv)  # 创建应用
    GameAutoGUI_Tool = GameAutoGUI()
    GameAutoGUI_Tool.ui.show()
    sys.exit(app.exec())  # 开始执行程序，并且进入消息循环等待