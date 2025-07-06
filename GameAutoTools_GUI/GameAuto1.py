import logging
from PySide6.QtWidgets import QApplication, QMessageBox, QTextBrowser
from PySide6.QtUiTools import QUiLoader #UI加载工具
import sys
import re  # 正则表达式
from datetime import datetime, timedelta  # 获取时间
from threading import Thread    # 线程相关，防止GUI界面在运行主函数时卡死
# from PySide6.QtCore import (QThread, Signal)   # 线程相关，防止GUI界面在运行主函数时卡死
import traceback    # 异常处理
from PySide6.QtCore import Signal,QObject   # 子线程想要使用主线程的变量，必须用信号传递，不然程序必然崩溃。

# from Demos.security.lsastore import retrieveddata

from Settings_Server import *
from FaultMonitor import *
from OPFuncs import *



# 自定义信号源对象类型，一定要继承自 QObject
class   MySignal(QObject):
    # 定义一种信号，两个参数 类型分别是： QTextBrowser 和 字符串
    # 调用 emit方法 发信号时，传入参数 必须是这里指定的 参数类型
    text_print = Signal(QTextBrowser, LogLevel, str)

    # 还可以定义其他种类的信号
    cyc_update = Signal(QTextBrowser, str)

# 全局变量
# 信号
G_Sig = MySignal()
# # 控制GUI相关代码的初始化次数
# G_GuiInit = False

# class WorkerThread(QThread):
#     # 定义信号
#     sig_updated = Signal(int)  # 进度更新
#     sig_finished = Signal(str)  # 任务完成
#     #sig_err_occurred = Signal(str)  # 错误发生
#
#     def __init__(self):
#         super().__init__()
#         self.is_running = True
#
#     def run(self):
#         count = 0
#         while self.is_running:
#             count += 1
#             auto = Automation(PC_NAME, GAME_MODE_CUR)
#             if auto.initSelf():
#                 # 初始化成功，开始自动化
#                 auto.auto_play()
#             # 发送进度信号
#             self.sig_updated.emit(f"周期计数{auto.pcsCnt}")
#
#         self.sig_finished.emit()
#
#     def stop(self):
#         """停止任务"""
#         self.is_running = False

