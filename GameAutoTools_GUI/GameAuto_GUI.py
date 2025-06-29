# from contextlib import nullcontext
#
# from PySide6.QtWidgets import QApplication,QMessageBox
# from PySide6.QtUiTools import QUiLoader #UI加载工具
# import sys
# from GameAuto1 import *
#
# class GameAutoGUI:
#     def __init__(self):
#
#         # 参数信息初始化
#         self.gameMode = GAME_MODE_PVE_XMGD  #默认游戏模式
#         self.pcName = PC_Desktop            #默认为台式机电脑
#
#         self.gameAuto = None    #在未获取基本的设置参数之前，不能实例化
#
#         self.ui = ui_loader.load("UI/mainWindow.ui")
#         #self.ui.resize(640, 440)
#         self.ui.btn_start.clicked.connect(self.startScript) #开始自动操作
#         self.ui.btn_end.clicked.connect(self.endScript)     #立即结束脚本
#
#         # 初始化游戏模式
#         self.ui.cBox_gameMode.addItem(GAME_MODE_PVP_WJSL)
#         self.ui.cBox_gameMode.addItem(GAME_MODE_PVE_XMGD)
#         self.ui.cBox_gameMode.addItem(GAME_MODE_PVE_HMZN)
#         self.ui.cBox_gameMode.addItem(GAME_MODE_PVE_WXJL)
#         self.ui.cBox_gameMode.addItem(GAME_MODE_PVE_HSBL)
#         # 初始化平台名称
#         self.ui.cBox_pcName.addItem(PC_ThinkBook16P)
#         self.ui.cBox_pcName.addItem(PC_MyServer)
#         self.ui.cBox_pcName.addItem(PC_WuJie14X)
#         self.ui.cBox_pcName.addItem(PC_Desktop)
#
#     # 获取上位机的参数设置信息
#     def getSettings(self):
#         self.gameMode = self.ui.cBox_gameMode.currentText()
#         self.pcName = self.ui.cBox_pcName.currentText()
#
#     #启动核心函数
#     def startScript(self):
#         self.ui.btn_start.setEnabled(False)   #同时运行的脚本个数只能为1
#         self.getSettings()
#         # 实例自动化类
#         self.gameAuto = Automation(self.pcName, self.gameMode)
#
#         if self.gameAuto.initSelf():
#             # 初始化成功，开始自动化
#             self.gameAuto.auto_play()
#
#     # 上位机显示信息更新
#     def updateInfo(self):
#         self.ui.tEdit.append(self.gameAuto.logInfo)
#
#     def endScript(self):
#         # 结束脚本
#         # del self.gameAuto
#         self.gameAuto = None
#         self.ui.btn_start.setEnabled(True)
#
#
# if __name__ == '__main__':
#     ui_loader = QUiLoader()  # PySide6的bug，需要在QApplication前先实例这个类
#     app = QApplication(sys.argv)  # 创建应用
#     GameAutoGUI_Tool = GameAutoGUI()
#     GameAutoGUI_Tool.ui.show()
#     sys.exit(app.exec())  # 开始执行程序，并且进入消息循环等待