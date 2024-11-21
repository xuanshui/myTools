# import pyautogui
import ctypes
from ctypes import *
from win32com.client import Dispatch
# from Settings_WuJie14X import *
from Settings_Server import *
import logging  #日志记录
import random   #实现随机数
import re       #正则表达式
from datetime import datetime, timedelta    #获取时间
import time     # 实现倒计时
# from Settings_Server import *


#调整日志记录形式：以文本形式记录
LOG_FORMAT = "%(asctime)s- %(levelname)s -%(message)s"
log_file_name = "log.txt"
log_file_handler = logging.FileHandler(log_file_name, encoding='GBK')   #GB18030
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, handlers={log_file_handler})
# logging.basicConfig(filename=log_file_name, level=logging.DEBUG, format=LOG_FORMAT)

# 加载免注册dll
dll = windll.LoadLibrary(path_tools_dll)
# 调用setupW函数
result = dll.setupW(path_opx64_dll)
#开启DPI感知
ctypes.windll.user32.SetProcessDPIAware()

# 如果result不等于1,则执行失败
if result != 1:
    logging.critical("\n\nOP插件免注册dll加载失败！脚本已退出。\n\n")
    exit(0)

# OP的基础方法
class Automation:
    #初始化
    def __init__(self):
        # 创建com对象
        self.op = Dispatch("op.opsoft")

        self.hwnd = 0  # 窗口句柄
        self.send_hwnd = 0
        self.UI = game_info.UI_Err    #游戏的界面类型，-1为非法值表示未获取到界面信息
        # self.real_screen_resolution = [1440,900]    #实际的屏幕分辨率，该参数可以修改

        self.windowState_active = True #窗口是否处于激活状态？

        self.clientArea = []    #客户端窗口的坐标，四维列表
        self.clientSize = []    #客户端窗口的尺寸，二维列表
        self.clientAreaMidPoint = []    #客户端窗口的中心点
        self.windowSize = []    #窗口的尺寸，2维列表
        self.windowArea = []    #窗口的坐标，4维列表
        self.isBorderlessWindow = True  #默认用户设置Naraka为无边框窗口

        self.Ratio = 2 #屏幕物理分辨率/窗口矩形分辨率 = 比例，该参数可以修改
        self.RatioX = 2
        self.RatioY = 2
        self.op.SetShowErrorMsg(2)  # 设置是否弹出错误信息,默认是打开：0:关闭，1:显示为信息框，2:保存到文件,3:输出到标准输出

        self.gameTimeLeftStr = ""   #剩余时间的字符串，格式“07:12”
        self.gameTimeLeftS = 0   #本局游戏还剩余的时间：游戏右上角显示，这里的时间单位是秒
        self.gameTimeEnd = 0    #本局游戏应该在什么时间结束，即当前时间+游戏剩余时间
        self.EXP = 0        #脚本本次运行所获取的所有经验值
        self.holdTime = 0   #一局内的蓄力次数
        self.gameTime = 0   #游戏次数

        self.op.SetKeypadDelay("normal", 30)    #键盘按下和弹起之间的默认延时

        self.curPoint = [0,0]  #脚本当前应该点击的点
        logging.info("\n\n——————————————————————————————————————————————————————————————————————————————————————")
        logging.info(f"OP插件版本：{self.op.Ver()}") # 输出插件版本号
        logging.info(f"OP插件工作目录：：{self.op.GetPath()}") # 获取全局路径
        logging.info("脚本初始化成功！")

    # 基础测试：利用鼠标的移动来获取坐标倍数关系
    def base_test(self)->bool:
        tryCnt = 0  #坐标倍数调试次数
        while tryCnt < 10:
            tryCnt += 1
            #思路：
            # 1、先获取客户端窗口的坐标，然后计算移动的目标点①：窗口四点的中间点。
            #2、然后把使用op.MoveTo函数移动鼠标到目标点①，这时候再获取鼠标的实际位置点②。
            #3、如果点②x坐标/点①x坐标=点②y坐标/点①y坐标 ，那么倍率Ratio=点②x坐标/点①x坐标
            #4、验证Ratio正确性：计算对于op来说，目标点①所对应的实际目标点③：(③x坐标=①x坐标/Ratio,③y坐标=①y坐标/Ratio)
            # 再次使用op.MoveTo函数移动鼠标到点③，移动后立即判断当前鼠标位置点④和点①坐标是否相同？
            # 如果x、y坐标差值在2以内，就认为相同。返回坐标调试结果：True
            self.op.Sleep(code_control.Common_sleep) #先休眠100ms
            if self.op.SetWindowState(self.hwnd, 1) == 1:
                logging.info(f"激活窗口成功。")
            tmpArea = self.clientArea
            origin_pos = self.op.GetCursorPos() #记录鼠标原位置
            if origin_pos[0] != 1:  # 获取鼠标平面坐标失败，直接退出
                logging.error(f"基础测试：op.GetCursorPos()获取鼠标平面坐标失败1:{origin_pos[1:]}")
                return False
            else:
                logging.info(f"基础测试：op.GetCursorPos()获取鼠标平面坐标成功1:{origin_pos[1:]}")

            dstPoint1 = [int((tmpArea[0] + tmpArea[2]) / 2), int((tmpArea[1] + tmpArea[3]) / 2)]
            if self.op.MoveTo(dstPoint1[0], dstPoint1[1]) == 1:
                logging.info(f"基础测试：op.MoveTo()移动鼠标成功")
            else:
                logging.info(f"基础测试：op.MoveTo()移动鼠标失败")
                return False
            # 获取鼠标坐标
            tmp_cur_pos = self.op.GetCursorPos()  # 该函数返回了一个三元素的元组
            if tmp_cur_pos[0] != 1:  # 获取鼠标平面坐标失败，直接退出
                logging.error(f"基础测试：op.GetCursorPos()获取鼠标平面坐标失败2:{tmp_cur_pos[1:]}")
                return False
            else:
                logging.info(f"基础测试：op.GetCursorPos()获取鼠标平面坐标成功2:{tmp_cur_pos[1:]}")
            dstPoint2 = tmp_cur_pos[1:]  # 鼠标当前位置
            #获取坐标倍率:如果x坐标移动的倍率等于y坐标移动的倍率，则只算1个倍率
            # 精度：小数点后2位
            if f"{(dstPoint2[0] / dstPoint1[0]):.3f}" == f"{(dstPoint2[1] / dstPoint1[1]):.3f}":
                self.Ratio = round(dstPoint2[0] / dstPoint1[0], 3)
            else:
                self.RatioX = round(dstPoint2[0] / dstPoint1[0], 3)
                self.RatioY = round(dstPoint2[1] / dstPoint1[1], 3)
                logging.error(f"坐标存在倍率关系，x坐标倍率：{self.RatioX}，y坐标倍率：{self.RatioY}。"
                              f"需要更新代码。重新设计涉及到Ratio的各个函数：拆分单一Ratio倍率为RatioX倍率和RatioY倍率")
                return False    #并不是调试失败了，而是需要更新代码。
            #验证坐标倍率：再次移动
            dstPoint3 = [int(dstPoint1[0] / self.Ratio), int(dstPoint1[1] / self.Ratio)]
            self.op.MoveTo(dstPoint3[0], dstPoint3[1])
            #如果按照倍率移动鼠标，能够移动到预期位置（允许误差：±2个像素点），就认为成功！
            dstPoint4 = self.op.GetCursorPos()[1:]
            if (abs(dstPoint4[0] - dstPoint1[0]) <= 2) and (abs(dstPoint4[1] - dstPoint1[1]) <= 2):
                self.op.MoveTo(origin_pos[1]/self.Ratio, origin_pos[2]/self.Ratio) #恢复鼠标到原位置
                logging.info(f"基础测试：第{tryCnt}次调试，成功获取坐标倍率系数Ratio={self.Ratio}")
                return True
            else:
                logging.error(f"基础测试：第{tryCnt}次调试，获取坐标倍率系数Ratio失败！")
                return False

    def clear_window(self):
        self.op.UnBindWindow()

    #  r=self.op.WinExec("notepad",1); #运行可执行文件,0：隐藏，1：用最近的大小和位置显示,激活
    #  print("Exec notepad:",r);

    # 获取程序的窗口句柄
    # 非0：获取成功，返回窗口句柄。0：获取失败
    def get_window_by_name(self, cur_window_name):
        # 测试窗口接口
        self.hwnd = self.op.FindWindow("", cur_window_name)  # 通过窗口名称查找窗口句柄
        if self.hwnd != 0:
            logging.info(f"找到窗口：{cur_window_name}，parent hwnd:{self.hwnd}")
            # print(self.op.GetClientRect(self.hwnd))
            self.set_window()
            return self.hwnd
        else:
            logging.error(f"未找到窗口：{cur_window_name}")
            return 0

    def set_window(self):
        # 注意：GetClientRect和GetWindowRect得到的尺寸是不一样的。Clien只包含游戏主界面，Window还包含更多。
        # 例如Naraka的“窗口化”模式，Window尺寸(0, 0, 1306, 791)，Client尺寸(0, 0, 1280, 720)
        # 例如Naraka的“无边框窗口”模式，Window尺寸(0, 0, 1282, 722)，Client尺寸(0, 0, 1280, 720)
        if self.op.SetClientSize(self.hwnd, code_control.clientWindowSize_X,
                                 code_control.clientWindowSize_Y) != 1:
            logging.error(f"op.SetClientSize设置窗口尺寸失败")
            return False
        self.op.Sleep(code_control.Common_sleep)
        if self.op.MoveWindow(self.hwnd, 0, 0) != 1 :
            logging.error("移动窗口到[0,0]失败！")

        tmpClientArea = self.op.GetClientRect(self.hwnd)
        tmpWindowArea = self.op.GetWindowRect(self.hwnd)
        if tmpClientArea[0] != 1:
            logging.error(f"op.GetClientRect获取client窗口尺寸失败")
            return False
        if tmpWindowArea[0] != 1:
            logging.error(f"op.GetWindowRect获取window窗口尺寸失败")
            return False
        self.clientArea = tmpClientArea[1:]
        self.windowArea = tmpWindowArea[1:]
        logging.info(f"获取Client窗口坐标成功：{self.clientArea}")
        logging.info(f"获取Window窗口坐标成功：{self.clientArea}")
        logging.info(f"设置Client窗口尺寸成功：[{code_control.clientWindowSize_X}, {code_control.clientWindowSize_Y}]")

        self.clientSize = self.op.GetClientSize(self.hwnd)[1:]
        self.windowSize = [abs(self.windowArea[2]-self.windowArea[0]),abs(self.windowArea[3]-self.windowArea[1])]

        #如果window尺寸等于client尺寸（没有误差），则认为游戏窗口是无边框窗口
        if (self.clientSize[0]==self.windowSize[0]) and (self.clientSize[1]==self.windowSize[1]):
            self.isBorderlessWindow = True
        else:
            self.isBorderlessWindow = False

        # 设置窗口尺寸后，如果不是无边框窗口则需要重新移动窗口
        #如果窗口是无边框窗口：直接返回成功，无需移动窗口
        if self.isBorderlessWindow:
            # if self.op.MoveWindow(self.hwnd, -1, -1):  # 移动窗口到左上角。注意
            #     logging.info("移动窗口到左上角成功")
            # else:
            #     logging.warning("移动窗口到左上角失败")
            return True
        # 如果窗口是普通窗口（有边框）：分别向x、y方向多移动一些距离，才能使client真正到达左上角
        # 因为op插件给的函数时MoveWindow()不是MoveClient()
        else:
            # 如果移动到左上角，需要移动的多余像素点数量，分为x方向和y方向
            windowMoveX = abs(self.clientArea[0] - self.windowArea[0])
            windowMoveY = abs(self.clientArea[1] - self.windowArea[1])
            if self.op.MoveWindow(self.hwnd, -windowMoveX, -windowMoveY):  # 移动窗口到左上角。Naraka的数据是x：-13，y：-58
                logging.info("移动窗口到左上角成功")
            else:
                logging.warning("移动窗口到左上角失败")
        tmpClientArea = self.op.GetClientRect(self.hwnd)
        tmpWindowArea = self.op.GetWindowRect(self.hwnd)
        self.clientArea = tmpClientArea[1:]
        self.windowArea = tmpWindowArea[1:]
        logging.info(f"获取client窗口坐标成功：{self.clientArea}")
        logging.info(f"获取window窗口坐标成功：{self.windowArea}")
        # 获取窗口中心点坐标
        self.clientAreaMidPoint = [(self.clientArea[0] + self.clientArea[2]) / 2,
                                   (self.clientArea[1] + self.clientArea[3]) / 2]
        logging.info(f"client窗口中心点坐标：{self.clientAreaMidPoint}")

        # op插件的GetWindowState函数获取窗口是否处于激活状态
        if self.op.GetWindowState(self.hwnd, 1) == 1:
            self.windowState_active = True
        else:
            self.windowState_active = False
        logging.info(f"client窗口是否激活：{self.windowState_active}")

    # 绑定窗口hwnd，方便后面进行后台操作、获取相对坐标位置
    # 返回值：1成功，0失败
    def bind_window(self):
        # 绑定指定的窗口,并指定这个窗口的屏幕颜色获取方式(normal前台),鼠标仿真模式(normal前台),
        # 键盘仿真模式(normal前台),以及模式设定(0/1:都一样).
        # 绑定窗口后，一定要记得释放窗口UnBindWindow()，否则游戏可能异常
        # 绑定之后,所有的坐标都相对于窗口的客户区坐标(不包含窗口边框)
        # Naraka游戏中，
        # 屏幕显示：设置为normal，可以
        # 鼠标：设置为normal，可以
        # 键盘：必需设置为normal.hd才能进行输入
        # 模式：设置为0，可以
        r = self.op.BindWindow(self.hwnd, "normal", "normal", "normal.hd", 0)
        if r == 0:
            logging.warning(f"绑定窗口{window_name}失败。bind false")
        else:
            logging.info(f"成功绑定窗口{window_name}")


        return r

    # 自动化操作
    def auto_play(self, range_r:int):
        #1、窗口激活
        if self.op.SetWindowState(self.hwnd,1) == 1:  #激活窗口，显示到前台
            logging.info(f"激活窗口成功")
        else:
            logging.error(f"激活窗口失败")

        #2、主循环
        count = 0       #周期计数
        errUICnt = 0    #进入脚本认为可以跳过的界面（错误界面errUI）的次数
        while True:  #一直进行
        # while count < code_control.loop_count:  # 循环次数
            count += 1  #计数器自增
            # 检测用户输入暂停键:如果用户按下CapLock，则休眠30秒
            self.UserPause()

            self.op.Sleep(code_control.sleep_main_cycle)# 周期300ms

            # op插件的GetWindowState函数获取窗口是否处于激活状态
            if self.op.GetWindowState(self.hwnd, 1) == 1:
                self.windowState_active = True
            else:
                self.windowState_active = False

            if count % 5 == 0 : #每5个周期激活一次窗口。不能每个周期都检查，不然就没法关闭游戏了。
                if not self.windowState_active: #如果当前不是激活状态
                    if self.op.SetWindowState(self.hwnd,1) == 1:  #激活窗口，显示到前台
                        logging.info(f"检测到窗口未激活，尝试激活窗口成功。")
                    else:
                        logging.error(f"检测到窗口未激活，尝试激活窗口失败！")

            # 如果窗口尺寸发生变化，重新设置窗口尺寸
            curWindowArea = self.op.GetWindowRect(self.hwnd)[1:]    #窗口尺寸
            curClientArea = self.op.GetClientRect(self.hwnd)[1:]    #客户端尺寸
            #如果window区域坐标或Client区域坐标发生任何变化，都重新设置窗口大小、位置
            if (curWindowArea[0] != self.windowArea[0] or curWindowArea[1] != self.windowArea[1]
                    or curWindowArea[2] != self.windowArea[2] or curWindowArea[3] != self.windowArea[3]
                    or curClientArea[0] != self.clientArea[0] or curClientArea[1] != self.clientArea[1]
                    or curClientArea[2] != self.clientArea[2] or curClientArea[3] != self.clientArea[3]):
                self.set_window()

            #获取当前界面
            self.UI = self.get_cur_UI()

            # 主界面-未点击“开始游戏”
            if self.UI == game_info.UI_PVP_Main_Prepare:
                # 检测用户输入暂停键:如果用户按下CapLock，则休眠30秒
                self.UserPause()
                logging.info("【进入主界面：未点击“开始游戏”】")
                if self.MoveToAreaRandom(UIInfo.UI_main_area):
                    if self.LeftClick():
                        # self.gameTime += 1 #这里获取游戏次数不对，因为可能存在匹配失败，多次点击“开始游戏”的情况
                        logging.info("主界面：点击“开始游戏”成功")
                        logging.info(f"【【游戏局数：{self.gameTime }】】")
                        # 点击开始后进入游戏，休眠等15秒进游戏：尝试匹配15秒
                        self.op.Sleep(code_control.sleep_after_start_game)

            # 主界面：正在匹配：匹配过久则取消匹配。
            if self.UI == game_info.UI_PVE_Main_Enter:
                # 检测用户输入暂停键:如果用户按下CapLock，则休眠30秒
                self.UserPause()
                logging.info("【进入主界面：正在匹配】")
                if self.MoveToAreaRandom(UIInfo.UI_main_area):
                    if self.LeftClick():
                        # self.gameTime += 1 #这里获取游戏次数不对，因为可能存在匹配失败，多次点击“开始游戏”的情况
                        logging.warning(f"主界面：等待{code_control.sleep_after_start_game}"
                                     f"秒后游戏未开始，认为匹配失败，取消匹配，等待下一次脚本点击“开始游戏”")


            # 选择英雄界面
            elif self.UI == game_info.UI_PVP_Select_Hero:
                # 检测用户输入暂停键:如果用户按下CapLock，则休眠30秒
                self.UserPause()
                logging.info("【进入英雄选择界面：】")
                if self.MoveToAreaRandom(UIInfo.UI_Select_cur_hero):
                    if self.LeftClick():
                        logging.info("英雄选择界面：点击“使用”成功")
                    else:
                        logging.error("英雄选择界面：点击“使用”失败")
                else:
                    logging.error("英雄选择界面：移动鼠标到“使用”失败")

            # 选择跳点界面
            elif self.UI == game_info.UI_PVP_Select_Point:
                #不选跳点，随机跳点，等待进入游戏
                # 检测用户输入暂停键:如果用户按下CapLock，则休眠30秒
                self.UserPause()
                pass

            # 游戏内界面：未死亡
            elif self.UI == game_info.UI_PVP_Game_in:
                # 检测用户输入暂停键:如果用户按下CapLock，则休眠30秒
                self.UserPause()
                #重复进行空手右键蓄力
                self.holdTime = 0
                logging.info("【进入游戏局内界面：】")
                if self.getGameTimeLeft():
                    logging.info(f"本局游戏剩余时间：{self.gameTimeLeftStr}")
                #下面进行一次右键蓄力
                if self.MoveToAreaRandom(UIInfo.UI_Random_left_move):
                    if self.RightHold(random.randint(code_control.HoldTimeStart,code_control.HoldTimeEnd)):
                        logging.info("游戏局内界面：使用右键蓄力成功")

            # 游戏内界面：死亡，待返魂【无尽试炼不存在该界面】
            elif self.UI == game_info.UI_PVP_Game_dad:
                # 重复进行跳跃
                # 检测用户输入暂停键:如果用户按下CapLock，则休眠30秒
                self.UserPause()
                logging.info("【进入游戏局内界面：死亡，待返魂】")

            # 结算界面1
            elif self.UI == game_info.UI_PVP_Game_End1:
                # 检测用户输入暂停键:如果用户按下CapLock，则休眠30秒
                self.UserPause()
                #后续：OCR识别获取击败数量
                logging.info("【进入结算界面2：】")
                if self.MoveToAreaRandom(UIInfo.UI_end_area1):
                    if self.LeftClick():
                        logging.info("跳过了结算界面2")


            # 结算界面2
            elif self.UI == game_info.UI_PVP_Game_End2:
                # 检测用户输入暂停键:如果用户按下CapLock，则休眠30秒
                self.UserPause()
                #后续：OCR识别获取增加的经验
                logging.info("【进入结算界面3：】")
                if self.MoveToAreaRandom(UIInfo.UI_end_area1):
                    if self.LeftClick():
                        logging.info("跳过了结算界面3")

            # 结算界面4
            elif self.UI == game_info.UI_PVP_Game_End4:
                # 检测用户输入暂停键:如果用户按下CapLock，则休眠30秒
                self.UserPause()
                self.gameTime += 1
                #后续：OCR识别获取增加的经验
                logging.info("【进入结算界面4：】")
                #获取经验值EXP
                curEXP = self.getEXP()
                self.EXP += curEXP
                logging.info(f"本局游戏经验值：{curEXP}(若为0则表示OCR识别经验值失败。)")
                logging.info(f"本次脚本已获取游戏经验值：{self.EXP}")
                self.op.Sleep(code_control.Common_sleep)
                if self.PressKey(key_code.Space):
                    logging.warning("使用空格跳过结算界面4")

            # 可以空格跳过的界面
            elif self.UI == game_info.UI_Skip_Space:
                self.op.Sleep(code_control.Common_sleep)
                if self.PressKey(key_code.Space):
                    logging.warning("可以空格跳过的界面：尝试跳出错误界面，输入一次“空格”")

            # 可以ESC跳过的界面
            elif self.UI == game_info.UI_Skip_ESC:
                self.op.Sleep(code_control.Common_sleep)
                if self.PressKey(key_code.ESC):
                    logging.warning("可以ESC跳过的界面：尝试跳出错误界面，输入一次“ESC”")

            # 返回游戏界面：一般是误触ESC导致的
            elif self.UI == game_info.UI_Return_game:
                self.op.Sleep(code_control.Common_sleep)
                #移动到“返回游戏”，然后点击
                self.MoveTo(self.curPoint)
                self.LeftClick()
                logging.warning("误触ESC的界面：尝试跳出错误界面，点击一次“返回游戏”")

            # 非法界面
            else:
                # 检测用户输入暂停键:如果用户按下CapLock，则休眠30秒
                self.UserPause()
                # 不是上面的界面，则认为是错误界面信息，重新获取界面类型。并尝试以下3种方法跳出错误界面：
                #1、按空格，2、按ESC，3、鼠标点击客户端中心位置
                if count % 10 == 0 :    #经历6次循环判断，都无法判断出正确的界面，再尝试跳出
                    errUICnt += 1
                    # 移动鼠标到客户端[167,96]位置，点一下。
                    self.MoveTo([167,96])
                    self.op.Sleep(code_control.Common_sleep)
                    self.LeftClick()
                    logging.warning("尝试跳出错误界面：鼠标点击客户端[167,96]位置一次")
                    self.op.Sleep(code_control.Common_sleep)
                    if errUICnt % 2 == 0 :
                        self.PressKey(key_code.Space)
                        logging.warning("尝试跳出错误界面：输入一次“空格”")
                    else:
                        self.PressKey(key_code.ESC)
                        logging.warning("尝试跳出错误界面：输入一次“ESC”")
                    self.op.Sleep(code_control.Common_sleep)

                    pass


    # 获取本局游戏剩余时间，返回结束时间
    def getGameTimeLeft(self)->bool:
        picFullName = "/Pic/tmpScreen.bmp"
        self.op.Sleep(code_control.Common_sleep)
        if self.captureArea(UI_info.UI_time_left, picFullName):  # 如果截图指成功
            self.op.Sleep(code_control.OCR_sleep)
            # 如果识别到“12:23”之类的字符串，认为是获取到了剩余时间
            time_str = self.ocr_pic_text(picFullName)
            # 替换中文冒号为英文冒号，并去掉字符串中的空格
            time_str = time_str.replace('：', ':').replace(' ', '')
            if self.is_valid_time_format(time_str):#先判断字符串是不是

                # 将时间段字符串转换为小时和分钟
                minutes, seconds = map(int, time_str.split(':'))
                # 创建一个 timedelta 对象，表示时间段
                time_delta = timedelta(minutes=minutes,seconds=seconds)
                # 获取当前时间，并计算倒计时的持续时间
                now = datetime.now()
                # 计算当前时间加上时间段后的新时间点
                game_end_time = now + time_delta    #游戏结束的时间
                # 本局游戏还剩多少秒
                leftTimeS = (game_end_time - now).total_seconds()
                leftTimeS = minutes * 60 + seconds
                if 0 < leftTimeS < game_info.TimeLeftS_Max: #剩余时间的秒数，要在合理范围内，才认为正确

                    self.gameTimeLeftStr = time_str
                    # 获取本局游戏剩余时间
                    self.gameTimeLeftS = leftTimeS
                    # 获取本局游戏的结束时间点
                    self.gameTimeEnd = game_end_time
                    return True
            self.gameTimeLeftStr = ""
            # 获取本局游戏剩余时间
            self.gameTimeLeftS = -1
            # 获取本局游戏的结束时间点
            self.gameTimeEnd = -1
            return False

    #正确的时间格式：“06:23”
    @staticmethod
    def is_valid_time_format(time_str:str)->bool:
        # 尝试解析时间格式
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False

    #检测用户输入暂停键，则休眠脚本
    def UserPause(self):
        if self.op.GetKeyState(code_control.key_user_paused):
            logging.critical(f"检测到用户输入暂停键，脚本休眠{code_control.sleep_user_paused}ms")
            self.op.Sleep(code_control.sleep_user_paused)

    def PressKey(self,  keyCode: int) -> bool:
        self.op.Sleep(code_control.Common_sleep/2)
        if self.op.KeyPress(keyCode) == 1:
            # logging.info(f"PressKey点击一次{keyCode}键成功")
            return True
        logging.error(f"PressKey点击一次{keyCode}键失败")
        return False
        # if self.op.KeyPress(27) == 1:   #27=esc
        #     pass
        #     logging.info(f"KeyPress点击一次esc键成功")
        # if self.op.KeyDownChar(keyStr) == 1:
        #     self.op.Sleep(random.randint(10, 30))  # 按下20ms到80ms
        #     if self.op.KeyUpChar(keyStr) == 1:
        #         # logging.info(f"按下和弹起{keyStr}键成功")
        #         return True
        #     else:
        #         logging.error(f"弹起{keyStr}键失败")
        #         return False
        # else:
        #     logging.error(f"按下{keyStr}键失败")
        #     return False

    def getEXP(self)->int:
        EXE1picFullName = "/Pic/tmpEXP1.bmp"
        EXE2picFullName = "/Pic/tmpEXP2.bmp"
        EXE1 = 0
        EXE2 = 0
        self.op.Sleep(code_control.Capture_sleep)
        if self.captureArea(UI_info.UI_EXE_area_1, EXE1picFullName):  # 如果截图指成功
            self.op.Sleep(code_control.OCR_sleep)
            EXPstr = self.ocr_pic_text(EXE1picFullName)
            if EXPstr != "":
                # logging.info(f"getEXP：OCR识别到经验值字符串：{EXPstr}")
                curEXP = int(re.findall(r"\d+",EXPstr)[0])
                # logging.info(f"getEXP：OCR识别到经验值：{curEXP}")
                if curEXP > 0:
                    if game_info.EXE_MIN <= curEXP <= game_info.EXE_MAX:
                        EXE1 = curEXP
                    else:
                        EXE1 = 0
        else:
            logging.error(f"captureArea：截图区域{UI_info.UI_EXE_area_1}失败。")
        self.op.Sleep(code_control.Capture_sleep)
        if self.captureArea(UI_info.UI_EXE_area_2, EXE2picFullName):  # 如果截图指成功
            self.op.Sleep(code_control.OCR_sleep)
            EXPstr = self.ocr_pic_text(EXE2picFullName)
            if EXPstr != "":
                # logging.info(f"getEXP：OCR识别到经验值字符串：{EXPstr}")
                curEXP = int(re.findall(r"\d+",EXPstr)[0])
                # logging.info(f"getEXP：OCR识别到经验值：{curEXP}")
                if curEXP > 0:
                    if game_info.EXE_MIN <= curEXP <= game_info.EXE_MAX:
                        EXE2 = curEXP
                    else:
                        EXE2 = 0
        else:
            logging.error(f"captureArea：截图区域{UI_info.UI_EXE_area_2}失败。")
        if (EXE1 == EXE2) and (EXE1 != 0):
            return EXE1 #这里可能是正确的经验值，也可能是0
        else:
            logging.error(f"OCR识别通行证经验值，精确值({EXE1}) ≠ 粗略值({EXE2})")
            if EXE1 == 0 and EXE2 != 0 :
                return EXE2
            elif EXE2 == 0 and EXE1 != 0 :
                return EXE1
            else:
                return EXE1


    #移动鼠标到目标位置
    def MoveTo(self, dstPoint:list[2])->bool:
        self.op.Sleep(code_control.Move_sleep)
        if self.op.MoveTo(dstPoint[0] / self.Ratio, dstPoint[1] / self.Ratio) == 1:
            # logging.info(f"移动鼠标成功，目标地址：{dstPoint}")
            return True
        else:
            logging.warning(f"移动鼠标失败！目标位置：{dstPoint}，当前位置：{self.op.GetCursorPos()[1:]}")
            return False

    #移动鼠标到目标位置附近范围的随机一个地方，随机的范围可以设置
    def MoveToRandom(self, dstPoint:list[2])->bool:
        self.op.Sleep(code_control.Move_sleep)
        newDstPoint = self.op.MoveToEx(dstPoint[0] / self.Ratio, dstPoint[1] / self.Ratio,
                            code_control.Random_range_x, code_control.Random_range_y)
        if newDstPoint != "":
            # logging.info(f"移动鼠标成功，目标地址：({newDstPoint})")
            return True
        else:
            logging.warning(f"随机移动鼠标失败！目标位置：{dstPoint}附近随机范围，当前位置：{self.op.GetCursorPos()[1:]}")
            return False

    # 移动鼠标到目标区域内的随机一个地方
    def MoveToAreaRandom(self, dstArea: list[4]) -> bool:
        self.op.Sleep(code_control.Move_sleep)
        randomX = random.randint(int(dstArea[0]),int(dstArea[2]))
        randomY = random.randint(int(dstArea[1]),int(dstArea[3]))
        newDstPoint = [randomX, randomY]
        # curDstPoint = self.op.GetCursorPos()[1:]  # 移动前鼠标位置
        ret = self.op.MoveTo(newDstPoint[0] / self.Ratio, newDstPoint[1] / self.Ratio)
        curDstPoint2 = self.op.GetCursorPos()[1:]  # 移动后鼠标位置
        if self.InArea(curDstPoint2, dstArea):
            if ret != 0:
                # logging.info(f"移动鼠标成功，目标地址：({newDstPoint})")
                return True
            else:
                logging.warning(f"随机移动鼠标失败！目标区域：{dstArea}范围内随机位置，当前位置：{curDstPoint2}")
                return False
        else:
            logging.warning(f"随机移动鼠标超范围！目标区域：{dstArea}范围内随机位置，当前位置：{curDstPoint2}")
            return False

    @staticmethod
    def InArea(curPoint:list[2], curArea:list[4])->bool:
        if curArea[0] <= curPoint[0] <= curArea[2]:
            if curArea[1] <= curPoint[1] <= curArea[3]:
                return True
        return False

    #单击一下鼠标左键
    def LeftClick(self)->bool:
        self.op.Sleep(code_control.Click_sleep)
        if self.op.LeftClick() == 1:
            # logging.info(f"点击鼠标左键成功，点击位置：{self.op.GetCursorPos()[1:]}")
            return True
        else:
            logging.warning(f"点击鼠标左键失败")
            return False

    # 单击一下鼠标右键
    def RightClick(self) -> bool:
        self.op.Sleep(code_control.Click_sleep)
        if self.op.RightClick() == 1:
            # logging.info(f"点击鼠标左键成功，点击位置：{self.op.GetCursorPos()[1:]}")
            return True
        else:
            logging.warning(f"点击鼠标左键失败")
            return False

    #按下鼠标左键一段时间，然后抬起
    def LeftHold(self,holdTime:int)->bool:
        self.op.Sleep(code_control.Click_sleep)
        if self.op.LeftDown() == 1:
            self.op.Sleep(holdTime)
            if self.op.LeftUp() == 1:
                # logging.info(f"按下并抬起鼠标左键成功，点击位置：{self.op.GetCursorPos()[1:]}")
                return True
            else:
                logging.warning(f"抬起鼠标左键失败")
                return False
        else:
            logging.warning(f"按下鼠标左键失败")
            return False

    # 按下鼠标右键一段时间，然后抬起
    def RightHold(self, holdTime: int) -> bool:
        self.op.Sleep(code_control.Click_sleep)
        if self.op.RightDown() == 1:
            self.op.Sleep(holdTime)
            if self.op.RightUp() == 1:
                # logging.info(f"按下并抬起鼠标右键成功，点击位置：{self.op.GetCursorPos()[1:]}")
                return True
            else:
                logging.warning(f"抬起鼠标右 键失败")
                return False
        else:
            logging.warning(f"按下鼠标右键失败")
            return False

    def get_cur_UI(self)->int:
        # 如果游戏局内时间超过25秒，直接返回当前界面为游戏内界面
        if self.gameTimeLeftS >= code_control.GameInTimeS_MAX:
            return game_info.UI_PVP_Game_in

        picFullName = "/Pic/tmpScreen.bmp"

        # 当前界面是否为结算界面4-经验值界面？下面两个方式都可以认为是经验结算界面
        self.op.Sleep(code_control.Common_sleep);
        if self.captureArea(UI_info.UI_end_area4, picFullName):  # 如果截图指成功
            if self.ocr_pic_text(picFullName) == UI_info.UI_end_text4:
                logging.info(f"get_cur_UI：OCR指定区域{UI_info.UI_end_area4}识别到进入结算界面4：通行证经验值")
                return game_info.UI_PVP_Game_End4
        else:
            logging.error(f"captureArea：截图区域{UI_info.UI_end_area4}失败。")
        # self.op.Sleep(code_control.FindPic_sleep)
        # findPicRlt = self.findPic("/Pic/EXEUI_Pic.bmp", code_control.FindPic_sim)
        # if findPicRlt[0] != -1:
        #     logging.info(f"get_cur_UI：找到图片EXEUI_Pic.bmp左上角坐标：{findPicRlt[1:]}："
        #                  f"该界面需先OCR获取通行证经验，然后使用空格进行跳过")
        #     return game_info.UI_PVP_Game_End4

        # #通过查找屏幕截图中是否存在特征图片，来判断模式：可以使用空格进行跳过
        self.op.Sleep(code_control.FindPic_sleep)
        findPicRlt = self.findPic("/Pic/skipPic1.bmp", code_control.FindPic_sim)
        if findPicRlt[0] != -1:
            logging.info(f"get_cur_UI：找到图片skipPic1.bmp左上角坐标：{findPicRlt[1:]}：该界面可以使用空格进行跳过")
            return game_info.UI_Skip_Space
        # #通过查找屏幕截图中是否存在特征图片，来判断模式：可以使用空格进行跳过
        self.op.Sleep(code_control.FindPic_sleep)
        findPicRlt = self.findPic("/Pic/skipPic2.bmp", code_control.FindPic_sim)
        if findPicRlt[0] != -1:
            logging.info(f"get_cur_UI：找到图片skipPic2.bmp左上角坐标：{findPicRlt[1:]}：该界面可以使用空格进行跳过")
            return game_info.UI_Skip_Space

        # #通过查找屏幕截图中是否存在特征图片，来判断模式：可以使用ESC进行跳过
        self.op.Sleep(code_control.FindPic_sleep)
        findPicRlt = self.findPic("/Pic/skipPic3.bmp", code_control.FindPic_sim)
        if findPicRlt[0] != -1:
            logging.info(f"get_cur_UI：找到图片skipPic3.bmp左上角坐标：{findPicRlt[1:]}：该界面可以使用空格进行跳过")
            return game_info.UI_Skip_ESC

        # #通过查找屏幕截图中是否存在特征图片，来判断模式：是否误触ESC？如果是，后面应该点击“返回游戏”
        self.op.Sleep(code_control.FindPic_sleep)
        findPicRlt = self.findPic("/Pic/ReturnGame.bmp", code_control.FindPic_sim)
        if findPicRlt[0] != -1:
            logging.info(f"get_cur_UI：找到图片ReturnGame.bmp左上角坐标：{findPicRlt[1:]}：该界面可以使用空格进行跳过")
            #要点击的位置是比“返回游戏”略微向右下角多出2个像素点
            self.curPoint[0] = findPicRlt[1] + 2
            self.curPoint[1] = findPicRlt[2] + 2
            return game_info.UI_Return_game


        #先截图屏幕指定区域，再OCR识别指定区域文字来判断
        self.op.Sleep(code_control.Common_sleep);


        # 是否为主界面？
        self.op.Sleep(code_control.Common_sleep);
        if self.captureArea(UI_info.UI_main_area, picFullName) :   #如果截图指成功
            if self.ocr_pic_text(picFullName) == UI_info.UI_main_text1 :
                logging.info(f"get_cur_UI：OCR识别到进入主界面：未开始")
                return game_info.UI_PVP_Main_Prepare
            else:
                if self.ocr_pic_text(picFullName) == UI_info.UI_main_text2:
                    logging.info(f"get_cur_UI：OCR识别到进入主界面：已开始，正在匹配")
                    return game_info.UI_PVE_Main_Enter
        else:
            logging.error(f"captureArea：截图区域{UI_info.UI_main_area}失败。")

        # 是否为英雄选择界面？
        self.op.Sleep(code_control.Common_sleep);
        if self.captureArea(UI_info.UI_select_hero_area, picFullName):  # 如果截图指成功
            if self.ocr_pic_text(picFullName) == UI_info.UI_select_hero_text:
                logging.info(f"get_cur_UI：OCR识别到进入英雄选择界面")
                return game_info.UI_PVP_Select_Hero
        else:
            logging.error(f"captureArea：截图区域{UI_info.UI_select_hero_text}失败。")

        # 是否为跳点选择界面：聚窟州？
        self.op.Sleep(code_control.Common_sleep)
        if self.captureArea(UI_info.UI_select_point_area, picFullName):  # 如果截图指成功
            if self.ocr_pic_text(picFullName) == UI_info.UI_select_point_text1:
                logging.info(f"get_cur_UI：OCR识别到进入跳点选择界面：{UI_info.UI_select_point_text1}")
                return game_info.UI_PVP_Select_Point
            # elif self.ocr_pic_text(picFullName) == UI_info.UI_select_point_text2:
            #     logging.info(f"get_cur_UI：OCR识别到进入跳点选择界面：{UI_info.UI_select_point_text2}")
            #     return game_info.UI_PVP_Select_Point
        else:
            logging.error(f"captureArea：截图区域{UI_info.UI_select_point_area}失败。")


        # 是否为结算界面1？
        # 截图前休眠
        self.op.Sleep(code_control.Common_sleep)
        if self.captureArea(UI_info.UI_end_area1, picFullName):  # 如果截图指成功
            if self.ocr_pic_text(picFullName) == UI_info.UI_end_text1: #OCR识别："返回大厅"
                logging.info(f"get_cur_UI：OCR识别到进入结算界面1")
                return game_info.UI_PVP_Game_End1
            else:
                # 截图前休眠
                self.op.Sleep(code_control.Common_sleep)
        else:
            logging.error(f"captureArea：截图区域{UI_info.UI_game_end11}失败")


        # 是否为结算界面2？
        if self.captureArea(UI_info.UI_end_area2, picFullName):  # 如果截图指成功
            # OCR前休眠
            if self.ocr_pic_text(picFullName) == UI_info.UI_end_text2: #OCR识别："继续“
                logging.info(f"get_cur_UI：OCR识别到进入结算界面2")
                return game_info.UI_PVP_Game_End2
        else:
            logging.error(f"captureArea：截图区域{UI_info.UI_game_end2}失败。")

        # 无尽试炼没有这一项内容。正常排位/人机模式才有。
        # # 是否为游戏内界面，已死亡待返魂：特征：中间:有“进入返魂坛复活”的字样
        # self.op.Sleep(code_control.Common_sleep)
        # if self.captureArea(UI_info.UI_game_dad, picFullName):  # 如果截图指成功
        #     self.op.Sleep(code_control.OCR_sleep)
        #     if self.ocr_pic_text(picFullName) == UI_info.UI_game_dad_text:
        #         logging.info(f"get_cur_UI：OCR识别到进入游戏内界面：已死亡，待返魂")
        #         return game_info.UI_PVP_Game_dad
        # else:
        #     logging.error(f"captureArea：截图区域{UI_info.UI_game_dad}失败。")

        # 是否为游戏内界面，未死亡：特征1，左上角的“排名”，无尽试炼特有：特征2，护甲粉末，特征3，凝血丸（因为无尽试炼出生就有）
        self.op.Sleep(code_control.Common_sleep)
        if self.captureArea(UI_info.UI_game_area, picFullName):  # 如果截图指成功
            self.op.Sleep(code_control.OCR_sleep)
            # 如果识别到“排名”，认为是在游戏内
            if self.ocr_pic_text(picFullName) == UI_info.UI_game_text:
                logging.info(f"get_cur_UI：OCR识别到进入游戏内界面，特征字：{UI_info.UI_game_text}")
                return game_info.UI_PVP_Game_in
        else:
            logging.error(f"captureArea：截图区域{UI_info.UI_game_area}失败。")
        # #通过查找屏幕截图中是否存在特征图片护甲粉末ArmorPowder.bmp，来判断是否为游戏内界面
        self.op.Sleep(code_control.FindPic_sleep)
        findPicRlt = self.findPic("/Pic/ArmorPowder2.bmp", code_control.FindPic_sim)
        if findPicRlt[0] != -1:
            logging.info(f"get_cur_UI：找到图片ArmorPowder2.bmp左上角坐标：{findPicRlt[1:]}：此时处于游戏内界面")
            return game_info.UI_PVP_Game_in
        # #通过查找屏幕截图中是否存在特征图片凝血丸BloodPill2.bmp，来判断是否为游戏内界面
        self.op.Sleep(code_control.FindPic_sleep)
        findPicRlt = self.findPic("/Pic/BloodPill2.bmp", code_control.FindPic_sim)
        if findPicRlt[0] != -1:
            logging.info(f"get_cur_UI：找到图片BloodPill2.bmp左上角坐标：{findPicRlt[1:]}：此时处于游戏内界面")
            return game_info.UI_PVP_Game_in


        # 不符合任何一个特征，就认为进入了错误界面
        logging.error(f"get_cur_UI：界面识别失败。")
        return game_info.UI_Err


    #在整个屏幕截图中查找指定图片的位置，每次查找耗时约110ms
    def findPic(self, pic_name: str,sim:float) -> int:
        area = self.clientArea
        #有BUG，要么进行一次休眠，要么连续查找2次。否则会失败
        self.op.Sleep(code_control.FindPic_sleep)
        pos = self.op.FindPic(area[0], area[1],area[2], area[3],pic_name, "000000", sim, 0)
        return pos

    #对指定区域进行截图，如果截图成功则返回1，失败返回0：每次截图耗时约7ms～15ms
    def captureArea(self,area:list[4],picFullName:str)->bool:
        self.op.Sleep(code_control.Capture_sleep)
        screenCapture = self.op.Capture(area[0], area[1], area[2],area[3],picFullName)
        if screenCapture == 1:
            return True
        else :
            return False

    #获取指定区域内的文字：每次调用消耗时间：1035ms
    def ocr_area_text(self, area)->str:
        self.op.Sleep(code_control.OCR_sleep);
        #对指定区域area进行OCR文字识别
        text = self.op.OcrAuto(area[0], area[1], area[2], area[3], code_control.OCR_sim)
        if text != "":
            logging.info(f"get_area_text：OCR识别区域{area}成功：\n{text}")
        else:
            logging.info(f"get_area_text：OCR识别区域{area}失败。")

        return text

    # 获取指定区域内的文字：针对同一张图片，第一次调用耗时800ms，往后每次调用，耗时约30ms～40ms
    def ocr_pic_text(self, picPath:str) -> str:
        # 对指定区域area进行OCR文字识别
        text = self.op.OcrFromFile(picPath,"9f2e3f-000000",code_control.OCR_sim)
        if text != "":
            # logging.info(f"get_pic_area_text：OCR识别图片{picPath}成功：\n{text}")
            pass
        else:
            # logging.info(f"get_pic_area_text：OCR识别图片{picPath}失败。")
            pass
        return text


    def UI_main_fun(self):
        pass

    def UI_select_fun(self):
        pass

    def UI_settlement_fun1(self):
        pass

    def UI_settlement_fun2(self):
        pass

    #游戏内界面：重复进行：随机移动，右键蓄力后释放、左键蓄力蓄力后释放
    def UI_game_fun(self):
        tmp_cur_pos = self.op.GetCursorPos()  # 该函数返回了一个三元素的元组
        if tmp_cur_pos[0] != 1:  # 获取鼠标平面坐标失败，直接退出
            # 【出口】2
            print("获取鼠标平面坐标失败，无法进行自动化操作。")
            return -2
        cur_pos = tmp_cur_pos[1:]  # 鼠标当前位置
        self.op.LeftDown()  # 按下左键

        self.op.MoveTo(cur_pos[0], cur_pos[1])

        self.op.LeftUp()
        self.op.RightDown()
        self.op.RightUp()

    def auto_move_click(self):
        self.op.MoveTo(200, 200)
        self.op.LeftClick()
        r = self.op.SendString(self.send_hwnd, "Hello World!")
        print("SendString ret:", r)
        return 0

    def test_bkimage(self):
        cr = self.op.GetColor(30, 30)
        print("color of (30,30):", cr)
        ret = self.op.Capture(0, 0, 2000, 2000, "screen.bmp")
        print("op.Capture ret:", ret)
        r, x, y = self.op.FindPic(0, 0, 2000, 2000, "test.png", "000000", 0.6, 0)
        print("op.FindPic:", r, x, y)
        return 0

    def test_ocr(self):
        s = self.op.OcrAuto(0, 0, 100, 100, 0.9)
        print("ocr:", s)
        s = self.op.OcrEx(0, 0, 100, 100, "000000-020202", 0.9)
        print("OcrEx:", s)
        s = self.op.OcrAutoFromFile("screen.bmp", 0.95)
        print("OcrAutoFromFile:", s)
        return 0



#实例化Automation类，实现自动化
def run_automation():

    auto = Automation()
    auto.get_window_by_name(window_name)
    if auto.bind_window() != 0 :    #绑定窗口成功的前提下才自动游戏
        if auto.base_test():
            auto.auto_play(20)
    auto.clear_window() #脚本结束，释放窗口

if __name__ == "__main__":
    window_name = "1-主界面_20241102.png（2879×1799像素, 2.21MB）- 2345看图王 - 第1/12张 100% "
    window_name = "Naraka"        #NeacProtect  #Naraka
    code_control = CodeControl()
    game_info = GameInfo()
    UI_info = UIInfo()
    key_code = KeyCode()

    run_automation()