# OP的基础方法
class Automation:
    # 初始化
    def  __init__(self):

        # ——————————窗口相关的属性——————————
        self.hwnd = 0  # 窗口句柄
        # 窗口是否存在？（游戏可能莫名其妙自己崩溃）
        # 窗口是否仍然在相应？（游戏可能莫名其妙无响应）
        # 窗口是否处于激活状态？（用户可能会点击非游戏界面，导致游戏不处于前台）
        # 窗口位置、尺寸是否正确？
        self.windowStates = [False, False, False, False]
        self.windowArea = [-1, -1, -1, -1]  # window窗口的坐标，四维列表
        self.windowSize = [-1, -1]  # window窗口的尺寸，二维列表
        self.clientArea = [-1, -1, -1, -1]  # client窗口的坐标，四维列表
        self.clientSize = [-1, -1]  # client窗口的尺寸，二维列表
        self.clientAreaMidPoint = [-1, -1]  #

        self.ratio = [-1, -1]  # 坐标系的x、y倍率。只要屏幕存在缩放，那么倍率就不会为1

        # ——————————周期相关的属性——————————
        self.pcsCnt = 0  # 主循环的次数
        self.errUICnt = 0  # 进入脚本认为可以跳过的界面（错误界面errUI）的次数
        self.battleCnt = 0  # 进入局内战斗界面的次数
        self.gameCnt = 0  # 游戏次数
        self.gameTimeStart = datetime.now()  # 时间起点
        self.gameTimeLeftStr = ""  # 本局游戏还剩余的时间：游戏右上角显示，这里是字符串。
        self.gameTimeLeftS = 0  # 本局游戏还剩余的时间：游戏右上角显示，这里的时间单位是秒
        self.gameTimeEnd = 0  # 本局游戏应该在什么时间结束，即当前时间+游戏剩余时间
        self.gameTimeUsed = -1  # 本局游戏已用时间，单位秒
        self.EXP = 0  # 脚本本次运行所获取的所有经验值
        self.fatigue = 0 # PVE模式下，当前疲劳值（注：总疲劳为2400）
        self.endFlg = False     #脚本结束标识（上位机设置）

        self.UI = GameInfo.UI_Err_Other  # 游戏的界面类型，-1为非法值表示未获取到界面信息
        self.UI_valid = GameInfo.UI_Err_Other  # 游戏的有效界面类型，-1为非法值表示未获取到界面信息

        # ——————————平台/模式相关的属性——————————
        self.pcName = ""          #电脑平台
        self.gameMode = ""        #设置的游戏模式
        self.realGameMode = ""  # 游戏实际的模式
        self.curHero = ""  # 当前选择的英雄
        self.YML = RwYaml(filename = Config_File_Path)
        if self.YML.file_read_success:
        # 读取配置表成功，才能进行操作
            self.conf =  ConfigDict(self.YML.config)  # 从config.yml文件中读取所有的配置信息
            self.conf_base = ConfigDict(self.conf.base) #基本设置
            self.conf_hsbl = ConfigDict({}) #黄沙百炼的设置信息

            # a = self.conf_dict.hsbl.desktop.p1.sleep
            # b = self.conf_dict.get_nested('hsbl.desktop.p2.move', default=[315,-110])[1]
            # c = self.conf_dict['hsbl']['desktop']['p1']['sleep']
        else:
            print(f"配置文件config.yml读取失败！脚本已退出！")
            return


        # ——————————不同界面对应的处理方法——————————
        self.dict_UIHandle = {
            # 错误界面
            GameInfo.UI_Err_Other: self.Handle_Err_UI,  # 每个周期交替输入ESC、空格
            GameInfo.UI_Err_Main_LoseServerConnect: self.Handle_Err_UI,  # 后续实现，重启游戏
            GameInfo.UI_Err_LogIn_AccountError: self.Handle_Err_UI,  # 后续实现，重启游戏
            GameInfo.UI_Err_Main_PVEWarehouseFull: self.Handle_Err_Main_PVEWarehouseFull, # 征神仓库已满，结束脚本。

            # 游戏内界面
            # ===无尽试炼===
            GameInfo.UI_PVP_Game_In_WJSL: self.Handle_PVP_Game_In_WJSL,
            # ===PVE：雪满弓刀===
            # GameInfo.UI_PVE_Game_In_1_W: self.Handle_PVE_Game_In_1_W,
            # GameInfo.UI_PVE_Game_In_2_E: self.Handle_PVE_Game_In_2_E,
            # GameInfo.UI_PVE_Game_In_3_ESC: self.Handle_PVE_Game_In_3_ESC,
            GameInfo.UI_PVE_Game_In_4_Battle: self.Handle_PVE_Game_In_4_Battle,
            # GameInfo.UI_PVE_Game_In_5_Succeed: self.Handle_PVE_Game_In_5_Succeed,
            # ===PVE：黄沙百炼===
            GameInfo.UI_PVE_HSBL_Game_In_1_ESC: self.Handle_PVE_HSBL_Game_In_1_ESC,
            GameInfo.UI_PVE_HSBL_Game_In_2_Battle: self.Handle_PVE_HSBL_Game_In_2_Battle,
            # ===PVE：鸿溟之难===
            GameInfo.UI_PVE_HMZN_Game_In_Battle:self.Battle_In_HMZN,
            # ===PVE：万象降临===
            GameInfo.UI_PVE_WXJL_Game_In_Battle:self.Battle_In_WXJL,

            # 登录界面
            GameInfo.UI_LogIn_Announcement: self.Handle_LogIn_Announcement,
            GameInfo.UI_LogIn_AgeRatingReminder: self.Handle_LogIn_AgeRatingReminder,

            # 主界面
            # ===无尽试炼===
            GameInfo.UI_PVP_Main_Prepare: self.Handle_PVP_Main_Prepare,
            GameInfo.UI_PVP_Main_Entering: self.Handle_PVP_Main_Entering,
            # ===PVE：雪满弓刀===
            GameInfo.UI_PVE_Main_Prepare: self.Handle_PVE_Main_Prepare,
            GameInfo.UI_PVE_Main_Sure: self.Handle_PVE_Main_Sure,
            GameInfo.UI_PVE_Main_Tire_Sure: self.Handle_PVE_Main_Tire_Sure,
            # 通用界面
            GameInfo.UI_Daily_Msg: self.Handle_Daily_Msg,

            # 选择界面：PVP
            GameInfo.UI_PVP_Select_Hero: self.Handle_PVP_Select_Hero,
            GameInfo.UI_PVP_Select_Point: self.Handle_PVP_Select_Point,
            # 选择界面：PVE：雪满弓刀/黄沙百炼/鸿溟之难
            GameInfo.UI_PVE_Select_Hero: self.Handle_PVE_Select_Hero,

            # 结算界面：无尽试炼
            GameInfo.UI_PVP_Game_End_WJSL_1: self.Handle_PVP_Game_End_WJSL_1,
            GameInfo.UI_PVP_Game_End_WJSL_2: self.Handle_PVP_Game_End_WJSL_2,
            GameInfo.UI_PVP_Game_End_WJSL_3: self.Handle_PVP_Game_End_WJSL_3,
            GameInfo.UI_PVP_Game_End_WJSL_4: self.Handle_PVP_Game_End_WJSL_4,
            GameInfo.UI_PVP_Game_End_WJSL_5: self.Handle_PVP_Game_End_WJSL_5,
            # 结算界面：PVE：雪满弓刀
            GameInfo.UI_PVE_Game_End_1: self.Handle_PVE_Game_End_1,
            GameInfo.UI_PVE_Game_End_2: self.Handle_PVE_Game_End_2,
            GameInfo.UI_PVE_Game_End_3: self.Handle_PVE_Game_End_3,
            GameInfo.UI_PVE_Game_End_4: self.Handle_PVE_Game_End_4,
            GameInfo.UI_PVE_Game_End_5: self.Handle_PVE_Game_End_5,
            GameInfo.UI_PVE_Game_End_6: self.Handle_PVE_Game_End_6,

            # ESC选择界面
            GameInfo.UI_ESC_Selection_OutGame: self.Handle_ESC_Selection,

            # 过渡界面
            GameInfo.UI_Transition: self.Handle_Transition,

        }

        # ——————————图形化界面相关——————————
        # 只能在实例化类的时候运行一次，后续调用__init__方法时不能运行
        # if not globals().get('G_GuiInit', False):
        # 线程
        self.thread = None
        # 自定义信号的处理
        G_Sig.text_print.connect(self.Info)
        G_Sig.cyc_update.connect(self.update_cyc_info)
        self.ui = ui_loader.load("UI/mainWindow.ui")

        # 初始化游戏模式
        self.ui.cBox_gameMode.addItem(GAME_MODE_PVP_WJSL)
        self.ui.cBox_gameMode.addItem(GAME_MODE_PVE_XMGD)
        self.ui.cBox_gameMode.addItem(GAME_MODE_PVE_HMZN)
        self.ui.cBox_gameMode.addItem(GAME_MODE_PVE_WXJL)
        self.ui.cBox_gameMode.addItem(GAME_MODE_PVE_HSBL)
        # 初始化平台名称
        self.ui.cBox_pcName.addItem(PC_ThinkBook16P)
        self.ui.cBox_pcName.addItem(PC_MyServer)
        self.ui.cBox_pcName.addItem(PC_WuJie14X)
        self.ui.cBox_pcName.addItem(PC_Desktop)
        # 禁用停止按钮
        self.ui.btn_end.setEnabled(False)

        # 从配置文件中获取电脑平台、游戏模式，并更新到UI交互界面
        self.pcName = self.conf_base.get_nested("pc_name")
        self.gameMode = self.conf_base.get_nested("game_mode")
        self.ui.cBox_pcName.setCurrentText(self.pcName)  # 电脑平台
        self.ui.cBox_gameMode.setCurrentText(self.gameMode)


        # 槽函数：要放在界面初始化之后，不然会在初始化时触发下面的槽函数
        self.ui.btn_start.clicked.connect(self.startScript)  # 开始自动操作
        self.ui.btn_end.clicked.connect(self.endScript)  # 立即结束脚本
        self.ui.cBox_gameMode.currentTextChanged.connect(self.save_conf_base)  # 模式、平台发生变化时保存到配置文件
        self.ui.cBox_pcName.currentTextChanged.connect(self.save_conf_base)  # 模式、平台发生变化时保存到配置文件




    def startScript(self):
        self.ui.btn_start.setEnabled(False)  # 同时运行的脚本个数只能为1
        self.ui.btn_end.setEnabled(True)  # 使能停止按钮
        self.endFlg = False                 #重置结束标识

        self.thread = Thread(target=self.mainThread,
                        # args=('参数1', '参数2'),
                        daemon=True
                        )
        self.thread.start()

    def mainThread(self):
        if self.initSelf():
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"设置的游戏模式：{self.gameMode}")
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"设置的电脑平台：{self.pcName}")
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "脚本已启动！")
            self.auto_play()
        else:
            G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error, "initSelf初始化失败，无法启动脚本！")

    def endScript(self):
        # 结束脚本
        self.endFlg = True
        self.ui.btn_start.setEnabled(True)  # 使能开始按钮
        self.ui.btn_end.setEnabled(False)  # 禁用停止按钮


    # ——GUI相关函数：显示信息——
    @staticmethod
    def Info(textBrowser, logLevel, text) -> None :
        if logLevel == LogLevel.info:
            print(text)
            logging.info(text)
            textBrowser.append(text)
            return
        elif logLevel == LogLevel.critical:
            logging.critical(text)
        elif logLevel == LogLevel.error:
            logging.error(text)
        elif logLevel == LogLevel.warning:
            logging.warning(text)
        print(text)
        textBrowser.append(text)
        return

    # 保存配置文件信息
    def save_conf_base(self):
        # 电脑平台
        tmp_pcName = self.ui.cBox_pcName.currentText()
        if tmp_pcName != "" and tmp_pcName != self.pcName:
            self.pcName = tmp_pcName
            self.conf_base.set_nested("pc_name", value=tmp_pcName)   #更新程序使用的配置信息
            self.YML.write_value("base", "pc_name", value=tmp_pcName)        #更新配置信息到配置文件
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"设置的电脑平台：{self.pcName}")  #UI界面提示更新成功
        # 游戏模式
        tmp_gameMode = self.ui.cBox_gameMode.currentText()
        if tmp_gameMode != "" and tmp_gameMode != self.gameMode:
            self.gameMode = tmp_gameMode
            self.conf_base.set_nested("game_mode", value=tmp_gameMode)   #更新程序使用的配置信息
            self.YML.write_value("base", "game_mode", value=tmp_gameMode)        #更新配置信息到配置文件
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"设置的游戏模式：{self.gameMode}")  #UI界面提示更新成功

    # 更新周期计数
    @staticmethod
    def update_cyc_info(textBrowser, msg):
        textBrowser.setText(msg)

    # 游戏启动后，重新获取窗口句柄hwnd、坐标系倍率ratio、窗口信息
    def initSelf(self) -> bool:
        # 重新调用一遍，初始化类的属性
        # globals()['G_GuiInit'] = True  # GUI相关代码已初始化
        # self.__init__()

        # 【1】如果OP绑定过窗口，解绑OP对象之前绑定的窗口
        if OP.IsBind() == 1:
            OP.UnBindWindow()

        # 【2】初始化OP对象
        if not BaseSet.initOP():  # 初始化失败，直接退出。
            G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error,f"OP插件免注册操作失败！脚本已退出。\n"
                  f"请检查OP插件的2个dll路径：\n{path_tools_dll}\n{path_opx64_dll}\n是否正确")
            exit(0)

        # 【3】获取窗口句柄
        self.hwnd = WindowOp.get_window_by_name(GameInfo.windowName_game)
        if self.hwnd == 0:
            G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error, f"未找到窗口“{GameInfo.windowName_game}”，脚本已退出。")
            # G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error,f"未找到窗口“{GameInfo.windowName_game}”，脚本已退出。")
            return False

        # 【4】绑定窗口句柄到OP对象、获取坐标系倍率
        if not WindowOp.bind_window(self.hwnd, self.ratio):
            G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error,f"绑定窗口失败")
            G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error,f"绑定窗口失败，或获取坐标系倍率{self.ratio}失败")
            return False

        # 【5】窗口设置
        # 判断窗口状态，如果有非法状态，则进行恢复
        if not self.updateWindowState():
            self.recoverWindowState()

        # 调试：在PVP的自由训练中，根据不同的电脑，获取其鼠标移动倍率mouseRatio
        # （不是坐标系倍率ratio，ratio只和坐标绝对值有关，而这里的mouseRatio则是鼠标的相对位移）
        # mouseRatio = self.getMouseRatio()
        # 【6】判断脚本设置的游戏模式 和 游戏实际模式是否一致？不一致则直接退出
        if not self.checkGameMode():
            G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error,
                                  f"游戏实际模式（{self.realGameMode}）与脚本设置模式（{self.gameMode}）不同，脚本已退出。")
            self.endScript()
        return True

    def checkGameMode(self) -> bool:
        # 每次“开始”时要重新读取配置信息
        self.YML = RwYaml(filename=Config_File_Path)
        if self.YML.file_read_success:
            # 读取配置表成功，才能进行操作
            self.conf = ConfigDict(self.YML.config)  # 从config.yml文件中读取所有的配置信息
            self.conf_base = ConfigDict(self.conf.base)  # 基本设置
            self.conf_hsbl = ConfigDict({})  # 黄沙百炼的设置信息
            # 从配置文件中获取电脑平台、游戏模式，并更新到UI交互界面
            self.pcName = self.conf_base.get_nested("pc_name")
            self.gameMode = self.conf_base.get_nested("game_mode")
        # 根据不同的电脑平台获取不同的设置信息
        if self.pcName == PC_Desktop:
            self.conf_hsbl = ConfigDict(self.conf.hsbl.desktop)  # 黄沙百炼-Desktop的配置信息
        elif self.pcName == PC_ThinkBook16P:
            self.conf_hsbl = ConfigDict(self.conf.hsbl.thinkbook16p)  # 黄沙百炼-Desktop的配置信息
        elif self.pcName == PC_WuJie14X:
            self.conf_hsbl = ConfigDict(self.conf.hsbl.wujie14x)  # 黄沙百炼-Desktop的配置信息
        else:
            self.conf_hsbl = {}
            G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error,
                                  f"当前平台（{self.pcName}）不在脚本范围内，脚本已退出。")
            self.endScript()
            return False
        if self.conf_hsbl == {}:
            G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error,
                                  f"获取配置表为空，脚本已退出。")
            self.endScript()
            return False
        # 设置的游戏模式

        if self.pcName == "":
            G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error, "未能获取到用户设置的电脑平台，脚本已退出")
            return False
        if self.gameMode == "":
            G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error, "未能获取到用户设置的游戏模式，脚本已退出")
            return False
        tryCnt = 1  #最多识别6次，只要有任意一次识别正确，那就上报正常。
        while tryCnt < 7:
            OP.Sleep(tryCnt * 200)
            self.realGameMode = GetScrInfo.ocrAreaText(WinInfo.Area_Cur_GameMode)
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"第{tryCnt}次识别，游戏实际模式：{self.realGameMode}，脚本设置模式：{self.gameMode}")
            # OCR识别可能会有个别字识别不到，故需要根据关键字纠错
            if "之难" in self.realGameMode or "鸿" in self.realGameMode:
                self.realGameMode = "鸿溟之难"
            elif "黄沙" in self.realGameMode:
                self.realGameMode = "黄沙百炼"
            elif "雪" in self.realGameMode:
                self.realGameMode = "雪满弓刀"
            elif "万象" in self.realGameMode:
                self.realGameMode = "万象降临"
            elif "无尽" in self.realGameMode:
                self.realGameMode = "无尽试炼"
            else:   #如果识别结果不在以上范围内，说明可能在游戏界面内，此时默认模式为正确的模式
                if tryCnt >= 4 :    # 识别4次及以上都没有结果
                    self.realGameMode = self.gameMode
                    return True
            if self.gameMode in self.realGameMode:
               return True
            tryCnt += 1
        return False    #6次识别均异常，报故障


    def getMouseRatio(self) -> float:
        # 思路：在训练场向左移动固定的数值：300，然后查看方向
        mRatio = -1.0
        cnt = 0
        MouseOp.LeftClickAreaRandom(WinInfo.Area_Char_PVP_Main, self.ratio)  # 点击开始，进入自由训练
        OP.Sleep(22000)
        while cnt < 1280:
            cnt += 1
            MouseOp.MoveRT(-1, 0)  # 每次移动两个像素点
            # 识别坐标点(639, 372)-货郎下划线的色彩，如果是红色，则停止
            curColor = OP.GetColor(639, 372)
            # G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"cnt={cnt}，颜色={curColor}")
            if self.is_red(curColor):
                # 说明：经过多次测试，Desktop台式机的cnt在412～413范围内，
                # 即左移412/413个像素点，就能到达预定位置：货郎的红色下划线。故以此作为对比基数，计算新环境下的倍率
                # Desktop：cnt取值412～413
                # MyServer：cnt取值405～406
                mRatio = f"{(cnt / 412):.4f}"  # 只保留小数点后4位有效数字
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"cnt={cnt}，颜色={curColor}")
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"mRatio={mRatio}")
                break
            # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
            self.UserPause()
        return mRatio

    @staticmethod
    def is_red(hex_color):
        # 判断十六进制字符串是否表示红色
        # 移除颜色前的 '#'
        hex_color = hex_color.lstrip('#')

        # 将十六进制颜色转换为RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # 判断是否为红色范围
        if r > 130 and g < 100 and b < 100:
            return True
        return False

    # 自动化操作：无尽试炼
    def auto_play(self):
        # 1、窗口激活
        if OP.SetWindowState(self.hwnd, 12) == 1:  # 激活窗口，显示到前台
            OP.SetWindowState(self.hwnd, 7)
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"激活窗口成功")
        else:
            G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error,f"激活窗口失败")

        # 2、主循环
        self.pcsCnt = 0  # 周期计数清零

        while True:
            # #————————————————————调试————————————————————————————
            # self.Handle_PVE_HSBL_Game_In_2_Battle()
            # # ————————————————————调试————————————————————————————

            self.pcsCnt += 1  # 计数器自增
            OP.Sleep(ParamTime.sleep_main_cycle)  # 周期固定休眠时间

            # 周期更新GUI界面信息
            G_Sig.cyc_update.emit(self.ui.lEdit_cycCnt, str(self.pcsCnt))   #周期计数
            G_Sig.cyc_update.emit(self.ui.lEdit_fatigue, str(self.fatigue)) #已用疲劳
            G_Sig.cyc_update.emit(self.ui.lEdit_gameCnt, str(self.gameCnt)) #游戏局数

            if self.endFlg: #上位机主动结束标识为真时，结束主循环
                G_Sig.cyc_update.emit(self.ui.lEdit_cycCnt, "周期结束")
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "周期任务已结束。")
                break

            isUINormal = False  # 默认界面为异常，只有非过渡界面才认为是正常的

            # 获取当前的UI界面
            time1 = datetime.now()
            self.UI = self.getCurUI()
            time2 = datetime.now()
            time_UI_Recognition = (time2 - time1).total_seconds()
            # if time_UI_Recognition < 0.1:  # 如果识别界面消耗的时间太短了，主动休眠一段时间。
            #     OP.Sleep(ParamTime.slp_cmd * 2)

            if self.UI != GameInfo.UI_Transition:
                # 非过渡界面，才认为是有效界面
                self.UI_valid = self.UI
                isUINormal = True
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"周期计数：{self.pcsCnt}，本次界面识别耗时：{time_UI_Recognition:.6f}秒，当前界面：{self.UI}，当前有效界面：{self.UI_valid}")


            # 过渡界面监控（监控过渡界面连续出现的次数）
            pSelfCheck(isUINormal, PscRltAll[FAULT_TRANSITION_UI], PscCfgAll[FAULT_TRANSITION_UI])
            # 如果错误界面达到故障次数
            if not PscRltAll[FAULT_TRANSITION_UI].reportRlt:
                self.UI_valid = GameInfo.UI_Err_Other  # 1-将当前有效界面置为故障界面
                self.Handle_Err_UI()  # 2-调用故障处理函数

            # 利用字典，根据响应的UI直接调用对应的处理函数
            self.dict_UIHandle.get(self.UI)()  # `()` 是用来调用函数的
            # self.dict_UIHandle.get(self.UI, self.Handle_Err_UI())()  # `()` 是用来调用函数的

            # 信息申报
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"当前游戏模式：{self.gameMode}\n当前疲劳值：{self.fatigue}")

    # 获取当前的界面类型：主要分2大类，游戏内，游戏外。
    # 游戏内，需要做到快速响应。游戏外，需要做到精准识别。
    def getCurUI(self) -> int:
        # ————————————游戏内界面(无尽试炼模式)-非返魂-识别————————————
        # ===无尽试炼===
        if self.gameMode == GAME_MODE_PVP_WJSL:
            # 如果游戏局内时间超过XX秒，直接返回当前界面为游戏内界面。游戏内，每隔N个周期更新游戏剩余时间
            if self.gameTimeLeftS >= ParamTime.default_InGame_LefTimeS_MAX:
                return GameInfo.UI_PVP_Game_In_WJSL

            # 是否为游戏内界面，未死亡：特征1，左上角的“排名”，无尽试炼特有：特征2，护甲粉末，特征3，凝血丸（因为无尽试炼出生就有）
            OP.Sleep(ParamTime.slp_OCR)
            # 如果OCR识别到“排名”，认为是在游戏内
            if WinInfo.Text_Char_Game_In_WJSL_1 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_In_WJSL_1):
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入游戏内界面，特征字：{WinInfo.Text_Char_Game_In_WJSL_1}")
                return GameInfo.UI_PVP_Game_In_WJSL

            # 通过查找屏幕截图中是否存在特征图片护甲粉末ArmorPowder1.bmp，来判断是否为游戏内界面
            OP.Sleep(ParamTime.slp_findPic)
            # 找到图片：ArmorPowder
            findPicRlt = GetScrInfo.findPic(WinInfo.Pic_Char_Game_In_WJSL_Powder1, self.clientArea)
            if findPicRlt[0] != -1:
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：找到图片ArmorPowder2.bmp左上角坐标：{findPicRlt[1:]}：此时处于游戏内界面")
                return GameInfo.UI_PVP_Game_In_WJSL

            # #通过查找屏幕截图中是否存在特征图片凝血丸BloodPill1.bmp，来判断是否为游戏内界面
            OP.Sleep(ParamTime.slp_findPic)
            # 找到图片：BloodPill
            findPicRlt = GetScrInfo.findPic(WinInfo.Pic_Char_Game_In_WJSL_Pill1, self.clientArea)
            if findPicRlt[0] != -1:
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：找到图片BloodPill2.bmp左上角坐标：{findPicRlt[1:]}：此时处于游戏内界面")
                return GameInfo.UI_PVP_Game_In_WJSL
        # ===PVE征神，雪满弓刀===
        elif self.gameMode == GAME_MODE_PVE_XMGD:
            # 前提：上一个有效界面是英雄选择界面 或 自己
            if (self.UI_valid == GameInfo.UI_PVE_Select_Hero
                    or self.UI_valid == GameInfo.UI_PVE_Game_In_4_Battle
                    or self.UI_valid == GameInfo.UI_Err_Other):
                # 如果OCR识别到“势比登天”
                if WinInfo.Text_Char_Game_In_PVE_1 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_In_PVE_1):
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入游戏内界面，特征字：{WinInfo.Text_Char_Game_In_PVE_1}")
                    return GameInfo.UI_PVE_Game_In_4_Battle

            # # 游戏内界面4-战斗界面：如果游戏使用时间未满XX秒，直接返回当前界面为游戏内界面-战斗界面。
            # if 0 < self.gameTimeUsed < ParamTime.default_InGame_TimeUsed_PVE_XMGD:
            #     G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"本局游戏已用{self.gameTimeUsed:.2f}秒，"
            #                  f"不满{ParamTime.default_InGame_TimeUsed_PVE_XMGD}秒，直接判定当前界面为游戏内战斗界面。")
            #     return GameInfo.UI_PVE_Game_In_4_Battle

            # # 前提：上一个有效界面是游戏内界面3-到达传送点或游戏内界面4-战斗界面
            # # 【界面入口-2】局内战斗界面-通关暂未成功
            # if (self.UI_valid == GameInfo.UI_PVE_Game_In_3_ESC
            #         or self.UI_valid == GameInfo.UI_PVE_Game_In_4_Battle
            #         # or self.UI_valid == GameInfo.UI_PVE_Game_In_45_Again_W
            #         or self.UI_valid == GameInfo.UI_Err_Other):
            #     # 如果OCR识别到“昆仑主母”
            #     if WinInfo.Text_Char_Game_in_PVE_4 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_in_PVE_4):
            #         G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info,
            #             f"getCurUI：OCR识别到进入游戏内界面4-战斗界面，特征字：{WinInfo.Text_Char_Game_in_PVE_4}")
            #         return GameInfo.UI_PVE_Game_In_4_Battle
            # # 游戏内界面1-未到达传送点，长按W前往传送点
            # # 前提：上一个有效界面是英雄选择界面 或 自己
            # if self.UI_valid == GameInfo.UI_PVE_Select_Hero or self.UI_valid == GameInfo.UI_PVE_Game_In_1_W:
            #     # 如果OCR识别到“势比登天”
            #     if WinInfo.Text_Char_Game_In_PVE_1 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_In_PVE_1):
            #         G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入游戏内界面1-未传送，特征字：{WinInfo.Text_Char_Game_In_PVE_1}")
            #         return GameInfo.UI_PVE_Game_In_1_W

            # # 游戏内界面3-传送后出现的过渡动画，可以ESC跳过
            # # 前提：上一个有效界面是游戏内界面2-到达传送点
            # if self.UI_valid == GameInfo.UI_PVE_Game_In_1_W or self.UI_valid == GameInfo.UI_PVE_Game_In_3_ESC:
            #     # 如果OCR识别到“跳过”
            #     if WinInfo.Text_Char_Game_in_PVE_3 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_in_PVE_3):
            #         G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info,
            #             f"getCurUI：OCR识别到进入游戏内界面3-过渡动画，特征字：{WinInfo.Text_Char_Game_in_PVE_3}")
            #         return GameInfo.UI_PVE_Game_In_3_ESC
            # # 游戏内界面5-通关成功，可以ESC返回大厅
            # # 前提：上一个有效界面是游戏内界面4-战斗界面
            # if self.UI_valid == GameInfo.UI_PVE_Game_In_4_Battle or self.UI_valid == GameInfo.UI_PVE_Game_In_5_Succeed:
            #     # 如果OCR识别到“通关成功”
            #     if WinInfo.Text_Char_Game_in_PVE_5 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_in_PVE_5):
            #         G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info,
            #             f"getCurUI：OCR识别到进入游戏内界面5-通关成功，特征字：{WinInfo.Text_Char_Game_in_PVE_5}")
            #         return GameInfo.UI_PVE_Game_In_5_Succeed
        # ===PVE征神，黄沙百炼===
        elif self.gameMode == GAME_MODE_PVE_HSBL:
            # # 游戏内界面4-战斗界面：如果游戏使用时间未满XX秒，直接返回当前界面为游戏内界面-战斗界面。
            # if 0 < self.gameTimeUsed < ParamTime.default_InGame_TimeUsed_PVE_XMGD:
            #     G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"本局游戏已用{self.gameTimeUsed:.2f}秒，"
            #                  f"不满{ParamTime.default_InGame_TimeUsed_PVE_XMGD}秒，直接判定当前界面为游戏内战斗界面。")
            #     return GameInfo.UI_PVE_HSBL_Game_In_2_Battle
            # 【界面入口-2】局内战斗界面-尚未开箱
            if (self.UI_valid == GameInfo.UI_PVE_HSBL_Game_In_1_ESC
                    or self.UI_valid == GameInfo.UI_PVE_HSBL_Game_In_2_Battle
                    or self.UI_valid == GameInfo.UI_Err_Other):
                # 如果OCR识别到“寻找出路”
                if WinInfo.Text_Char_Game_In_PVE_HSBL_2 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_In_PVE_HSBL_2):
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info,
                        f"getCurUI：OCR识别到进入游戏内界面2-战斗界面，特征字：{WinInfo.Text_Char_Game_In_PVE_HSBL_2}")
                    return GameInfo.UI_PVE_HSBL_Game_In_2_Battle
            # 游戏内界面3-传送后出现的过渡动画，可以ESC跳过
            # 前提：上一个有效界面是英雄选择界面/自己
            if self.UI_valid == GameInfo.UI_PVE_Select_Hero or self.UI_valid == GameInfo.UI_PVE_HSBL_Game_In_1_ESC:
                # 如果OCR识别到“跳过”
                if WinInfo.Text_Char_Game_in_PVE_HSBL_1 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_in_PVE_HSBL_1):
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info,
                        f"getCurUI：OCR识别到进入游戏内界面-过渡动画，特征字：{WinInfo.Text_Char_Game_in_PVE_3}")
                    return GameInfo.UI_PVE_HSBL_Game_In_1_ESC
        # ===PVE征神，鸿溟之难===
        elif self.gameMode == GAME_MODE_PVE_HMZN:
            # 【界面入口-2】局内战斗界面-尚未通关或未满最大时间
            if (self.UI_valid == GameInfo.UI_PVE_HMZN_Game_In_Battle
                    or self.UI_valid == GameInfo.UI_PVE_Select_Hero
                    or self.UI_valid == GameInfo.UI_Err_Other):
                # 如果OCR识别到“潮汐之间”
                if WinInfo.Text_Char_Game_In_PVE_HMZN_1 in GetScrInfo.ocrAreaText(
                        WinInfo.Area_Char_Game_In_PVE_HMZN_1):
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info,
                        f"getCurUI：OCR识别到进入游戏内界面-战斗界面，特征字：{WinInfo.Text_Char_Game_In_PVE_HMZN_1}")
                    return GameInfo.UI_PVE_HMZN_Game_In_Battle
        # ===PVE征神，万象降临===
        elif self.gameMode == GAME_MODE_PVE_WXJL:
            # 【界面入口-2】局内战斗界面-尚未通关或未满最大时间
            if (self.UI_valid == GameInfo.UI_PVE_WXJL_Game_In_Battle
                    or self.UI_valid == GameInfo.UI_PVE_Select_Hero
                    or self.UI_valid == GameInfo.UI_Err_Other):
                # 如果OCR识别到“落日之火”
                if WinInfo.Text_Char_Game_In_PVE_WXJL_1 in GetScrInfo.ocrAreaText(
                        WinInfo.Area_Char_Game_In_PVE_WXJL_1):
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info,
                        f"getCurUI：OCR识别到进入游戏内界面-战斗界面，特征字：{WinInfo.Text_Char_Game_In_PVE_WXJL_1}")
                    return GameInfo.UI_PVE_WXJL_Game_In_Battle


        # ————————————游戏结算界面识别————————————
        # ===无尽试炼===
        if self.gameMode == GAME_MODE_PVP_WJSL:
            # 结算界面1：“前三甲”。游戏会自动跳过该界面，脚本可以不用识别。
            # 是否为结算界面1：战斗前三甲？
            OP.Sleep(ParamTime.slp_OCR)
            # OCR识别："战斗前三甲"
            if WinInfo.Text_Char_WJSL_End_1 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_WJSL_End_1):
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入结算界面1：战斗前三甲")
                return GameInfo.UI_PVP_Game_End_WJSL_1

            # 是否为结算界面2：积分榜？
            OP.Sleep(ParamTime.slp_OCR)
            # OCR识别："返回大厅"
            if WinInfo.Text_Char_WJSL_End_2 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_WJSL_End_2):
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入结算界面2：积分榜")
                return GameInfo.UI_PVP_Game_End_WJSL_2

            # 是否为结算界面3：无尽试炼等阶？
            OP.Sleep(ParamTime.slp_OCR)
            # OCR识别："试炼"
            if WinInfo.Text_Char_WJSL_End_3 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_WJSL_End_3):
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入结算界面3：无尽试炼等阶")
                return GameInfo.UI_PVP_Game_End_WJSL_3

            # 当前界面是否为结算界面4-通行证经验值界面？下面两个方式都可以认为是经验结算界面
            OP.Sleep(ParamTime.slp_OCR)
            # OCR识别："恭喜获得"
            if WinInfo.Text_Char_WJSL_End_4 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_WJSL_End_4):
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入结算界面4：通行证经验")
                return GameInfo.UI_PVP_Game_End_WJSL_4

            # 当前界面是否为结算界面5-游戏等级经验，没什么用。
            OP.Sleep(ParamTime.slp_OCR)
            # OCR识别："等级"
            if WinInfo.Text_Char_WJSL_End_5 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_WJSL_End_5):
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入结算界面5：游戏等级经验")
                return GameInfo.UI_PVP_Game_End_WJSL_5
        # ===PVE征神，雪满弓刀/黄沙百炼/鸿溟之难/万象降临===
        elif (self.gameMode == GAME_MODE_PVE_XMGD
              or self.gameMode == GAME_MODE_PVE_HSBL
              or self.gameMode == GAME_MODE_PVE_HMZN
              or self.gameMode == GAME_MODE_PVE_WXJL):
            # 结算界面1：伤害/用时
            # # OCR识别到"胜利"/“失败”，且上一个界面为游戏内成功通关
            # if self.UI_valid == GameInfo.UI_PVE_Game_In_5_Succeed:
            if (WinInfo.Text_Char_XMGD_End_1 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_XMGD_End_1)
                    or WinInfo.Text_Char_HSBL_End_1 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_XMGD_End_1)):
                OP.Sleep(ParamTime.slp_OCR)
                if not WinInfo.Text_Char_XMGD_End_2 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_XMGD_End_2):
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入结算界面1：伤害/用时")
                    return GameInfo.UI_PVE_Game_End_1

            # 是否为结算界面2：各类经验
            # OCR识别："战斗奖励"，且上一个界面为结算界面1
            if self.UI_valid == GameInfo.UI_PVE_Game_End_1 or self.UI_valid == GameInfo.UI_PVE_Game_End_2:
                if WinInfo.Text_Char_XMGD_End_2 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_XMGD_End_2):
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入结算界面2：各类经验")
                    return GameInfo.UI_PVE_Game_End_2

            # 是否为结算界面3：用户等级
            # OCR识别："等级"，且上一个界面为结算界面2
            if self.UI_valid == GameInfo.UI_PVE_Game_End_2 or self.UI_valid == GameInfo.UI_PVE_Game_End_3:
                if WinInfo.Text_Char_XMGD_End_3 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_XMGD_End_3):
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入结算界面3：用户等级")
                    return GameInfo.UI_PVE_Game_End_3

            # 是否为结算界面4-潜能等级
            # OCR识别："潜能等级"，且上一个界面为结算界面3
            if self.UI_valid == GameInfo.UI_PVE_Game_End_3 or self.UI_valid == GameInfo.UI_PVE_Game_End_4:
                if WinInfo.Text_Char_XMGD_End_4 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_XMGD_End_4):
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入结算界面3：潜能等级")
                    return GameInfo.UI_PVE_Game_End_4

            # 是否为结算界面5-恭喜获得，不一定会出现。
            # OCR识别："返回"，且上一个界面为结算界面
            if GameInfo.UI_PVE_Game_End_1 <= self.UI_valid <= GameInfo.UI_PVE_Game_End_4:
                if WinInfo.Text_Char_XMGD_End_5 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_XMGD_End_5):
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入结算界面5-恭喜获得")
                    return GameInfo.UI_PVE_Game_End_5

            # 是否为结算界面6-恭喜获得，不一定会出现。
            # OCR识别："获得"，且上一个界面为结算界面
            if GameInfo.UI_PVE_Game_End_1 <= self.UI_valid <= GameInfo.UI_PVE_Game_End_5:
                if WinInfo.Text_Char_XMGD_End_6 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_XMGD_End_6):
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入结算界面5-恭喜获得")
                    return GameInfo.UI_PVE_Game_End_6

        # ————————————主界面识别————————————
        # ===无尽试炼===
        if self.gameMode == GAME_MODE_PVP_WJSL:
            # 是否为主界面-未点击“开始游戏”
            OP.Sleep(ParamTime.slp_OCR)
            # OCR识别："开始游戏"
            if WinInfo.Text_Char_Main_Prepare in GetScrInfo.ocrAreaText(WinInfo.Area_Char_PVP_Main):
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入主界面-未点击“开始游戏”")
                return GameInfo.UI_PVP_Main_Prepare

            # 是否为主界面-已点击“开始游戏”，正在匹配玩家
            OP.Sleep(ParamTime.slp_OCR)
            # OCR识别："取消"
            if WinInfo.Text_Char_Main_Entering in GetScrInfo.ocrAreaText(WinInfo.Area_Char_PVP_Main):
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入主界面-已点击“开始游戏”，正在匹配玩家")
                return GameInfo.UI_PVP_Main_Entering
        # ===PVE征神，雪满弓刀/黄沙百炼/鸿溟之难/万象降临===
        elif (self.gameMode == GAME_MODE_PVE_XMGD
              or self.gameMode == GAME_MODE_PVE_HSBL
              or self.gameMode == GAME_MODE_PVE_HMZN
              or self.gameMode == GAME_MODE_PVE_WXJL):
            # 【界面入口-1】主界面
            # OCR识别："开始征神"
            if ((GameInfo.UI_PVE_Game_End_1 <= self.UI_valid <= GameInfo.UI_PVE_Game_End_6)
                    or self.UI_valid == GameInfo.UI_Err_Other):
                if WinInfo.Text_Char_PVE_Main in GetScrInfo.ocrAreaText(WinInfo.Area_Char_PVE_Main)\
                    or WinInfo.Text_Char_PVE_Main_2 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_PVE_Main):
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入主界面-未点击“开始征神”")
                    return GameInfo.UI_PVE_Main_Prepare
            # 前提：上一个界面是主界面
            if self.UI_valid == GameInfo.UI_PVE_Main_Prepare or self.UI_valid == GameInfo.UI_PVE_Main_Sure:
                if WinInfo.Text_Char_PVE_Main_Sure in GetScrInfo.ocrAreaText(WinInfo.Area_Char_PVE_Main_Sure):
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入主界面-关闭疲劳的确认界面")
                    return GameInfo.UI_PVE_Main_Sure
            # 前提：上一个界面是主界面
            if self.UI_valid == GameInfo.UI_PVE_Main_Prepare or self.UI_valid == GameInfo.UI_PVE_Main_Tire_Sure:
                if WinInfo.Text_Char_PVE_Main_Tire_Sure in GetScrInfo.ocrAreaText(WinInfo.Area_Char_PVE_Main_Tire_Sure):
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入主界面-疲劳值已达第5档")
                    return GameInfo.UI_PVE_Main_Tire_Sure

        # 是否为主界面-消息弹窗
        OP.Sleep(ParamTime.slp_OCR)
        # OCR识别："取消"
        if WinInfo.Text_Char_Daily_Msg in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Daily_Msg):
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入主界面-已点击“开始游戏”，正在匹配玩家")
            return GameInfo.UI_Daily_Msg

        # ————————————游戏开始：英雄选择界面识别————————————
        # ===无尽试炼===
        if self.gameMode == GAME_MODE_PVP_WJSL:
            # 是否为英雄选择界面？
            OP.Sleep(ParamTime.slp_OCR)
            # OCR识别："英雄选择"
            if WinInfo.Text_Char_Select_Hero in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Select_Hero):
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入英雄选择界面")
                return GameInfo.UI_PVP_Select_Hero
        # ===PVE征神，雪满弓刀/鸿溟之难/万象降临===
        elif (self.gameMode == GAME_MODE_PVE_XMGD
              or self.gameMode == GAME_MODE_PVE_HMZN
              or self.gameMode == GAME_MODE_PVE_WXJL):
            # 前一个界面是主界面/消息弹窗界面/不勾选疲劳确认界面/疲劳值已满确认界面
            if (self.UI_valid == GameInfo.UI_PVE_Main_Prepare
                    or self.UI_valid == GameInfo.UI_Daily_Msg
                    or self.UI_valid == GameInfo.UI_PVE_Main_Sure
                    or self.UI_valid == GameInfo.UI_PVE_Main_Tire_Sure
                    or self.UI_valid == GameInfo.UI_PVE_Select_Hero):
                # OCR识别："英雄选择"
                if WinInfo.Text_Char_PVE_Select_Hero in GetScrInfo.ocrAreaText(WinInfo.Area_Char_PVE_Select_Hero):
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入英雄选择界面")
                    return GameInfo.UI_PVE_Select_Hero
        # ===PVE征神，黄沙百炼===
        elif self.gameMode == GAME_MODE_PVE_HSBL:
            # 前一个界面是主界面/消息弹窗界面/不勾选疲劳确认界面/疲劳值已满确认界面
            if (self.UI_valid == GameInfo.UI_PVE_Main_Prepare
                    or self.UI_valid == GameInfo.UI_Daily_Msg
                    or self.UI_valid == GameInfo.UI_PVE_Main_Sure
                    or self.UI_valid == GameInfo.UI_PVE_Main_Tire_Sure
                    or self.UI_valid == GameInfo.UI_PVE_Select_Hero):
                # OCR识别："英雄选择"
                if WinInfo.Text_Char_PVE_Select_Hero in GetScrInfo.ocrAreaText(
                        WinInfo.Area_Char_PVE_Select_Hero):
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入英雄选择界面")
                    return GameInfo.UI_PVE_Select_Hero
        # ————————————游戏开始：跳点选择界面识别————————————
        # # 是否为跳点选择界面【无尽试炼没有跳点选择】
        # OP.Sleep(ParamTime.slp_OCR)
        # OCR识别“英雄选择”
        # if WinInfo.Text_Char_Select_Hero in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Select_Hero):
        #     G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入英雄选择界面")
        #     return GameInfo.UI_PVP_Select_Hero

        # ————————————登录界面识别————————————
        # OP.Sleep(ParamTime.slp_OCR)
        # OCR识别："公告"
        if WinInfo.Text_Char_Game_Start_1 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_Start_1):
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入登录界面1：公告界面")
            return GameInfo.UI_LogIn_Announcement

        # OP.Sleep(ParamTime.slp_OCR)
        # 找到图片："适龄提示16+"
        if GetScrInfo.findPic(WinInfo.Pic_Char_Game_Start_2, self.clientArea)[0] >= 0:
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到进入登录界面2：适龄提示")
            return GameInfo.UI_LogIn_AgeRatingReminder

        # ————————————错误界面识别————————————
        # 主界面错误：提示，失去服务器连接
        # OP.Sleep(ParamTime.slp_OCR)
        # OCR识别："临时仓库中存在未领取的征神魂玉"
        if WinInfo.Text_Char_Main_Tip_PVEWarehouseFull in GetScrInfo.ocrAreaText(
                WinInfo.Area_Char_Main_Tip_PVEWarehouseFull):
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到主界面异常：临时仓库中存在未领取的征神魂玉")
            return GameInfo.UI_Err_Main_PVEWarehouseFull

        # OCR识别："失去服务器链接"
        if WinInfo.Text_Char_Main_Err_LoseServerConnect in GetScrInfo.ocrAreaText(
                WinInfo.Area_Char_Main_Err_LoseServerConnect):
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到主界面错误：失去服务器连接")
            return GameInfo.UI_Err_Main_LoseServerConnect

        # 登录界面2：错误：提示，账号异常
        # OP.Sleep(ParamTime.slp_OCR)
        # OCR识别："账号异常"
        if WinInfo.Text_Char_Game_Start_2_Err in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_Start_2_Err):
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到启动界面错误：账号异常")
            return GameInfo.UI_Err_LogIn_AccountError

        # 未录入信息的其他错误界面，弹窗名称是“提示”
        # OP.Sleep(ParamTime.slp_OCR)
        if WinInfo.Text_DialogBox_Title_Name_Prompt in GetScrInfo.ocrAreaText(WinInfo.Area_DialogBox_Title_Name):
            Prompt = GetScrInfo.ocrAreaText(WinInfo.Area_DialogBox_Err_Content)
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurUI：OCR识别到对话框弹窗，提示错误信息：{Prompt}")
            return GameInfo.UI_Err_Other

        # ————————————不符合上述任何一种界面：过渡界面————————————
        # 不符合任何一个特征，就认为进入了过渡界面。什么也不做，等待指定的时间：10秒
        G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error,f"getCurUI：进入过渡界面。")
        return GameInfo.UI_Transition

    # ==========PVP无尽试炼===================================
    # 游戏内的操作，无尽试炼
    def Handle_PVP_Game_In_WJSL(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        # 重复进行空手右键蓄力
        G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "【进入游戏局内界面：】")
        if self.getGameTimeLeft():
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"本局游戏剩余时间：{self.gameTimeLeftStr}")
        # 下面进行右键三连蓄力
        MouseOp.RightClickAreaRandom(WinInfo.Area_Random_left_move, self.ratio)
        OP.Sleep(300)
        MouseOp.RightClickAreaRandom(WinInfo.Area_Random_left_move, self.ratio)
        OP.Sleep(300)
        MouseOp.RightClickAreaRandom(WinInfo.Area_Random_left_move, self.ratio)
        OP.Sleep(300)
        MouseOp.RightClickAreaRandom(WinInfo.Area_Random_left_move, self.ratio)
        if self.pcsCnt % 2 ==0:
            OP.Sleep(300)
            KeyOp.PressKey(OPKeyCode.F)
            KeyOp.PressKey(OPKeyCode.F)
        else:
            OP.Sleep(300)
            KeyOp.PressKey(OPKeyCode.V)
            KeyOp.PressKey(OPKeyCode.V)

    # 主界面，未点击“开始游戏”
    def Handle_PVP_Main_Prepare(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "【进入主界面：未点击“开始游戏”】")
        if MouseOp.LeftClickAreaRandom(WinInfo.Area_Char_PVP_Main, self.ratio):
            # self.gameTime += 1 #这里获取游戏次数不对，因为可能存在匹配失败，多次点击“开始游戏”的情况
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "主界面：点击“开始游戏”成功，正在匹配……")
            # 点击开始后进入游戏，休眠等15秒进游戏：尝试匹配15秒
            OP.Sleep(ParamTime.slp_After_Start_Game)

    # 主界面，已经点击“开始游戏”，正在匹配玩家，当前特征区域显示“取消”
    def Handle_PVP_Main_Entering(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "【进入主界面：正在匹配】")
        if MouseOp.LeftClickAreaRandom(WinInfo.Area_Char_PVP_Main, self.ratio):
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"主界面：等待{ParamTime.slp_After_Start_Game}"
                         f"秒后游戏未开始，匹配失败，取消匹配，等待下一次脚本点击“开始游戏”")

    # 进入游戏，选择英雄的界面
    def Handle_PVP_Select_Hero(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "【进入英雄选择界面：】")
        if MouseOp.LeftClickAreaRandom(WinInfo.Area_Select_Cur_Hero, self.ratio):
            self.curHero = GetScrInfo.ocrAreaText(WinInfo.Area_Hero_Name)
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"已选择：{self.curHero}")

    # 进入游戏，选择跳点的界面
    def Handle_PVP_Select_Point(self):
        # 不选跳点，随机跳点，等待进入游戏
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()

    # 无尽试炼-结算界面1：这个界面显示几秒钟后，游戏能够会自行跳过
    def Handle_PVP_Game_End_WJSL_1(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "【已跳过结算界面1】")

    # 无尽试炼-结算界面2：空格跳过
    def Handle_PVP_Game_End_WJSL_2(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        # 后续：OCR识别获取击败数量
        G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "【进入结算界面2】")
        if MouseOp.LeftClickAreaRandom(WinInfo.Area_Char_WJSL_End_2, self.ratio):
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "跳过了结算界面2")

    # 无尽试炼-结算界面3：空格跳过
    def Handle_PVP_Game_End_WJSL_3(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        # 后续：OCR识别获取增加的经验
        G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "【进入结算界面3】")
        if MouseOp.LeftClickAreaRandom(WinInfo.Area_Skip_WJSL_End_3, self.ratio):
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "跳过了结算界面3")

    # 无尽试炼-结算界面4：OCR获取通行证经验值，空格跳过
    def Handle_PVP_Game_End_WJSL_4(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        # self.gameCnt += 1
        # 后续：OCR识别获取增加的经验
        G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "【进入结算界面4】")
        # 获取经验值EXP
        curEXP = self.getEXP_WJSJ()
        if curEXP > 0:
            self.EXP += curEXP
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"本局游戏经验值：{curEXP}(若为0则表示OCR识别经验值失败。)")
        else:
            G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.warning,f"OCR识别经验值失败。")
        G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"本次脚本已获取游戏经验值：{self.EXP}")
        if KeyOp.PressKey(OPKeyCode.Space):
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "使用空格跳过结算界面4")

    # 无尽试炼-结算界面5：空格跳过
    def Handle_PVP_Game_End_WJSL_5(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "【进入结算界面5】")
        if KeyOp.PressKey(OPKeyCode.Space):
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "使用空格跳过结算界面5")

    # ==========PVE黄沙百炼===================================
    def Handle_PVE_HSBL_Game_In_1_ESC(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        # 可以ESC跳过的界面
        KeyOp.PressKey(OPKeyCode.ESC)
        if self.pcName == "MyServer":
            OP.Sleep(3000)  #由于MyServer处理器和显卡性能极差，故需要等待3秒，让地图加载完毕
        else:
            OP.Sleep(1600)  # 休眠1秒，等待游戏加载出界面。否则会识别为过渡界面。

    def Handle_PVE_HSBL_Game_In_2_Battle(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        self.battleCnt += 1
        # 第一次进入局内战斗界面时，初始化游戏开始时间
        if self.battleCnt == 1:
            self.gameTimeStart = datetime.now()
        # 因为黄沙百炼地图需要调整特定的视角、奔跑指定的距离，所以不同的电脑，有不同的参数。这些参数御鼠标DPI、视角灵敏度有关。
        self.Battle_In_HSBL(cur_mouse_ratio)

    def Battle_In_HSBL(self, mouse_ratio:float):
        # ——————————————————————————————————————————————————————————————————————————————————————————————
        # 以下所有写死的数据，均是基于笔记本电脑【ThinkBook16P】
        # 游戏设置中视角灵敏度：50， 视角灵敏度(射击模式)：20，
        # 鼠标DPI：2000，
        # Windows11系统设置中鼠标速度：10， 控制面板的指针选项的“选择指针移动速度”为第6格的位置，并且关闭“增强指针精确度”
        # ——————————————————————————————————————————————————————————————————————————————————————————————
        OP.Sleep(self.conf_hsbl.get_nested('p1.sleep', default=1000))
        # OP.Sleep(3000)  #由于MyServer处理器和显卡性能极差，故需要等待3秒，让地图加载完毕  #【可调参数】
        # ————————1、前进到P2，调整视角———————————————————————————————————————————————————————————————————
        self.UserPause()  # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        KeyOp.HoldTwoKey(OPKeyCode.W,
                         self.conf_hsbl.get_nested('p2.run', default=[1020,1000])[0],
                         OPKeyCode.Shift,
                         self.conf_hsbl.get_nested('p2.run', default=[1020,1000])[1])  #【可调参数】
        OP.Sleep(300)
        MouseOp.MoveR(
            round((self.conf_hsbl.get_nested('p2.move', default=[315,-110])[0]) * mouse_ratio),
            round((self.conf_hsbl.get_nested('p2.move', default=[315,-110])[1]) * mouse_ratio))  # 视角往右、往上移动  #【可调参数】
        # OP.Sleep(300)
        OP.Sleep(self.conf_hsbl.get_nested('p2.sleep', default=200))   # 电脑性能差，多休眠一段时间  #【可调参数】
        # ————————2、钩锁到P3————————————————————————————————————————————————————————————————————————————
        # 到达P2，视角已调整，按Q+鼠标左键
        KeyOp.PressKey(OPKeyCode.Q)
        OP.Sleep(300)
        MouseOp.LeftClickNow()
        OP.Sleep(self.conf_hsbl.get_nested('p3.sleep', default=3000))  #【可调参数】

        # ————————3、前进到P4，调整视角———————————————————————————————————————————————————————————————————
        self.UserPause()  # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        KeyOp.HoldTwoKey(OPKeyCode.W,
                         self.conf_hsbl.get_nested('p4.run', default=[1400,1000])[0],
                         OPKeyCode.Shift,
                         self.conf_hsbl.get_nested('p4.run', default=[1400,1000])[1])  # 在平台上移动  #【可调参数】
        # MouseOp.MoveR(-round(106 * mouse_ratio), round(85 * mouse_ratio))  # 视角往左下角移动
        MouseOp.MoveR(
            round(self.conf_hsbl.get_nested('p4.move', default=[-110,-25])[0] * mouse_ratio),
            round(self.conf_hsbl.get_nested('p4.move', default=[-110,-25])[1] * mouse_ratio))  # 视角往左上角移动：变更钩锁点  #【可调参数】
        OP.Sleep(300)
        # ————————4、钩锁P5飞袭到P6————————————————————————————————————————————————————————————————————————
        # 到达P4，视角已调整，按Q+鼠标左键。
        self.UserPause()    # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        KeyOp.PressKey(OPKeyCode.Q)
        OP.Sleep(200)
        MouseOp.LeftClickNow()
        OP.Sleep(self.conf_hsbl.get_nested('p5p6.sleep1', default=1600))  # 休眠1秒，在接左键飞袭  #【可调参数】
        MouseOp.LeftClickNow()
        OP.Sleep(self.conf_hsbl.get_nested('p5p6.sleep2', default=2700))  # 休眠，等待钩锁攻击结束，然后才能奔跑  #【可调参数】
        # KeyOp.PressKey(OPKeyCode.C) #有可能挂在钩锁点，所以需要C下坠。：后来发现，如果挂上去了，就算下坠下来，方向也变了。所以没必要。
        # OP.Sleep(1500)
        # ————————5、前进到P7，调整视角，火炮攻击2次———————————————————————————————————————————————————
        self.UserPause()    # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        KeyOp.HoldTwoKey(OPKeyCode.W,
                         self.conf_hsbl.get_nested('p7.run', default=[3650,1000])[0],
                         OPKeyCode.Shift,
                         self.conf_hsbl.get_nested('p7.run', default=[3650,1000])[1])  # 奔跑到P7，由于空中平台上，故需要多跑一段时间  #【可调参数】
        KeyOp.PressKey(OPKeyCode.Num2)  # 数字键2切换火炮
        OP.Sleep(300)
        KeyOp.PressKey(OPKeyCode.Num2)  # 数字键2切换火炮-多切换一次，防止切换失败。
        OP.Sleep(800)
        # MouseOp.MoveR(-round(415 * mouse_ratio), round(90 * mouse_ratio))  # 视角往左下移动，瞄准野怪
        MouseOp.MoveR(
            round(self.conf_hsbl.get_nested('p7.move1', default=[-415,207])[0] * mouse_ratio),
            round(self.conf_hsbl.get_nested('p7.move1', default=[-415,207])[1] * mouse_ratio))  # 视角往左下移动，瞄准野怪：由于钩锁点变化，故此处也变化  #【可调参数】
        OP.Sleep(500)
        # for fireCnt in range(1, 3, 1):  # 火炮攻击2次。其实无需火炮，F技能火球就能击杀小怪。但是稳妥起见，火炮攻击。
        #     MouseOp.LeftClickNow()
        #     OP.Sleep(random.randint(1500, 1800))
        KeyOp.PressKey(OPKeyCode.F)  # 使用F技能：火球
        OP.Sleep(300)
        KeyOp.PressKey(OPKeyCode.F)  # 使用F技能：火球。防止F失败，多F一次
        OP.Sleep(1200)
        # MouseOp.MoveR(-160, 0)  # 视角往左移动
        MouseOp.MoveR(
            round(self.conf_hsbl.get_nested('p7.move2', default=[-150,0])[0] * mouse_ratio),
            round(self.conf_hsbl.get_nested('p7.move2', default=[-150,0])[1] * mouse_ratio))  # 视角往左移动  #【可调参数】
        OP.Sleep(800)
        # ————————6、前进到P8，调整视角，前进到P9————————————————————————————————————————————————————————
        self.UserPause()  # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        KeyOp.HoldTwoKey(OPKeyCode.W,
                         self.conf_hsbl.get_nested('p8.run1', default=[2200,1000])[0],
                         OPKeyCode.Shift,
                         self.conf_hsbl.get_nested('p8.run1', default=[2200,1000])[1])  # 奔跑到达拐点P8  #【可调参数】
        # OP.Sleep(2600)  # 这里到达P8是个下坡，可能会有滑落动作，等2秒
        OP.Sleep(600)  # P8现在是挂壁状态
        MouseOp.MoveR(
            round(self.conf_hsbl.get_nested('p8.move1', default=[-193,-55])[0] * mouse_ratio),
            round(self.conf_hsbl.get_nested('p8.move1', default=[-193,-55])[1] * mouse_ratio))  # 视角往左上移动  #【可调参数】
        OP.Sleep(500)
        # 到达P8后，如果继续往前，可能会出现卡脚的情况，必须先往左转走两步，再复原视角，解决卡脚问题。
        KeyOp.PressKey(OPKeyCode.C)  # 挂壁，要先落下，才能行走
        OP.Sleep(800)
        MouseOp.MoveR(self.conf_hsbl.get_nested('p8.move2', default=[-580,0])[0],
                      self.conf_hsbl.get_nested('p8.move2', default=[-580,0])[1])  # 视角往左移动  #【可调参数】
        KeyOp.HoldKey(OPKeyCode.W, self.conf_hsbl.get_nested('p8.walk', default=660)) # 走一下  #【可调参数】
        OP.Sleep(300)
        MouseOp.MoveR(self.conf_hsbl.get_nested('p8.move3', default=[580, 0])[0],
                      self.conf_hsbl.get_nested('p8.move3', default=[580, 0])[1])  # 视角往右移动  #【可调参数】
        OP.Sleep(300)
        KeyOp.HoldTwoKey(OPKeyCode.W,
                         self.conf_hsbl.get_nested('p8.run2', default=[400,1000])[0],
                         OPKeyCode.Shift,
                         self.conf_hsbl.get_nested('p8.run2', default=[400,1000])[1])  # 到达P9  #【可调参数】
        OP.Sleep(800)
        # ————————7、在P9，调整视角，火炮远程攻击————————————————————————————————————————————————————————
        self.UserPause()    # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        MouseOp.MoveR(
            round(self.conf_hsbl.get_nested('p9.move1', default=[260,-20])[0] * mouse_ratio),
            round(self.conf_hsbl.get_nested('p9.move1', default=[260,-20])[1] * mouse_ratio))  # 视角往右上移动  #【可调参数】
        OP.Sleep(1500)
        for fireCnt in range(1, 4, 1):  # 火炮攻击3次(可能有天赐武备匣效果)
            MouseOp.LeftClickNow()
            OP.Sleep(random.randint(1900, 2000))
        OP.Sleep(1000)
        # ————————7、继续待在P9原地不动，调整视角，火炮远程攻击———————————————————————————————————————————————————————
        self.UserPause()  # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        MouseOp.MoveR(
            round(self.conf_hsbl.get_nested('p9.move2', default=[-106,60])[0] * mouse_ratio),
            round(self.conf_hsbl.get_nested('p9.move2', default=[-106,60])[1] * mouse_ratio))  # 视角左下移动  #【可调参数】
        OP.Sleep(800)
        # KeyOp.PressKey(OPKeyCode.R)  # 维修火炮
        # OP.Sleep(600)
        # KeyOp.PressKey(OPKeyCode.R)  # 维修火炮-因为可能一次维修不成功
        # OP.Sleep(2000)
        for fireCnt in range(1, 8, 1):  # 火炮攻击7次(可能有天赐武备匣效果)
            MouseOp.LeftClickNow()
            OP.Sleep(random.randint(1900, 2000))
        if self.pcName == "MyServer":
            OP.Sleep(1000)
        KeyOp.PressKey(OPKeyCode.R)  # 维修火炮
        OP.Sleep(600)
        KeyOp.PressKey(OPKeyCode.R)  # 维修火炮-因为可能一次维修不成功
        OP.Sleep(2500)
        for fireCnt in range(1, 8, 1):  # 火炮攻击8次，实际效果是7次(可能有天赐武备匣效果)    # 20250629：从11次改为7次
            MouseOp.LeftClickNow()
            OP.Sleep(random.randint(1900, 2000))
            # G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"fireCnt={fireCnt}")
        # 以下内容在20250629注释，因为一般不需要开这么多炮
        # KeyOp.PressKey(OPKeyCode.R)  # 维修火炮
        # OP.Sleep(600)
        # KeyOp.PressKey(OPKeyCode.R)  # 维修火炮-因为可能一次维修不成功
        # OP.Sleep(2000)
        # for fireCnt in range(1, 3, 1):  # 火炮攻击3次(可能有天赐武备匣效果)
        #     MouseOp.LeftClickNow()
        #     OP.Sleep(random.randint(1750, 1900))
        # ————————9、调整视角，前往P10，开两炮，再调整视角——————————————————————————————————————————————————————————
        self.UserPause()  # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        OP.Sleep(1500)
        MouseOp.MoveR(
            round(self.conf_hsbl.get_nested('p10.move', default=[-78,0])[0] * mouse_ratio),
            round(self.conf_hsbl.get_nested('p10.move', default=[-78,0])[1] * mouse_ratio))  # 视角平行往左移动  #【可调参数】
        OP.Sleep(600)
        KeyOp.HoldTwoKey(OPKeyCode.W,
                         self.conf_hsbl.get_nested('p10.run', default=[1700,1000])[0],
                         OPKeyCode.Shift,
                         self.conf_hsbl.get_nested('p10.run', default=[1700,1000])[1])  # 前进到P10  #【可调参数】
        OP.Sleep(600)
        # ===改进代码：到达P10后，向3个方向攻击（3个方向的角度和为355），提高成功几率（不能保证一定成功）===
        MouseOp.MoveR(
            round(self.conf_hsbl.get_nested('p11.move1', default=[60,-75])[0] * mouse_ratio),
            round(self.conf_hsbl.get_nested('p11.move1', default=[60,-75])[1] * mouse_ratio))  # 视角往右移动10度、往上移动一些  #【可调参数】
        OP.Sleep(1000)
        MouseOp.LeftClickNow()  # 火炮攻击一次
        OP.Sleep(2200)
        MouseOp.MoveR(
            round(self.conf_hsbl.get_nested('p11.move2', default=[298,0])[0] * mouse_ratio),
            round(self.conf_hsbl.get_nested('p11.move2', default=[298,0])[1] * mouse_ratio))  # 视角平行往右移动60度  #【可调参数】
        OP.Sleep(1000 )
        MouseOp.LeftClickNow()  # 火炮攻击一次
        OP.Sleep(2200)

        MouseOp.MoveR(
            round(self.conf_hsbl.get_nested('p11.move3', default=[150,0])[0] * mouse_ratio),
            round(self.conf_hsbl.get_nested('p11.move3', default=[150,0])[1] * mouse_ratio))  # 视角平行往右移动  #【可调参数】
        OP.Sleep(1000)
        MouseOp.LeftClickNow()  # 火炮攻击一次
        OP.Sleep(2200)
        MouseOp.MoveR(
            round(self.conf_hsbl.get_nested('p11.move4', default=[-150, 0])[0] * mouse_ratio),
            round(self.conf_hsbl.get_nested('p11.move4', default=[-150, 0])[1] * mouse_ratio))  # 视角平行往左移动  #【可调参数】
        OP.Sleep(1000)

        # ————————10、前往P12，并E开箱————————————————————————————————————————————————————————————————————
        Tools.RunAndE(
            self.conf_hsbl.get_nested('p12.run', default=[1200,120])[0],
            self.conf_hsbl.get_nested('p12.run', default=[1200,120])[1])    # 一边跑，一边E  #【可调参数】
        OP.Sleep(100)
        KeyOp.PressKey(OPKeyCode.E) # 多E一次
        OP.Sleep(1000)
        # ————————11、ESC退出、点击“返回大厅”、空格确定————————————————————————————————————————————————————————————————————
        self.Return_To_Home()  # 退出本局游戏，返回大厅

    # 仅适配台式机Desktop
    def Battle_In_HSBL_Desktop(self):
        # ——————————————————————————————————————————————————————————————————————————————————————————————
        # 以下所有写死的数据，均是基于：台式机【Desktop】
        # 游戏设置中视角灵敏度：50， 视角灵敏度(射击模式)：20，
        # 鼠标DPI：1600，
        # Windows11系统设置中鼠标速度：10， 控制面板的指针选项的“选择指针移动速度”为第6格的位置，并且勾选“提高指针精确度”
        # ——————————————————————————————————————————————————————————————————————————————————————————————
        # ————————1、前进到P2，调整视角———————————————————————————————————————————————————————————————————
        KeyOp.HoldTwoKey(OPKeyCode.W, 520, OPKeyCode.Shift, 1500)
        MouseOp.MoveR(315, -110)  # 视角往右、往上移动
        OP.Sleep(ParamTime.slp_cmd)
        # ————————2、钩锁到P3————————————————————————————————————————————————————————————————————————————
        # 到达P2，视角已调整，按Q+鼠标左键
        KeyOp.PressKey(OPKeyCode.Q)
        OP.Sleep(ParamTime.slp_cmd)
        MouseOp.LeftClickNow()
        OP.Sleep(3000)
        # ————————3、前进到P4，调整视角———————————————————————————————————————————————————————————————————
        KeyOp.HoldTwoKey(OPKeyCode.W, 1900, OPKeyCode.Shift, 500)  # 在平台上移动
        MouseOp.MoveR(-106, 85)  # 视角往左下角移动
        OP.Sleep(ParamTime.slp_cmd)
        # ————————4、钩锁P5飞袭到P6————————————————————————————————————————————————————————————————————————
        # 到达P4，视角已调整，按Q+鼠标左键
        KeyOp.PressKey(OPKeyCode.Q)
        OP.Sleep(200)
        MouseOp.LeftClickNow()
        OP.Sleep(1600)  # 休眠1秒，在接左键飞袭
        MouseOp.LeftClickNow()
        OP.Sleep(2500)  # 休眠，等待钩锁攻击结束，然后才能奔跑
        # ————————5、前进到P7，调整视角，火炮攻击3次———————————————————————————————————————————————————
        KeyOp.HoldTwoKey(OPKeyCode.W, 3000, OPKeyCode.Shift, 500)  # 奔跑到P7
        KeyOp.PressKey(OPKeyCode.Num2)  # 数字键2切换火炮
        OP.Sleep(800)
        MouseOp.MoveR(-415, 90)  # 视角往左下移动，瞄准野怪
        OP.Sleep(500)
        for fireCnt in range(1, 3, 1):  # 火炮攻击2次。其实无需火炮，F技能火球就能击杀小怪。但是稳妥起见，火炮攻击。
            MouseOp.LeftClickNow()
            OP.Sleep(random.randint(1260, 1360))  # random.randint(1260, 1360)
        KeyOp.PressKey(OPKeyCode.F)  # 使用F技能：火球
        OP.Sleep(1200)
        # MouseOp.MoveR(-160, 0)  # 视角往左移动
        MouseOp.MoveR(-150, 0)  # 视角往左移动
        OP.Sleep(800)
        # ————————6、前进到P8，调整视角，前进到P9————————————————————————————————————————————————————————
        # KeyOp.HoldKey(OPKeyCode.W, 4600) # 慢走到达拐点P8
        KeyOp.HoldTwoKey(OPKeyCode.W, 1730, OPKeyCode.Shift, 500)  # 走到达拐点P8
        OP.Sleep(2000)  # 这里到达P8是个下坡，可能会有滑落动作，等2秒
        # MouseOp.MoveR(-200, -55)   #视角往左上移动
        MouseOp.MoveR(-190, -55)  # 视角往左上移动
        OP.Sleep(800)
        KeyOp.HoldTwoKey(OPKeyCode.W, 1180, OPKeyCode.Shift, 500)  # 到达P9
        OP.Sleep(800)
        # ————————7、在P9，调整视角，火炮远程攻击————————————————————————————————————————————————————————
        # MouseOp.MoveR(266, -20)  # 视角往右上移动
        MouseOp.MoveR(260, -20)  # 视角往右上移动
        OP.Sleep(1500)
        for fireCnt in range(1, 10, 1):  # 火炮攻击10次(可能有天赐武备匣效果)
            MouseOp.LeftClickNow()
            OP.Sleep(random.randint(1260, 1360))
        OP.Sleep(1000)
        # ————————7、继续待在P9原地不动，调整视角，火炮远程攻击———————————————————————————————————————————————————————
        MouseOp.MoveR(-106, 60)  # 视角左下移动
        OP.Sleep(1000)
        KeyOp.PressKey(OPKeyCode.R)  # 维修火炮
        OP.Sleep(2000)
        for fireCnt in range(1, 12, 1):  # 火炮攻击12次(可能有天赐武备匣效果)
            MouseOp.LeftClickNow()
            OP.Sleep(random.randint(1260, 1360))
        KeyOp.PressKey(OPKeyCode.R)  # 维修火炮
        OP.Sleep(2000)
        for fireCnt in range(1, 9, 1):  # 火炮攻击12次(可能有天赐武备匣效果)
            MouseOp.LeftClickNow()
            OP.Sleep(random.randint(1260, 1360))
        # ————————9、调整视角，前往P10，开两炮，再调整视角——————————————————————————————————————————————————————————
        OP.Sleep(1500)
        MouseOp.MoveR(-78, 0)  # 视角平行往左移动
        OP.Sleep(200)
        KeyOp.HoldTwoKey(OPKeyCode.W, 2200, OPKeyCode.Shift, 500)  # 前进到P10
        OP.Sleep(600)
        # ===改进代码：到达P10后，向3个方向攻击（3个方向的角度和为355），提高成功几率（不能保证一定成功）===
        MouseOp.MoveR(60, -75)  # 视角往右移动10度、往上移动一些
        OP.Sleep(600)
        MouseOp.LeftClickNow()  # 火炮攻击
        OP.Sleep(2000)
        MouseOp.MoveR(120, 0)  # 视角平行往右移动20度
        OP.Sleep(600)
        MouseOp.LeftClickNow()  # 火炮攻击
        OP.Sleep(2000)
        MouseOp.MoveR(175, 0)  # 视角平行往右移动60度
        OP.Sleep(600)
        MouseOp.LeftClickNow()  # 火炮攻击
        OP.Sleep(2000)

        # ————————10、前往P12，并E开箱————————————————————————————————————————————————————————————————————
        KeyOp.HoldTwoKey(OPKeyCode.W, 1330, OPKeyCode.Shift, 500)
        OP.Sleep(200)
        KeyOp.PressKey(OPKeyCode.E)
        OP.Sleep(1000)
        # ————————11、ESC退出、点击“返回大厅”、空格确定————————————————————————————————————————————————————————————————————
        self.Return_To_Home()  # 退出本局游戏，返回大厅

    # 鸿溟之难-噩梦。轮椅套。
    def Battle_In_HMZN(self):
        self.battleCnt += 1
        # 第一次进入局内战斗界面时，初始化游戏开始时间
        if self.battleCnt == 1:
            self.gameTimeStart = datetime.now()
        cycCnt = 0  #循环次数
        isBegin = True  # 是否为开局状态？需要前进然后E
        isLocked = False    #是否锁定视角？
        bossName = "万象"      # 当前正在打的BOSS名称，总共两种：万象（魈、兽），本体
        curBossName = "万象"  # 当前OCR识别到的BOSS名称
        lifeLeft = 1    #返魂次数
        # 循环，直到识别到通关成功，或者到达设定时间仍未识别到通关成功，强行退出。
        while True:
            cycCnt += 1     #更新循环次数
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"循环计数：{cycCnt}")
            if not self.UserPause():  # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
                return False  # 用户主动结束，就退出循环
            # ————————计算已用时间，判断是否超时————————————————————————————————————————————————————————————————————
            self.gameTimeUsed = (datetime.now() - self.gameTimeStart).total_seconds()   #计算目前已用时间，单位：秒
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"已用{self.gameTimeUsed}秒")
            if self.gameTimeUsed >= ParamTime.max_InGame_Time_PVE_HMZN:
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info,
                    f"本局游戏已超时仍未通关，强制结束并返回大厅，本局消耗时间：{self.gameTimeUsed}秒。")
                self.Return_To_Home()  # 退出本局游戏，返回大厅
                return False
            # ————————从出生点/复活点前往战斗地点————————————————————————————————————————————————————————————————————
            if isBegin:
                MouseOp.MoveR(60, 0)  # 视角平行往右移动一些
                OP.Sleep(200)
                Tools.RunAndE(1200, 300)  # 一边跑，一边E
                OP.Sleep(4000)
                while True:
                    # 如果OCR识别到“跳过”，就ESC跳过
                    if WinInfo.Text_Char_Game_in_PVE_3 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_in_PVE_3):
                        G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info,
                            f"getCurUI：OCR识别到进入游戏内界面3-过渡动画，特征字：{WinInfo.Text_Char_Game_in_PVE_3}")
                        KeyOp.PressKey(OPKeyCode.ESC)
                        isBegin = False  # 只有成功识别到ESC跳过界面才能置isBegin为False，跳过过渡的可跳过界面
                        break
                OP.Sleep(3000)

                KeyOp.PressKey(OPKeyCode.Tilde)  # 锁定视角：本体
                KeyOp.HoldTwoKey(OPKeyCode.W, 2500, OPKeyCode.Shift, 500)   # 到达BOSS附近
                OP.Sleep(300)
                KeyOp.PressKey(OPKeyCode.Tilde)  # 解除锁定视角：本体
                OP.Sleep(300)
                MouseOp.LeftClickNow()  # 攻击一次
                OP.Sleep(4500)
                KeyOp.PressKey(OPKeyCode.Tilde)  # 锁定视角：万象-魈
                isLocked = True
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"首次锁定视角成功：万象-魈")
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"锁定视角成功，战斗开始。")

            # ————————获取BOSS名称、锁定视角、判断是否通关————————————————————————————————————————————————————————————————————
            if cycCnt % 2 == 0:
                timeBegin1 = datetime.now()
                tmpBossName = self.getCurBossName(WinInfo.Area_Char_Game_In_PVE_HMZN_2_BossName)
                usedTime1 = (datetime.now() - timeBegin1).total_seconds()
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"ocrAreaTextQuick用时：{usedTime1}，识别结果：{tmpBossName}")
                if tmpBossName != "NoResult": # 获取到有效结果
                    if "本体" in tmpBossName:
                        curBossName = "本体"
                    elif "万象" in tmpBossName:
                        curBossName = "万象"
                    else:
                        # 有效结果中没有BOSS名称，判断是否通关成功
                        if WinInfo.Text_Char_Game_in_PVE_5 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_in_PVE_5):
                            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info,
                                f"战斗结束，OCR识别到特征字：{WinInfo.Text_Char_Game_in_PVE_5}，本局消耗时间：{self.gameTimeUsed}秒。")
                            self.Return_To_Home()  # 退出本局游戏，返回大厅
                            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"通关成功。")
                            return True
                        else:
                            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"当前未通关成功，继续战斗。")
            if curBossName != bossName:   # 进入BOSS下一阶段
                MouseOp.MoveR(0, -250)  # 抬高一些视角，否则后面无法锁定
                isLocked = False
                bossName= curBossName
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"【BOSS切换】上一轮BOSS：{bossName}，当前BOSS：{curBossName}")
            else:
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"BOSS未切换，当前BOSS：{bossName}")

            if not isLocked:
                if bossName == "本体":
                    KeyOp.HoldTwoKey(OPKeyCode.S, 4000, OPKeyCode.Shift, 800)  # 退后在锁定视角
                elif bossName == "万象":
                    KeyOp.HoldTwoKey(OPKeyCode.S, 4000, OPKeyCode.Shift, 800)  # 退后在锁定视角
                OP.Sleep(500)
                KeyOp.PressKey(OPKeyCode.Tilde)  # 锁定视角
                isLocked = True
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"BOSS更新，锁定视角成功。")
            # ————————每次循环：左键攻击————————————————————————————————————————————————————————————————————
            self.ThreeAttackLeft()
            if cycCnt % 2 == 0:
                # ————————点击F键使用技能————————————————————————————————————————————————————————————————————
                OP.Sleep(random.randint(200, 250))
                KeyOp.PressKey(OPKeyCode.F)
            else:
                # ————————点击V键使用技能————————————————————————————————————————————————————————————————————
                OP.Sleep(random.randint(200, 250))
                KeyOp.PressKey(OPKeyCode.V)

    def getCurBossName(self, area: list[4])->str:
        name1 = GetScrInfo.ocrAreaTextQuick1(WinInfo.Area_Char_Game_In_PVE_HMZN_2_BossName)
        name2 = GetScrInfo.ocrAreaTextQuick2(WinInfo.Area_Char_Game_In_PVE_HMZN_2_BossName)
        if name1 == name2:
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getCurBossName连续两次相同：{name1}")
            return name1    # 正常来说，有三种结果：万象，本体，空字符串
        else:
            G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.warning, f"getCurBossName连续两次不同：{name1}、{name2}")
            return "NoResult"

    # 左键三连击
    @staticmethod
    def ThreeAttackLeft():
        MouseOp.LeftClickNow()
        OP.Sleep(random.randint(100, 120))
        MouseOp.LeftClickNow()
        OP.Sleep(random.randint(100, 120))
        MouseOp.LeftClickNow()
        OP.Sleep(random.randint(100, 120))

    # 万象降临-噩梦。轮椅套。万象降临只需要开头锁定一次视角即可，后续不需要锁定视角
    def Battle_In_WXJL(self):
        self.Battle_Common(GAME_MODE_PVE_WXJL)

    # 通用战斗方式，适用于只需锁定一次视角
    def Battle_Common(self, GameMode:str) -> bool:
        #————————————————————————————————————————————————————
        # 不同模式有不同的BOSS
        curBossName = ""
        if GameMode == GAME_MODE_PVE_XMGD:
            curBossName = "昆仑主母"
        elif GameMode == GAME_MODE_PVE_WXJL:
            curBossName = "万象"
        # 不同模式，识别BOSS的区域有所区别
        curBossArea = []
        if GameMode == GAME_MODE_PVE_XMGD:
            curBossArea = WinInfo.Area_Char_Game_in_PVE_4
        elif GameMode == GAME_MODE_PVE_WXJL:
            curBossArea = WinInfo.Area_Char_Game_In_PVE_WXJL_2_BossName
        # 不同模式，从出生点到达传送点的奔跑时间不同
        runTime = 5000
        if GameMode == GAME_MODE_PVE_XMGD:
            runTime = 4500
        elif GameMode == GAME_MODE_PVE_WXJL:
            runTime = 3600
        # 不同模式，默认最大战斗时间不同
        maxTime = 600
        if GameMode == GAME_MODE_PVE_XMGD:
            maxTime = ParamTime.max_InGame_Time_PVE_XMGD
        elif GameMode == GAME_MODE_PVE_WXJL:
            maxTime = ParamTime.max_InGame_Time_PVE_WXJL
        # ————————————————————————————————————————————————————

        self.battleCnt += 1
        # 第一次进入局内战斗界面时，初始化游戏开始时间
        if self.battleCnt == 1:
            self.gameTimeStart = datetime.now()
        cycCnt = 0  # 循环次数
        isBegin = True  # 是否为开局状态？需要前进然后E
        bossName = curBossName  # 当前正在打的BOSS名称，一般都是“万象·XXX”，例如万象狱炎、魈、兽、苍帝等等
        # 循环，直到识别到通关成功，或者到达设定时间仍未识别到通关成功，强行退出。
        while True:
            try:
                cycCnt += 1  # 更新循环次数
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"循环计数：{cycCnt}")
                if not self.UserPause():  # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
                    return False    # 用户主动结束，就退出循环
                # ————————计算已用时间，判断是否超时————————————————————————————————————————————————————————————————————
                self.gameTimeUsed = (datetime.now() - self.gameTimeStart).total_seconds()  # 计算目前已用时间，单位：秒
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"已用{self.gameTimeUsed}秒")
                if self.gameTimeUsed >= maxTime:  # 超出最大时间，强行返回大厅
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info,
                        f"本局游戏已超时仍未通关，强制结束并返回大厅，本局消耗时间：{self.gameTimeUsed}秒。")
                    self.Return_To_Home()  # 退出本局游戏，返回大厅
                    return False
                # ————————从出生点/复活点前往战斗地点————————————————————————————————————————————————————————————————————
                if isBegin:
                    MouseOp.MoveR(0, 0)  # 视角平行往右移动一些
                    OP.Sleep(200)
                    Tools.RunAndE(runTime, 330)  # 一边跑，一边E
                    OP.Sleep(5000)
                    while True:
                        G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"尝试ESC")
                        # 如果OCR识别到“跳过”，就ESC跳过
                        if WinInfo.Text_Char_Game_in_PVE_3 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_in_PVE_3):
                            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info,
                                f"getCurUI：OCR识别到进入游戏内界面3-过渡动画，特征字：{WinInfo.Text_Char_Game_in_PVE_3}")
                            KeyOp.PressKey(OPKeyCode.ESC)
                            isBegin = False  # 只有成功识别到ESC跳过界面才能置isBegin为False，跳过过渡的可跳过界面
                            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"ESC成功")
                            break
                    OP.Sleep(2500)
                    # 等待BOSS出现，然后进行视角锁定
                    while True:
                        G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"尝试锁定视角")
                        tmpBossName = self.getCurBossName(curBossArea)
                        if curBossName in tmpBossName:
                            KeyOp.PressKey(OPKeyCode.Tilde)  # 锁定视角
                            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"锁定视角成功，战斗开始。")
                            break

                # ————————判断是否通关————————————————————————————————————————————————————————————————————
                # if cycCnt % 2 == 0:
                timeBegin1 = datetime.now()
                tmpBossName = self.getCurBossName(curBossArea)
                usedTime1 = (datetime.now() - timeBegin1).total_seconds()
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"ocrAreaTextQuick用时：{usedTime1}，识别结果：{tmpBossName}")
                if tmpBossName != "NoResult":  # 获取到有效结果
                    if curBossName in tmpBossName:
                        G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"当前BOSS：{curBossName}")
                    else:
                        # 有效结果中没有BOSS名称，判断是否通关成功
                        if WinInfo.Text_Char_Game_in_PVE_5 in GetScrInfo.ocrAreaText(
                                WinInfo.Area_Char_Game_in_PVE_5):
                            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info,
                                f"战斗结束，OCR识别到特征字：{WinInfo.Text_Char_Game_in_PVE_5}，本局消耗时间：{self.gameTimeUsed}秒。")
                            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"通关成功。")
                            self.Return_To_Home()  # 退出本局游戏，返回大厅
                            return True
                        else:
                            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"当前未通关成功，继续战斗。")

                # ————————每次循环：左键三连击————————————————————————————————————————————————————————————————————
                self.ThreeAttackLeft()
                if cycCnt % 2 == 0:
                    # ————————点击F键使用技能————————————————————————————————————————————————————————————————————
                    OP.Sleep(random.randint(100, 120))
                    KeyOp.PressKey(OPKeyCode.F)
                    KeyOp.PressKey(OPKeyCode.F)
                elif cycCnt % 2 == 1:
                    # ————————点击V键使用技能————————————————————————————————————————————————————————————————————
                    OP.Sleep(random.randint(100, 120))
                    KeyOp.PressKey(OPKeyCode.V)
                    KeyOp.PressKey(OPKeyCode.V)
            except Exception as e:
                G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error, f"异常类型: {type(e).__name__}")
                G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error, f"异常信息: {str(e)}")
                G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error, f"异常参数: {e.args}")

                # 获取详细的错误追踪
                G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error, "\n详细错误追踪:")
                traceback.print_exc()

                # 获取异常的详细信息
                exc_type, exc_value, exc_traceback = sys.exc_info()
                G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error, f"\n系统异常信息:")
                G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error, f"异常类型: {exc_type}")
                G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error, f"异常值: {exc_value}")

                # 格式化异常追踪信息
                tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error, "格式化的异常追踪:")
                for line in tb_lines:
                    G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error, line.strip())

    def Return_To_Home(self):
        #————————ESC退出、点击“返回大厅”、空格确定————————————————————————————————————————————————————————————————————
        self.UserPause()  # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        KeyOp.PressKey(OPKeyCode.ESC)
        OP.Sleep(1500)
        self.UserPause()  # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        if WinInfo.Text_PVE_Return_Home_From_Game in GetScrInfo.ocrAreaText(WinInfo.Area_PVE_Return_Home_From_Game):
            # 如果识别到“返回大厅”，点击“返回大厅”
            MouseOp.LeftClickAreaRandom(WinInfo.Area_PVE_Return_Home_From_Game, self.ratio)
            OP.Sleep(1500)
        self.UserPause()  # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        if WinInfo.Text_PVE_Return_Home_From_Game_Sure in GetScrInfo.ocrAreaText(
                WinInfo.Area_PVE_Return_Home_From_Game_Sure):
            # 如果识别到“确定”，点击“确定”
            MouseOp.LeftClickAreaRandom(WinInfo.Area_PVE_Return_Home_From_Game_Sure, self.ratio)
            OP.Sleep(1500)
        KeyOp.PressKey(OPKeyCode.Space)  # 保险起见，再来空格确定一次
        OP.Sleep(1000)


    def Handle_PVE_Game_In_4_Battle(self):
        self.Battle_Common(GAME_MODE_PVE_XMGD)


    # def Handle_PVE_Game_In_4_Battle(self):
    #     # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
    #     self.UserPause()
    #
    #     self.battleCnt += 1
    #     # 第一次进入局内战斗界面时，初始化游戏开始时间
    #     if self.battleCnt == 1:
    #         self.gameTimeStart = datetime.now()
    #         KeyOp.PressKey(OPKeyCode.Tilde)  # 锁定视角
    #     # 计算目前已用时间
    #     self.gameTimeUsed = (datetime.now() - self.gameTimeStart).total_seconds()
    #
    #     # 固定操作：右键蓄力+右键(左蓄+右键容易变成振刀。)
    #     holdTime = random.randint(ParamTime.holdTimeMin, ParamTime.holdTimeMax)
    #     MouseOp.RightHoldPoint(self.clientAreaMidPoint, holdTime, self.ratio)
    #     delayTime = random.randint(650, 800)
    #     OP.Sleep(delayTime)  # 这个时间可以调整：蓄力完成后到点击右键的延时
    #     MouseOp.RightClickPoint(self.clientAreaMidPoint, self.ratio)
    #     # 每隔pcsOfF个周期放一次F
    #     if self.pcsCnt % ParamCnt.pcsOfF == 0:
    #         OP.Sleep(600)  # 这个时间可以调整：右键攻击到F的延时
    #         if KeyOp.PressKey(OPKeyCode.F):
    #             G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"尝试释放F技能")
    #     # 每隔pcsOfV个周期放一次V
    #     if self.pcsCnt % ParamCnt.pcsOfV == 0:
    #         OP.Sleep(500)  # 这个时间可以调整：F到V的延时
    #         if KeyOp.PressKey(OPKeyCode.V):
    #             G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"尝试释放V技能")

    # def Handle_PVE_Game_In_5_Succeed(self):
    #     # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
    #     self.UserPause()
    #     # 按ESC，然点击固定区域，然后再点击空格
    #     KeyOp.PressKey(OPKeyCode.ESC)
    #     OP.Sleep(1000)
    #     # 如果OCR识别到“返回大厅”
    #     if WinInfo.Text_PVE_Return_Home_From_Game in GetScrInfo.ocrAreaText(WinInfo.Area_PVE_Return_Home_From_Game):
    #         G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"成功输入ESC，识别到“{WinInfo.Text_PVE_Return_Home_From_Game}”")
    #         # 点击“返回大厅”这个区域
    #         MouseOp.LeftClickAreaRandom(WinInfo.Area_PVE_Return_Home_From_Game, self.ratio)
    #         G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"成功点击“{WinInfo.Text_PVE_Return_Home_From_Game}”")
    #         OP.Sleep(1500)
    #         KeyOp.PressKey(OPKeyCode.Space)  # 空格确定

    def Handle_PVE_Main_Prepare(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        self.battleCnt = 0
        self.gameCnt += 1
        G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"当前游戏局数：{self.gameCnt}")

        curFatigue = self.getCurFatigue()
        usedFatigue = curFatigue - self.fatigue
        if ParamCnt.FatigueMin <= usedFatigue <= ParamCnt.FatigueMax:   # 一局游戏消耗的疲劳值应当在合理范围内，否则不做记录
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"当前疲劳值：{curFatigue}，上一局游戏消耗疲劳：{curFatigue - self.fatigue}")
            if usedFatigue == 0:
                G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error,f"上局游戏未能消耗疲劳值！")
        else:
            if self.gameCnt > 1: #只在第二局游戏时开始判断
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"当前疲劳值：{curFatigue}（上局消耗疲劳值非法）")
        self.fatigue = curFatigue

        # 如果达到限定的疲劳值，则退出脚本
        if 0 < MAX_FATIGUE <= self.fatigue:
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"当前疲劳值{self.fatigue}，已经达到设定的疲劳值{MAX_FATIGUE}，脚本退出。")
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"当前疲劳值{self.fatigue}，已经达到设定的疲劳值{MAX_FATIGUE}，脚本退出。")
            exit(2)

        # 如果游戏局数每达到x盘，就休眠120秒
        if self.gameCnt % 100 == 0:
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"游戏局数达到100盘，休眠120秒")
            OP.Sleep(120000)
        MouseOp.LeftClickAreaRandom(WinInfo.Area_Char_PVE_Main, self.ratio)
        OP.Sleep(12000)  # 点击“开始征神”后，休眠数秒。防止一直点击。

    # 获取疲劳值
    def getCurFatigue(self)->int:
        fatigueStr = GetScrInfo.ocrAreaText(WinInfo.Area_PVE_Fatigue_All)   #当前疲劳值，格式：203/2400
        fatigueStr_int = 0  #默认0
        # 判断字符串中是否包含 "/"
        if '/' in fatigueStr:
            # 使用正则表达式提取 "/" 前面的数字
            match = re.match(r"(\d+)/", fatigueStr)
            if match:
                fatigueStr_int = match.group(1)
        # fatigueStr_int = re.findall(r"\d+", fatigueStr)[0]
        try:
            curFatigue = int(fatigueStr_int)
        except ValueError:
            print(f"Error: '{fatigueStr_int}' is not a valid integer.")
            curFatigue = 0
        return curFatigue

    def Handle_PVE_Main_Sure(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        # 先勾选“今日不再提示”
        MouseOp.LeftClickPoint(WinInfo.Point_PVE_Main_Not_Notify, self.ratio)
        OP.Sleep(1000)
        # 然后点击确定
        MouseOp.LeftClickAreaRandom(WinInfo.Area_PVE_Main_Sure, self.ratio)

    def Handle_PVE_Main_Tire_Sure(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒Handle_PVE_Main_Tire_Sure
        self.UserPause()
        # 先勾选“今日不再提示”
        MouseOp.LeftClickPoint(WinInfo.Point_PVE_Main_Tire_Not_Notify, self.ratio)
        OP.Sleep(1000)
        # 然后点击确定
        MouseOp.LeftClickAreaRandom(WinInfo.Area_PVE_Main_Tire_Sure, self.ratio)

    def Handle_PVE_Select_Hero(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        if (self.gameMode == GAME_MODE_PVE_XMGD
                or self.gameMode == GAME_MODE_PVE_HMZN
                or self.gameMode == GAME_MODE_PVE_WXJL):
            MouseOp.LeftClickAreaRandom(WinInfo.Area_PVE_Hero_NingHy, self.ratio)  # PVE-雪满弓刀只推荐宁红夜，F技能自动索敌
        elif self.gameMode == GAME_MODE_PVE_HSBL:
            MouseOp.LeftClickAreaRandom(WinInfo.Area_PVE_Hero_JiCH, self.ratio)  # PVE-黄沙百炼推荐季沧海/岳山，使用火炮
        OP.Sleep(1000)  # 休眠1秒，再点“确定”
        MouseOp.LeftClickAreaRandom(WinInfo.Area_PVE_Select_Cur_Hero, self.ratio)
        OP.Sleep(ParamTime.slp_After_Select_Hero)

    def Handle_PVE_Game_End_1(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        KeyOp.PressKey(OPKeyCode.Space)

    def Handle_PVE_Game_End_2(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        # EXPStr = GetScrInfo.ocrAreaText(WinInfo.Area_XMGD_EXE_Area_1)
        # EXPstr_int = re.findall(r"\d+", EXPStr)[0]
        # try:
        #     curEXP = int(EXPstr_int)
        # except ValueError:
        #     G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"Error: '{EXPstr_int}' is not a valid integer.")
        #     curEXP = ParamCnt.EXE_DEFAULT_WJSL
        # self.EXP += curEXP
        KeyOp.PressKey(OPKeyCode.Space)

    def Handle_PVE_Game_End_3(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        KeyOp.PressKey(OPKeyCode.Space)

    def Handle_PVE_Game_End_4(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        KeyOp.PressKey(OPKeyCode.Space)

    def Handle_PVE_Game_End_5(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        KeyOp.PressKey(OPKeyCode.ESC)

    def Handle_PVE_Game_End_6(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        KeyOp.PressKey(OPKeyCode.Space)

    # ==========通用===================================
    # 登录界面1，
    @staticmethod
    def Handle_LogIn_Announcement():
        KeyOp.PressKey(OPKeyCode.Space)  # 按下空格
        # 等待一段时间
        OP.Sleep(ParamTime.gameStart1ToStart2)

    # 登录界面2，
    def Handle_LogIn_AgeRatingReminder(self):
        MouseOp.LeftClickPoint(WinInfo.Point_Safe_Click, self.ratio)  # 点击屏幕内的安全点
        OP.Sleep(ParamTime.gameStart2ToMainUI)  # 等待一段时间

    # 主界面，但是弹窗每日消息，需要点击“今日不再提示”，然后ESC关闭弹窗
    def Handle_Daily_Msg(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "【进入主界面：发现每日消息弹窗】")
        if MouseOp.LeftClickPoint(WinInfo.Point_Daily_Msg_Skip, self.ratio):
            if KeyOp.PressKey(OPKeyCode.ESC):
                G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "已跳过每日消息弹窗。")

    # 如果在游戏局外，按下了ESC，会弹出这个界面。直接点击返回游戏即可。
    def Handle_ESC_Selection(self):
        # 移动到“返回游戏”，然后点击
        MouseOp.LeftClickPoint(WinInfo.Point_ESC_Select_OutGame_ReturnGame, self.ratio)
        G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.warning,"误触ESC的界面：尝试跳出错误界面，点击一次“返回游戏”")

    # 过渡界面
    @staticmethod
    def Handle_Transition():
        OP.Sleep(ParamTime.slp_Transition)

    # # 非以上任何一个界面，可以空格跳过的界面
    # @staticmethod
    # def Handle_Skip_Space():
    #     if KeyOp.PressKey(OPKeyCode.Space):
    #         G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.warning,"可以空格跳过的界面：尝试跳出错误界面，输入一次“空格”")
    #
    # # 非以上任何一个界面，可以ESC跳过的界面
    # @staticmethod
    # def Handle_Skip_ESC():
    #     if KeyOp.PressKey(OPKeyCode.ESC):
    #         G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.warning,"可以ESC跳过的界面：尝试跳出错误界面，输入一次“ESC”")
    #

    def Handle_Err_Main_PVEWarehouseFull(self):
        G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.critical,
            f"临时仓库中存在未领取的征神魂玉，征神仓库已满。需要手动清理仓库，脚本已退出。\n")
        exit(-2)

    # 过渡界面达到一定次数，则认为进入错误界面。错误界面的处理逻辑如下：
    def Handle_Err_UI(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()

        # 调用本函数的次数 = 故障后异常次数 = 连续异常次数 - 异常报故障次数
        ErrUI_ContCnt = PscRltAll[FAULT_TRANSITION_UI].contExCnt - PscCfgAll[FAULT_TRANSITION_UI].contExCnt
        if ErrUI_ContCnt >= ParamCnt.ExitErrUICnt_Max:
            G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.critical,
                f"\n连续调用错误界面处理函数Handle_Err_UI{ErrUI_ContCnt}次，仍然无法回到正常界面。脚本已结束运行！\n")
            exit(-1)

        self.errUICnt += 1

        # 移动鼠标到安全位置，点一下。
        # MouseOp.LeftClickPoint(WinInfo.Point_Safe_Click, self.ratio)
        # G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.warning,f"尝试跳出错误界面：鼠标点击客户端{WinInfo.Point_Safe_Click}位置一次")
        G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error,
            f"连续{PscRltAll[FAULT_TRANSITION_UI].contExCnt}次识别到过渡界面，判定当前界面为错误界面，尝试跳出……")

        # 先判断是否在主界面错误点击了ESC
        if WinInfo.Text_Char_ESC_Select_OutGame in GetScrInfo.ocrAreaText(WinInfo.Area_Char_ESC_Select_OutGame):
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info,
                f"Handle_Err_UI：OCR识别到进入主界面的ESC弹窗，点击“{WinInfo.Text_ESC_Select_OutGame_ReturnGame}”")
            if MouseOp.LeftClickPoint(WinInfo.Point_ESC_Select_OutGame_ReturnGame, self.ratio):
                curUI = self.getCurUI()
                if curUI == GameInfo.UI_PVE_Main_Prepare or curUI == GameInfo.UI_PVP_Main_Prepare:
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "返回主界面成功。")
                    return
                else:
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "未能成功返回主界面。")

        # 然后判断是否在游戏内错误点击了ESC
        if WinInfo.Text_Char_ESC_Select_InGame in GetScrInfo.ocrAreaText(WinInfo.Area_Char_ESC_Select_InGame):
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"Handle_Err_UI：OCR识别到进入游戏外ESC界面，点击“{WinInfo.Text_ESC_Select_InGame_ReturnGame}”")
            if MouseOp.LeftClickPoint(WinInfo.Point_ESC_Select_InGame_ReturnGame, self.ratio):
                curUI = self.getCurUI()
                if (GameInfo.UI_PVE_Game_In_1_W <= curUI <= GameInfo.UI_PVE_Game_In_5_Succeed) \
                        or (curUI == GameInfo.UI_PVP_Game_In_WJSL):
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "返回游戏局内成功。")
                    return
                else:
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "未能成功返回返回游戏局内。")

        # 其他错误界面，尝试轮流输入ESC或空格来跳过
        OP.Sleep(ParamTime.slp_cmd)
        if self.errUICnt % 2 == 0:
            if KeyOp.PressKey(OPKeyCode.Space):
                G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.warning,"尝试跳出错误界面：输入一次“空格”")
        else:
            if KeyOp.PressKey(OPKeyCode.ESC):
                G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.warning,"尝试跳出错误界面：输入一次“ESC”")

    # ————————————————————————————————————————————————————————————————————
    # 更新窗口状态信息：#窗口是否存在、窗口是否正常响应、窗口是否激活、窗口尺寸是否正确
    # 只要所有检测项有一个异常，就返回False
    def updateWindowState(self) -> bool:
        winStateRlt = True
        # op插件的GetWindowState函数获取窗口是否处于存在
        if OP.GetWindowState(self.hwnd, 0) == 1:
            self.windowStates[WIN_STATE_EXIST] = True  # 窗口还存在
        else:
            self.windowStates[WIN_STATE_EXIST] = False  # 窗口不存在了
            winStateRlt = False

        # op插件的GetWindowState函数获取窗口是否可以响应
        if OP.GetWindowState(self.hwnd, 6) == 1:
            self.windowStates[WIN_STATE_RESPONSE] = True  # 窗口可以正常响应
        else:
            # 【】【】【这个状态有问题】无论怎么获取，只要在后台，那就无响应。
            self.windowStates[WIN_STATE_RESPONSE] = True  # 窗口无响应
            # winStateRlt = False

        # op插件的GetWindowState函数获取窗口是否处于激活状态
        if OP.GetWindowState(self.hwnd, 1) == 1:
            self.windowStates[WIN_STATE_ACTIVE] = True  # 激活
        else:
            self.windowStates[WIN_STATE_ACTIVE] = False  # 未激活
            winStateRlt = False

        curWindowArea = OP.GetWindowRect(self.hwnd)[1:]  # 窗口区域坐标
        curClientArea = OP.GetClientRect(self.hwnd)[1:]  # 客户端区域坐标
        # 如果Client区域坐标发生任何变化，都重新设置窗口大小、位置
        if (curWindowArea[0] != self.windowArea[0] or curWindowArea[1] != self.windowArea[1]
                or curWindowArea[2] != self.windowArea[2] or curWindowArea[3] != self.windowArea[3]
                or curClientArea[0] != self.clientArea[0] or curClientArea[1] != self.clientArea[1]
                or curClientArea[2] != self.clientArea[2] or curClientArea[3] != self.clientArea[3]):
            self.windowStates[WIN_STATE_AREA_OK] = False  # Client窗口坐标位置错误
            winStateRlt = False
        else:
            self.windowStates[WIN_STATE_AREA_OK] = True  # Client窗口坐标位置正常

        return winStateRlt

    # ————————————————————————————————————————————————————————————————————
    # 恢复窗口状态
    def recoverWindowState(self):
        # 【1-发现问题】窗口是否存在？不存在则重新启动程序
        if not self.windowStates[WIN_STATE_EXIST]:
            # 【1-解决办法】启动游戏
            # self.startGame()
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "启动游戏。【功能未实现】")

        # 【2-发现问题】窗口是否正常响应？无响应则重新启动程序
        # 【】【】有问题。目前这个状态会一直报故障。先不管。
        if not self.windowStates[WIN_STATE_RESPONSE]:
            # 【2-解决办法】重启游戏
            # self.closeGame()
            # self.startGame()
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "关闭游戏。【功能未实现】")
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, "启动游戏。【功能未实现】")

        # 【3-发现问题】窗口是否处于激活状态（在前台显示）？未激活则激活窗口
        if self.pcsCnt % ParamCnt.cntCycActive == 0:  # 每5个周期激活一次窗口。不能每个周期都检查，不然就没法关闭游戏了。
            if not self.windowStates[WIN_STATE_ACTIVE]:  # 如果当前不是激活状态
                if OP.SetWindowState(self.hwnd, 12) == 1:  # 激活窗口，显示到前台
                    OP.SetWindowState(self.hwnd, 7)
                    G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"检测到窗口未激活，尝试激活窗口成功。")
                else:
                    G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error,f"检测到窗口未激活，尝试激活窗口失败！")

        # 【4-发现问题】窗口区域/尺寸是否发生变化？如果和设置的预期尺寸及位置不同，会导致脚本无法正常识别指定区域
        if not self.windowStates[WIN_STATE_AREA_OK]:
            WindowOp.update_window(self.hwnd,
                                   self.windowArea, self.windowSize,
                                   self.clientArea, self.clientSize,
                                   self.clientAreaMidPoint,
                                   self.windowStates)

    # ————————————————————————————————————————————————————————————————————
    # 关闭窗口
    def closeGame(self):
        if self.hwnd != 0:  # 如果绑定过窗口先解绑
            OP.UnBindWindow()
            self.hwnd = 0
        # 如果游戏窗口还存在，先关闭窗口。最多尝试关闭3次窗口（15s）
        retryCnt = 0
        while retryCnt < 3:
            if OP.GetWindowState(self.hwnd, 0) != 1:  # 窗口不存在
                # 窗口已经被关闭了，退出循环
                self.windowStates[WIN_STATE_EXIST] = False
                self.windowStates[WIN_STATE_RESPONSE] = False
                self.windowStates[WIN_STATE_ACTIVE] = False
                self.windowStates[WIN_STATE_AREA_OK] = False
                break
            retryCnt += 1

            # 发送指令：关闭窗口
            #  【】 【】 【】有问题。不要这样关闭，使用ESC，然后在游戏内点击来关闭。
            # ————————————————————————————————————————————————————————————————————
            if OP.SetWindowState(self.hwnd, 0) != 1:
                # ————————————————————————————————————————————————————————————————————

                G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error,f"尝试第{retryCnt}关闭窗口失败！")
            OP.Sleep(ParamTime.closeWinWait)  # 每次发送完关闭窗口的指令后，等待5秒

    # ————————————————————————————————————————————————————————————————————
    # 启动游戏：如果脚本是以管理员权限运行的话，那么程序也能以管理员权限启动
    def startGame(self) -> bool:
        # 只有先关闭现有的游戏窗口，才能重新启动游戏# 如果游戏窗口不存在了，再启动游戏
        if not self.windowStates[WIN_STATE_EXIST]:
            # 但是这里有一个问题。。运行这个程序会有弹窗，提示需要管理员权限。需要输入一个向左、然后一个Enter，才能运行程序。
            # 不过如果本脚本是以管理员权限运行的，那么也不会弹窗提示需要管理员权限了。

            #  【】 【】 【】有问题。这样启动后，游戏会提示异常。
            # ————————————————————————————————————————————————————————————————————
            OP.WinExec(GameInfo.gameLauncherPath, 1)  # 用最近的大小和位置显示,激活。  |
            # ————————————————————————————————————————————————————————————————————

            OP.Sleep(ParamTime.gameStartWaitTime)  # 启动后，等一段时间秒，让程序起来再说
            if not self.initSelf():
                G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error,f"初始化失败。")
                return False

            if not self.entryGame():
                return False

            return True
        G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.error,f"游戏窗口尚未关闭，无法重新启动游戏。")
        return False

    # 启动游戏后，怎么进入游戏正常界面
    def entryGame(self):
        # 尝试6次吧，如果不行，就进入失败，需要关闭游戏，然后重启游戏
        tryCnt = 0
        while tryCnt < 5:
            tryCnt += 1
            # 如果识别到了特征区域的特征字符串，就认为进入了启动界面1
            if GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_Start_1) == WinInfo.Text_Char_Game_Start_1:
                KeyOp.PressKey(OPKeyCode.Space)  # 按下空格
            # 等待一段时间
            OP.Sleep(ParamTime.gameStart1ToStart2)
            # 跳过启动界面2
            if GetScrInfo.findPic(WinInfo.Pic_Char_Game_Start_2, self.clientArea)[2] > 0:
                MouseOp.LeftClickPoint(WinInfo.Point_Safe_Click, self.ratio)  # 点击屏幕内的安全点
            # 等待一段时间
            OP.Sleep(ParamTime.gameStart2ToMainUI)
            # 跳过启动界面2后，如果识别到了特征图片“账号异常”。该故障不可恢复。需要关闭游戏，然后重启游戏
            if GetScrInfo.findPic(WinInfo.Pic_Char_Game_Start_2_Account_Err, self.clientArea)[2] > 0:
                G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.critical,f"账号异常！必须关闭游戏再重启游戏。")
                return False
            # 跳过启动界面2后，如果识别到了特征区域的特征字符串“账号异常”。该故障不可恢复。需要关闭游戏，然后重启游戏
            elif WinInfo.Text_Char_Game_Start_2_Err in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_Start_2_Err):
                G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.critical,f"账号异常！必须关闭游戏再重启游戏。")
                return False
            self.getCurUI()
            # 如果最后进入到游戏主界面/每日消息弹窗界面，那么就认为游戏启动成功
            if self.UI == GameInfo.UI_PVP_Main_Prepare or self.UI == GameInfo.UI_Daily_Msg:
                return True
        # 多次尝试，仍然失败
        return False

    # 通过截图然后OCR识别指定区域，来获取本局游戏剩余时间
    def getGameTimeLeft(self) -> bool:
        OP.Sleep(ParamTime.slp_cmd)
        timeLeftStr = GetScrInfo.ocrAreaText(WinInfo.Area_Time_Left)
        # 替换中文冒号为英文冒号，并去掉字符串中的空格
        timeLeftStr = timeLeftStr.replace('：', ':').replace(' ', '')
        # 如果识别到“12:23”之类的字符串，认为是获取到了剩余时间
        if self.is_valid_time_format(timeLeftStr):
            self.gameTimeLeftStr = timeLeftStr
            # 将时间段字符串转换为小时和分钟
            minutes, seconds = map(int, timeLeftStr.split(':'))
            # 创建一个 timedelta 对象，表示时间段
            time_delta = timedelta(minutes=minutes, seconds=seconds)
            # 获取当前时间，并计算倒计时的持续时间
            now = datetime.now()
            # 计算当前时间加上时间段后的新时间点
            game_end_time = now + time_delta  # 游戏结束的时间
            # 本局游戏还剩多少秒
            # leftTimeS = (game_end_time - now).total_seconds() #这个办法也可以获取秒数
            leftTimeS = minutes * 60 + seconds
            # 剩余时间的秒数，要在合理范围内，才认为正确
            if 0 < leftTimeS < ParamTime.TimeLeftS_WJSL_Max:
                # 获取本局游戏剩余时间
                self.gameTimeLeftS = leftTimeS
                # 获取本局游戏的结束时间点
                self.gameTimeEnd = game_end_time
                return True
        # 如果识别失败，则置为非法数据
        self.gameTimeLeftStr = "OCR识别剩余时间失败。"
        # 获取本局游戏剩余时间
        self.gameTimeLeftS = -1
        # 获取本局游戏的结束时间点
        self.gameTimeEnd = -1
        return False

    # 判断一个字符串是不是正确的时间格式，例如“06:23”是正确的
    @staticmethod
    def is_valid_time_format(time_str: str) -> bool:
        # 正则表达式匹配 "分钟:秒" 格式
        pattern = r'^[0-5]?[0-9]:[0-5]?[0-9]$'
        # 使用 re.match 来检查字符串是否匹配
        if re.match(pattern, time_str):
            return True
        else:
            return False

    # 检测用户输入暂停键，则休眠脚本
    def UserPause(self) -> bool:
        if self.endFlg:
            return False
        if KeyOp.DetectKey(ParamCnt.Key_User_Pause):
            G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"检测到用户输入暂停键，脚本休眠{ParamTime.slp_User_Pause}ms")
            # G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"检测到用户输入暂停键，脚本休眠{ParamTime.slp_User_Pause}ms")
            # G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.critical,f"检测到用户输入暂停键，脚本休眠{ParamTime.slp_User_Pause}ms")
            OP.Sleep(ParamTime.slp_User_Pause)
        return True # 这个True其实没啥用，因为已经执行完休眠才返回True

    # 获取无尽试炼模式的经验值
    @staticmethod
    def getEXP_WJSJ() -> int:
        OP.Sleep(ParamTime.slp_OCR)
        EXE1 = 0
        # EXPstr = GetScrInfo.ocrAreaText(WinInfo.Area_WJSL_EXE_Area_1)  # 如果截图指成功
        # # G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getEXP_WJSJ：OCR识别到经验值字符串：{EXPstr}")
        # EXPstr_int = re.findall(r"\d+", EXPstr)[0]
        # try:
        #     EXE1 = int(EXPstr_int)
        # except ValueError:
        #     G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"Error: '{EXPstr_int}' is not a valid integer.")
        #     EXE1 = ParamCnt.EXE_DEFAULT_WJSL
        # # G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"getEXP_WJSJ：OCR识别到经验值：{curEXP}")
        # # 经验值有自己的合理范围，如果不在合理范围内，就置0
        # if not (ParamCnt.EXE_MIN_WJSL <= EXE1 <= ParamCnt.EXE_MAX_WJSL):
        #     EXE1 = ParamCnt.EXE_DEFAULT_WJSL
        #     G_Sig.text_print.emit(self.ui.tEdit_errInfo, LogLevel.warning,f"OCR识别通行证经验值失败，记为默认经验值{ParamCnt.EXE_DEFAULT_WJSL}。")
        return EXE1

class Tools:
    # Shift+W奔跑的同时不断按E
    # runTime：奔跑时间，intervalE：E的间隔时间
    @staticmethod
    def RunAndE(runTime: int, intervalE: int):
        if runTime < intervalE:
            logging.error(f"输入参数非法：runTime < intervalE")
            return False
        # 先按住keyCode1,然后按住keyCode2，再抬起keyCode2，再抬起keyCode1
        OP.Sleep(OPTime.slp_cmd / 2)
        if OP.KeyDown(OPKeyCode.W) == 1:
            if OP.KeyDown(OPKeyCode.Shift) == 1:
                OP.Sleep(1000)   #按住Shift 0.5秒后，可以开始奔跑
                if OP.KeyUp(OPKeyCode.Shift) == 1:
                    cnt = int(runTime / intervalE)
                    # G_Sig.text_print.emit(self.ui.tEdit_info, LogLevel.info, f"cnt={cnt}")
                    idx = 0
                    while idx < cnt:
                        OP.Sleep(intervalE)
                        if OP.KeyPress(OPKeyCode.E) == 1:
                            print(f"E成功{idx + 1}次")
                        idx += 1
                    # print(f"退出循环，即将休眠{runTime - cnt * intervalE}")
                    OP.Sleep(runTime - cnt * intervalE)
                    if OP.KeyUp(OPKeyCode.W) == 1:
                        # print(f"函数成功！")
                        return True
        logging.error(f"RunAndE操作W失败")
        return False

    # 通关找色的方法查找本体的球
    @staticmethod
    def FindBossBenTi(findArea: list[4]):
        Pos = OP.FindColorEx(findArea[0], findArea[1], findArea[2], findArea[3], "87e4ff-000000", 1, 0)
        if len(Pos) > 0:
            allPos = Pos.split("|")
            print(allPos)
            curPos = allPos[0].split(",")
            OP.MoveTo(int(curPos[0])/2, int(curPos[1])/2)
        print(Pos)

# def run_auto():
#     Tools.FindBossBenTi([0, 0, 1920, 1080])
#     a = OP.FindMultiColor(19,654,60,696,"408b54","27|-8|fff0e8,52|-6|42a2d1,67|16|805998", 1, 0)
#     auto = Automation(PC_NAME, GAME_MODE_CUR)
#     if auto.initSelf():
#         # 初始化成功，开始自动化
#         auto.auto_play()


if __name__ == "__main__":
    # yml = RwYaml()
    # if yml.file_read_success:
        #读取配置表成功，才能进行操作
    #     sp1 = yml.read_value('hsbl', 'p1', 'sleep')
    #     yml.write_value('hsbl', 'p1', 'sleep', value=1001)
    # else:
    #     print(f"配置文件config.yml读取失败！脚本已退出！")
    ui_loader = QUiLoader()  # PySide6的bug，需要在QApplication前先实例这个类
    app = QApplication(sys.argv)  # 创建应用
    GameAutoGUI = Automation()
    GameAutoGUI.ui.show()
    sys.exit(app.exec())  # 开始执行程序，并且进入消息循环等待

