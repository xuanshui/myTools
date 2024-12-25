from win32com.client import Dispatch
import random   #实现随机数
from ctypes import windll
from Common import *

# PC_NAME = "ThinkBook16P"
# PC_NAME = "MyServer"
# PC_NAME = "WuJie14X"

#======================================================
PC_NAME = "ThinkBook16P"                    #当前所用的电脑
#======================================================

if PC_NAME == "MyServer":
    # 服务器
    path_tools_dll = "D:/code/Python/Tools/op-0.4.5_with_model/tools.dll"
    path_opx64_dll = "D:/code/Python/Tools/op-0.4.5_with_model/op_x64.dll"
    pass
elif PC_NAME == "WuJie14X":
    # 无界14
    path_tools_dll = "E:/Code/Python/Test/op-0.4.5_with_model/tools.dll"
    path_opx64_dll = "E:/Code/Python/Test/op-0.4.5_with_model/op_x64.dll"
elif PC_NAME == "ThinkBook16P":
    # ThinkBook16P
    path_tools_dll = "D:/Code/Python/Test/op-0.4.5_with_model/tools.dll"
    path_opx64_dll = "D:/Code/Python/Test/op-0.4.5_with_model/op_x64.dll"
else:
    print("path_tools_dll、path_opx64_dll路径为空！")
    exit(0)

# 游戏启动器的绝对路径
if PC_NAME == "MyServer":
    gameLauncherPath = "D:/EpicGame/NARAKABLADEPOINT/StartGame.exe" # 服务器

elif PC_NAME == "WuJie14X":
    gameLauncherPath = "D:/EpicGames/NARAKABLADEPOINT/StartGame.exe"  # 无界14

elif PC_NAME == "ThinkBook16P":
    gameLauncherPath = "D:/Programs/Naraka/program/StartGame.exe"  # ThinkBook16P

#——————————————————————————————————————————————————————————————————————————————————
#   宏定义
#——————————————————————————————————————————————————————————————————————————————————
# 下面是一些宏定义
WIN_STATE_CNT = 4           #监测的窗口状态数量
WIN_STATE_EXIST = 0        #窗口是否存在
WIN_STATE_RESPONSE = 1     #窗口是否能正常响应
WIN_STATE_ACTIVE = 2       #窗口是否激活
WIN_STATE_AREA_OK = 3       #窗口四维坐标是否

MOUSE_MOVE_ERR_RNG = 2      # isPosInAreaAbout函数的误差允许范围
#——————————————————————————————————————————————————————————————————————————————————
#   免注册调用OP插件
#——————————————————————————————————————————————————————————————————————————————————

#获取屏幕分辨率。要乘以缩放倍率。
DisplayScalingRatio = 1.0   #屏幕缩放：默认无缩放
ScreenResolution = (1920, 1080) #默认屏幕分辨率：1920×1080。后面有函数initOP()会获取实际的分辨率。

# 加载免注册dll
toolsDll = windll.LoadLibrary(path_tools_dll)
# 调用setupW函数
OPValid = False
if toolsDll.setupW(path_opx64_dll) != 1: # 如果setupW返回值不等于1,则执行失败
    OPValid = False
    logging.critical("\n\nOP插件免注册dll加载失败！一般是dll路径错误。脚本已退出。\n\n")
    exit(0)
#【关键】开启DPI感知。缩放比例不是100%，尤其是高分辨率屏幕必需打开。
# 如果不设置的话，当显示的缩放不是100%时，OP插件的各个函数无法正确识别整个屏幕，只能识别到左上角的一部分屏幕。
windll.user32.SetProcessDPIAware()

# 创建OP插件对象
OP = Dispatch("op.opsoft")
G_WorkPath = OP.GetPath()     # 全局工作路径


#——————————————————————————————————————————————————————————————————————————————————
#   参数设置
#——————————————————————————————————————————————————————————————————————————————————
# 键盘码值对应表
class OPKeyCode:
    #功能按键
    Backspace = 8
    Tab = 9
    Enter = 13
    Shift = 16
    Ctrl = 17
    Alt = 18
    Cap = 20
    ESC = 27
    Space = 32
    PageUp = 33
    PageDown = 34
    End = 35
    Home = 36
    Left = 37
    Up = 38
    Right = 39
    Down = 40
    Delete = 46
    Win = 91
    #数字按键 0-9
    Num0 = 48
    Num1 = 49
    Num2 = 50
    Num3 = 51
    Num4 = 52
    Num5 = 53
    Num6 = 54
    Num7 = 55
    Num8 = 56
    Num9 = 57
    #字母按键 a-z
    A = 65
    B = 66
    C = 67
    D = 68
    E = 69
    F = 70
    G = 71
    H = 72
    I = 73
    J = 74
    K = 75
    L = 76
    M = 77
    N = 78
    O = 79
    P = 80
    Q = 81
    R = 82
    S = 83
    T = 84
    U = 85
    V = 86
    W = 87
    X = 88
    Y = 89
    Z = 90
    #F区按键
    F1 = 112
    F2 = 113
    F3 = 114
    F4 = 115
    F5 = 116
    F6 = 117
    F7 = 118
    F8 = 119
    F9 = 120
    F10 = 121
    F11 = 122
    F12 = 123

# 时间相关的参数
class OPTime:
    #————————————————————休眠的时间——————————————————————————
    slp_cmd = 100  #各个普通操作之间的睡眠时间，100毫秒
    slp_OCR = 200     #每次进行OCR之前，休眠的时间
    slp_capture = 200 #每次截屏前，休眠的时间
    slp_findPic = 200 #每次查找图片前，休眠的时间
    slp_moveMouse = 100    #每次移动鼠标前，休眠的时间
    slp_click = 100  # 每次点击鼠标前，休眠的时间

    key_delay = 30  # 键盘按下和弹起之间的默认延时

# 数值、计数相关的参数
class OPVal:
    # =============================所有参数=========================================================
    # tuple_BindWin_display = ("normal", "normal.dxgi", "normal.wgc", "gdi", "gdi2",      # 0～4
    #                    "dx", "dx2", "dx.d3d9", "dx.d3d10", "dx.d3d11", "dx.d3d12",      # 5～10
    #                    "opengl", "opengl.std", "opengl.nox", "opengl.es", "opengl.fi")  # 11～15
    # tuple_BindWin_mouse = ("normal", "normal.hd", "windows", "dx")
    # tuple_BindWin_keypad = ("normal", "normal.hd", "windows")
    # tuple_BindWin_mode = (0, 1)
    #=============================================================================================
    tuple_BindWin_display = ("normal", "dx2", "gdi", "gdi2") #win11系统推荐："normal"，win10系统推荐："normal"
    tuple_BindWin_mouse = ("normal", "normal.hd")   # win11系统推荐："normal"，win10系统推荐："normal"
    tuple_BindWin_keypad = ("normal", "normal.hd")  # win11系统推荐："normal.hd"，win10系统推荐："normal.hd"
    tuple_BindWin_mode = (0, 1)                     #win11系统推荐："0"，win10系统推荐："0"

    #————————————————————绑定窗口参数——————————————————————————
    if PC_NAME == "MyServer":
        BindWin_display = tuple_BindWin_display[0]  # win10系统："normal"可以
        BindWin_mouse = tuple_BindWin_mouse[0]      # win10系统推荐："normal"
        BindWin_keypad = tuple_BindWin_keypad[1]    # win10系统推荐："normal.hd"
        BindWin_mode = tuple_BindWin_mode[0]        # "0"或者"1"好像没什么影响？

    elif PC_NAME == "ThinkBook16P":
        BindWin_display = tuple_BindWin_display[0]  # win11系统："normal"、"dx2"均可以。normal是前台模式。
        BindWin_mouse = tuple_BindWin_mouse[0]      # win11系统推荐："normal"
        BindWin_keypad = tuple_BindWin_keypad[1]    # win11系统推荐："normal.hd"
        BindWin_mode = tuple_BindWin_mode[0]        # "0"或者"1"好像没什么影响？
    else:
        BindWin_display = tuple_BindWin_display[0]
        BindWin_mouse = tuple_BindWin_mouse[0]
        BindWin_keypad = tuple_BindWin_keypad[1]
        BindWin_mode = tuple_BindWin_mode[0]


    #————————————————————窗口参数——————————————————————————
    DisplayScalingRatio = 2.00   #主显示器的缩放倍率，2.00就是200%（如果已经开启DPI感知，这个数据是用不到的。）
    areaTestRatio = (0, 0, 1280, 720)   #WindowOp.getRatio()的测试区域
    clientWindowPos_X = 0      # 设置Naraka窗口的左上角位置：X坐标
    clientWindowPos_Y = 0      # 设置Naraka窗口的左上角位置：Y坐标
    # clientWindowSize_X = 1280  # 设置Naraka窗口的尺寸：宽
    # clientWindowSize_Y = 720   # 设置Naraka窗口的尺寸：高
    clientWindowSize_X = 1280  # 设置Naraka窗口的尺寸：宽
    clientWindowSize_Y = 720  # 设置Naraka窗口的尺寸：高

    # ————————————————————相似度参数——————————————————————————
    sim_OCR = 0.8       #OCR的相似度,取值范围 0.1-1.0
    sim_findPic = 0.9       #查找图片的相似度,取值范围 0.1-1.0

    # OCR识别的相关参数
    color_format = "9f2e3f-000000"  # RGB单色识别

    # ————————————————————鼠标操作的参数——————————————————————————
    random_move_range_x = 10  # 随机移动鼠标时，随机范围，单位：像素点
    random_move_range_y = 10  # 随机移动鼠标时，随机范围，单位：像素点
    ratio_deviation = 2       # 利用鼠标的移动来获取坐标系倍率，所允许最大误差，单位像素点
    ratio_min = 0.1           # ratio合理范围的最小值
    ratio_max = 5.0           # ratio合理范围的最大值
    cntGetRatio = 5           # 最多尝试获取坐标系倍率的次数

    # ————————————————————其他——————————————————————————
    PicPathTestOcr = G_WorkPath + "\\Pic\\Test\\TestOcr.bmp"
    TextTestOcr = "Ocr识别测试"
    PicPathTestCapture_tmp = G_WorkPath + "\\Pic\\Test\\Delete_me_base_test_picHandle.bmp"
#——————————————————————————————————————————————————————————————————————————————————
#   调用本文件的脚本所适配的窗口的信息
#——————————————————————————————————————————————————————————————————————————————————


#——————————————————————————————————————————————————————————————————————————————————
#   基础设置：利用鼠标的移动来获取坐标倍数关系
#——————————————————————————————————————————————————————————————————————————————————

class BaseSet:
    # 初始化OP插件
    @staticmethod
    def initOP()->bool:
        logging.info(f"\n\n=================================OP插件初始化=================================")
        logging.info(f"当前机型：{PC_NAME}")
        global toolsDll, OP
        if toolsDll is None:
            # 加载免注册dll
            global OPValid
            toolsDll = windll.LoadLibrary(path_tools_dll)
            # 调用setupW函数
            OPValid = True
            if toolsDll.setupW(path_opx64_dll) != 1:  # 如果setupW返回值不等于1,则执行失败
                OPValid = False
                logging.critical("\n\nOP插件免注册dll加载失败！一般是dll路径错误。脚本已退出。\n\n")
                return False
            # 创建OP插件对象
            OP = Dispatch("op.opsoft")

        # 【关键】开启DPI感知。缩放比例不是100%，尤其是高分辨率屏幕必需打开。
        # 如果不设置的话，当显示的缩放不是100%时，OP插件的各个函数无法正确识别整个屏幕，只能识别到左上角的一部分屏幕。
        windll.user32.SetProcessDPIAware()

        # 获取屏幕分辨率。如果没有开启DPI感知，则要乘以缩放倍率。如果已经开启开启DPI感知，则直接获取即可。
        global DisplayScalingRatio, ScreenResolution
        DisplayScalingRatio = OPVal.DisplayScalingRatio  # 屏幕缩放200%
        # ScreenResolution0 = (int(windll.user32.GetSystemMetrics(0) * DisplayScalingRatio),
        #                     int(windll.user32.GetSystemMetrics(1) * DisplayScalingRatio))
        ScreenResolution = (windll.user32.GetSystemMetrics(0), windll.user32.GetSystemMetrics(1))

        # 设置OP对象的一些基础设定
        OP.SetKeypadDelay("normal", OPTime.key_delay)  # 键盘按下和弹起之间的默认延时
        OP.SetShowErrorMsg(2)  # 设置是否弹出错误信息,默认是打开：0:关闭，1:显示为信息框，2:保存到文件,3:输出到标准输出
        logging.info(f"OP插件版本：{OP.Ver()}")  # 输出插件版本号
        logging.info(f"OP插件工作目录：：{OP.GetPath()}")  # 获取全局路径

        return True

    # 基础测试。
    @staticmethod
    def base_test_all(hwnd: int, ratio:list[2])->bool:
        rlt = True  #默认成功
        # 鼠标功能测试
        OP.Sleep(OPTime.slp_cmd * 2)
        if BaseSet.base_test_mouse(hwnd, ratio):
            logging.info(f"BaseSet.base_test_mouse()鼠标功能测试成功！")
        else:
            logging.error(f"BaseSet.base_test_mouse()鼠标功能测试失败！")
            rlt = False
        # 键盘功能测试
        OP.Sleep(OPTime.slp_cmd * 2)
        if BaseSet.base_test_keypad():
            logging.info(f"BaseSet.base_test_keypad()键盘功能测试成功！")
        else:
            logging.error(f"BaseSet.base_test_keypad()键盘功能测试失败！")
            rlt = False
        # 截图与OCR功能测试
        OP.Sleep(OPTime.slp_cmd * 2)
        if BaseSet.base_test_picHandle():
            logging.info(f"BaseSet.base_test_picHandle()截图与OCR功能测试成功！")
        else:
            logging.error(f"BaseSet.base_test_picHandle()截图与OCR功能测试失败！")
            rlt = False
        # 窗口操作功能测试
        OP.Sleep(OPTime.slp_cmd * 2)
        if BaseSet.base_test_window(hwnd):
            logging.info(f"BaseSet.base_test_window()窗口操作功能测试成功！")
        else:
            logging.error(f"BaseSet.base_test_window()窗口操作功能测试失败！")
            rlt = False

        return rlt

    @staticmethod
    def base_test_mouse(hwnd: int, ratio:list[2])->bool:
        rlt = True
        tryCnt = 0
        while tryCnt < 10:
            rlt = True
            tryCnt += 1
            # 错误次数越多，休眠时间越长
            OP.Sleep(OPTime.slp_moveMouse * tryCnt)

            # 尝试获取鼠标坐标
            curPos = OP.GetCursorPos()
            if curPos[0] != 1:
                logging.error(f"GetCursorPos()获取鼠标平面坐标失败")
                rlt = False
                continue
            if curPos[1] > ScreenResolution[0] or curPos[2] > ScreenResolution[1]:
                logging.error(f"GetCursorPos()获取鼠标平面坐标为无效值（超出屏幕分辨率）。"
                              f"屏幕分辨率为{ScreenResolution}，程序获取的坐标为{curPos[1:]}")
                rlt = False
                continue

            #移动鼠标到(0,0)，再复原鼠标位置(这里其实不能正确还原，因为坐标系倍率还没有获取呢)
            OP.Sleep(OPTime.slp_moveMouse)
            if OP.MoveTo(0, 0) != 1 :
                logging.info(f"MoveTo()移动鼠标失败")
                rlt = False
                continue
            # OP.Sleep(OPTime.slp_moveMouse)
            # if OP.MoveTo(curPos[1], curPos[2]) != 1:
            #     logging.info(f"MoveTo()移动鼠标失败")
            #     rlt = False
            #     continue
            if rlt: # 鼠标基础测试通过，退出循环
                break
        if rlt:
            # 获取鼠标倍率ratio
            if not WindowOp.getRatio(hwnd, ratio):
                logging.error(f"获取坐标系倍率ratio失败！")
                rlt = False
        else:
            logging.error(f"base_test_mouse：鼠标基础测试不通过，无法调用函数getRatio获取坐标系倍率ratio")
        return rlt

    @staticmethod
    def base_test_keypad()->bool:
        rlt = True
        # 按下一次Win键，然后再按一次Win键：可以肉眼观察结果
        if OP.KeyPress(OPKeyCode.Win) != 1:
            logging.info(f"KeyPress测试失败")
            rlt = False
        OP.Sleep(OPTime.slp_cmd * 2)
        if OP.KeyPress(OPKeyCode.Win) != 1:
            logging.info(f"KeyPress测试失败")
            rlt = False
        return rlt


    @staticmethod
    def base_test_window(hwnd: int)->bool:
        rlt = True

        # OP.Sleep(OPTime.slp_cmd)
        # if OP.SetWindowSize(hwnd, 1280, 720) != 1:
        #     logging.error(f"SetWindowSize设置窗口尺寸失败")
        #     print(f"SetWindowSize设置窗口尺寸失败")
        #     rlt = False

        OP.Sleep(OPTime.slp_cmd)
        if OP.SetClientSize(hwnd, 1280, 720) != 1:
            logging.error(f"SetClientSize设置窗口尺寸失败")
            print(f"SetClientSize设置窗口尺寸失败")
            rlt = False

        clientRect = OP.GetClientRect(hwnd)
        if clientRect[0] != 1:
            logging.error(f"GetClientRect获取窗口坐标失败")
            rlt = False
        if clientRect[3] > ScreenResolution[0]or clientRect[4] > ScreenResolution[1]:
            logging.error(f"GetClientRect获取窗口坐标为无效值（超出屏幕分辨率）。屏幕分辨率为{ScreenResolution}，"
                          f"程序获取的client窗口坐标为{clientRect[1:]}")
            rlt = False

        windowRect = OP.GetWindowRect(hwnd)
        if windowRect[0] != 1:
            logging.error(f"GetWindowRect获取窗口坐标失败")
            rlt = False
        if windowRect[3] > ScreenResolution[0]or windowRect[4] > ScreenResolution[1]:
            logging.error(f"GetWindowRect获取窗口坐标为无效值（超出屏幕分辨率）。屏幕分辨率为{ScreenResolution}，"
                          f"程序获取的window窗口坐标为{windowRect[1:]}")
            rlt = False

        clientSize = OP.GetClientSize(hwnd)
        if clientSize[0] != 1:
            logging.error(f"GetClientSize获取窗口尺寸失败")
            rlt = False
        if clientSize[1] > ScreenResolution[0]or clientSize[2] > ScreenResolution[1]:
            logging.error(f"GetClientSize获取窗口尺寸为无效值（超出屏幕分辨率）。屏幕分辨率为{ScreenResolution}，"
                          f"程序获取的client窗口尺寸为{clientSize[1:]}")


        OP.Sleep(OPTime.slp_cmd)
        if OP.MoveWindow(hwnd, 0, 0) != 1:
            logging.error("MoveWindow移动窗口到[0,0]失败！")
            print("MoveWindow移动窗口到[0,0]失败！")
            rlt = False

        # isWindowActive0 = OP.GetWindowState(hwnd, 1)
        OP.Sleep(OPTime.slp_cmd)
        if OP.SetWindowState(hwnd, 12) != 1:  # 激活窗口
            OP.SetWindowState(hwnd, 7)
            logging.error(f"SetWindowState激活窗口失败！")
            rlt = False
        OP.Sleep(OPTime.slp_cmd)
        isWindowExist = OP.GetWindowState(hwnd, 0)
        if isWindowExist != 1: # 窗口理应存在
            logging.error(f"GetWindowState未能成功识别到窗口是否存在！")
            rlt = False
        # 判断窗口是否激活,存在BUG...
        # isWindowActive = OP.GetWindowState(hwnd, 1)
        # if isWindowActive != 1: # 激活窗口后，获取的窗口状态应该是“已激活”
        #     logging.error(f"GetWindowState未能成功识别到窗口是否激活！")
        #     rlt = False
        # 最小化窗口似乎也存在BUG，如果使用这个函数最小化，后面就没法激活和显示
        # OP.Sleep(OPTime.slp_cmd)
        # if OP.SetWindowState(hwnd, 2) != 1: #最小化窗口、不再激活窗口
        #     logging.error(f"SetWindowState最小化窗口失败！")
        #     rlt = False

        return rlt

    @staticmethod
    def base_test_picHandle()->bool:
        rlt = True

        OP.Sleep(OPTime.slp_capture)
        if OP.Capture(0, 0, 200, 200, OPVal.PicPathTestCapture_tmp) != 1:
            logging.error(f"Capture截屏失败！")
            rlt = False

        OP.Sleep(OPTime.slp_OCR)
        ocrRlt = OP.OcrFromFile(OPVal.PicPathTestOcr, OPVal.color_format, OPVal.sim_OCR)
        if OPVal.TextTestOcr != ocrRlt:
            logging.error(f"OcrFromFile识别文字失败！正确结果：{OPVal.TextTestOcr}，识别结果：{ocrRlt}")
            rlt = False

        return rlt


#——————————————————————————————————————————————————————————————————————————————————
#   获取屏幕信息：OCR、截图
#——————————————————————————————————————————————————————————————————————————————————
class GetScrInfo:
    #在整个屏幕截图中查找指定图片的位置，每次查找耗时约110ms
    @staticmethod
    def findPic(pic_name: str, areaClient:list[4], sim=OPVal.sim_findPic) -> list[4]:
        # area = WindowInfo.areaClient
        #有BUG，要么进行一次休眠，要么连续查找2次。否则会失败
        OP.Sleep(OPTime.slp_findPic)
        if not (0.1 < sim < 1):   #如果超出正常范围，设置为默认的相似度
            sim = OPVal.sim_findPic
        rlt = OP.FindPic(areaClient[0], areaClient[1],areaClient[2], areaClient[3],
                         pic_name, "000000", sim, 0)
        if rlt[0] != -1:
            pos = rlt[1:]
        else:
            pos = [-1, -1, -1, -1]
        return pos

    #获取指定区域内的文字：每次调用消耗时间：1035ms
    @staticmethod
    def ocrAreaText(area:list[4])->str:
        tmpPicName = "/Pic/tmpPic.bmp"
        OP.Sleep(OPTime.slp_capture)
        text = ""
        if GetScrInfo.captureArea(area, tmpPicName):
            OP.Sleep(OPTime.slp_OCR)
            #对指定区域area进行OCR文字识别
            text = OP.OcrFromFile(tmpPicName, OPVal.color_format, OPVal.sim_OCR)
            # text = OP.OcrAuto(area[0], area[1], area[2], area[3], OPVal.sim_OCR)
            # logging.info(f"get_area_text：OCR识别区域{area}：{text}。")
        return text

    # 对指定区域进行截图，如果截图成功则返回1，失败返回0：每次截图耗时约7ms～15ms
    @staticmethod
    def captureArea(area: list[4], picFullName: str) -> bool:
        OP.Sleep(OPTime.slp_capture)
        screenCapture = OP.Capture(area[0], area[1], area[2], area[3], picFullName)
        if screenCapture == 1:
            return True
        else:
            return False

    # 获取指定图片的文字：针对同一张图片，第一次调用耗时800ms，往后每次调用，耗时约30ms～40ms
    @staticmethod
    def ocrPicText(picPath:str) -> str:
        # 对指定区域area进行OCR文字识别
        text = OP.OcrFromFile(picPath, OPVal.color_format, OPVal.sim_OCR)
        if text != "":
            # logging.info(f"get_pic_area_text：OCR识别图片{picPath}成功：\n{text}")
            pass
        else:
            # logging.info(f"get_pic_area_text：OCR识别图片{picPath}失败。")
            pass
        return text



#——————————————————————————————————————————————————————————————————————————————————
#   窗口的相关操作
#——————————————————————————————————————————————————————————————————————————————————
class WindowOp:
    # 获取程序的窗口句柄
    # 输入：期望获取句柄多的窗口名称，比如Naraka
    # 输出：非0：获取成功，返回窗口句柄。0：获取失败
    @staticmethod
    def get_window_by_name(dstWindowName)->int:
        # 测试窗口接口
        hwnd = OP.FindWindow("", dstWindowName)  # 通过窗口名称查找窗口句柄
        if hwnd != 0:
            logging.info(f"找到窗口：{dstWindowName}，parent hwnd:{hwnd}")
            return hwnd
        # else:
        #     # # 如果没找到相应的窗口，最多尝试3次：启动这个程序
        #     # logging.error(f"未找到窗口：{dstWindowName}，尝试启动程序……")
        #     # restartGame()  # 启动程序
        #     # hwnd = OP.FindWindow("", dstWindowName)  # 通过窗口名称查找窗口句柄
        #     # if hwnd != 0:
        #     #     logging.info(f"找到窗口：{dstWindowName}，parent hwnd:{hwnd}")
        #     #     return hwnd
        #     # OP.Sleep(CodeControl.gameRestartWaitTime2)  # 每次尝试失败后，
        logging.error(f"未找到窗口：{dstWindowName}")
        return 0


    # 绑定窗口hwnd，方便后面进行后台操作、获取相对坐标位置
    # 返回值：1成功，0失败
    @staticmethod
    def bind_window(hwnd:int, ratio:list[2])->bool:
        # 绑定指定的窗口,并指定这个窗口的屏幕颜色获取方式(normal前台),鼠标仿真模式(normal前台),
        # 键盘仿真模式(normal前台),以及模式设定(0/1:都一样).
        # 绑定窗口后，一定要记得释放窗口UnBindWindow()，否则游戏可能异常
        # 绑定之后,所有的坐标都相对于窗口的客户区坐标(不包含窗口边框)
        # Naraka游戏中，
        # 屏幕显示：设置为normal，可以
        # 鼠标：设置为normal，可以
        # 键盘：必需设置为normal.hd才能进行输入
        # 模式：设置为0，可以
        logging.info(f"\n========================进入函数：bind_window========================")
        # 如果已经绑定过窗口，先解绑，再以新的方法绑定。
        if OP.IsBind():
            OP.UnBindWindow()
        logging.warning(f"绑定参数：BindWin_display：“{OPVal.BindWin_display}”，\tBindWin_mouse：“{OPVal.BindWin_mouse}”，"
            f"\tBindWin_keypad：“{OPVal.BindWin_keypad}”，\tBindWin_mode：“{OPVal.BindWin_mode}”")
        r = OP.BindWindow(hwnd, OPVal.BindWin_display, OPVal.BindWin_mouse, OPVal.BindWin_keypad, OPVal.BindWin_mode)
        if r == 0:
            logging.warning(f"绑定窗口{hwnd}失败。")
            return False
        tryCnt = 0
        while tryCnt < 10:
            tryCnt += 1
            OP.Sleep(OPTime.slp_cmd * tryCnt)  #休眠一下
            OP.SetWindowState(hwnd, 12)     #激活窗口，再进行后面的测试。
            OP.SetWindowState(hwnd, 7)
            if not BaseSet.base_test_all(hwnd, ratio):
                logging.info(f"第{tryCnt}次：绑定成功，但键鼠窗口等功能测试失败：\n【建议手动激活窗口，然后再运行脚本！】\n"
                    f"\tBindWin_display：“{OPVal.BindWin_display}”，\tBindWin_mouse：“{OPVal.BindWin_mouse}”， "
                    f"\tBindWin_keypad：“{OPVal.BindWin_keypad}”，\tBindWin_mode：“{OPVal.BindWin_mode}”")
                print(f"第{tryCnt}次：绑定成功，但键鼠窗口等功能测试失败：\n【建议手动激活窗口，然后再运行脚本！】\n"
                    f"\tBindWin_display：“{OPVal.BindWin_display}”，\tBindWin_mouse：“{OPVal.BindWin_mouse}”， "
                    f"\tBindWin_keypad：“{OPVal.BindWin_keypad}”，\tBindWin_mode：“{OPVal.BindWin_mode}”")
                OP.Sleep(1000)  # 休眠一下
                continue
            logging.info(f"第{tryCnt}次：成功绑定窗口{hwnd}，并通过基础测试。")
            print(f"第{tryCnt}次：\tBindWin_display：“{OPVal.BindWin_display}”，\tBindWin_mouse：“{OPVal.BindWin_mouse}”， "
                  f"\tBindWin_keypad：“{OPVal.BindWin_keypad}”，\tBindWin_mode：“{OPVal.BindWin_mode}”")
            return True
        return False

    # 尝试所有的组合
    @staticmethod
    def bind_window_try(hwnd: int, ratio:list[2]) -> bool:
        # 绑定指定的窗口,并指定这个窗口的屏幕颜色获取方式(normal前台),鼠标仿真模式(normal前台),
        # 键盘仿真模式(normal前台),以及模式设定(0/1:都一样).
        # 绑定窗口后，一定要记得释放窗口UnBindWindow()，否则游戏可能异常
        # 绑定之后,所有的坐标都相对于窗口的客户区坐标(不包含窗口边框)
        # Naraka游戏中，
        # 屏幕显示：设置为normal，可以
        # 鼠标：设置为normal，可以
        # 键盘：必需设置为normal.hd才能进行输入
        # 模式：设置为0，可以
        # r = OP.BindWindow(hwnd, "normal", "normal", "normal.hd", 0)
        # 组合总数： (16 * 4 * 3 * 2 = 384):
        cnt = 0  # 尝试绑定的总次数
        cntBind = 0  # OP.BindWindow绑定成功的总次数
        cntSucceed = 0  # 绑定成功并且键鼠窗口等测试也成功的次数
        for idxDisplay in range(0, len(OPVal.tuple_BindWin_display)):
            for idxMouse in range(0, len(OPVal.tuple_BindWin_mouse)):
                for idxKey in range(0, len(OPVal.tuple_BindWin_keypad)):
                    for idxMode in range(0, len(OPVal.tuple_BindWin_mode)):

                        cnt += 1

                        BindWin_display = OPVal.tuple_BindWin_display[idxDisplay]
                        BindWin_mouse = OPVal.tuple_BindWin_mouse[idxMouse]
                        BindWin_keypad = OPVal.tuple_BindWin_keypad[idxKey]
                        BindWin_mode = OPVal.tuple_BindWin_mode[idxMode]

                        # 如果已经绑定过窗口，先解绑，再以新的方法绑定。
                        if OP.IsBind():
                            OP.UnBindWindow()
                        logging.warning(
                            f"绑定参数：BindWin_display：“{BindWin_display}”，\tBindWin_mouse：“{BindWin_mouse}”， \t"
                            f"BindWin_keypad：“{BindWin_keypad}”，\tBindWin_mode：“{BindWin_mode}”")
                        r = OP.BindWindow(hwnd, BindWin_display, BindWin_mouse, BindWin_keypad, BindWin_mode)
                        if r == 0:
                            logging.warning(f"绑定窗口{hwnd}失败。")
                            # return False
                        else:
                            OP.Sleep(OPTime.slp_cmd * 5)  #休眠0.5秒
                            OP.SetWindowState(hwnd, 12)  # 激活窗口，再进行后面的测试。
                            OP.SetWindowState(hwnd, 7)
                            OP.Sleep(OPTime.slp_cmd * 5)  # 休眠0.5秒
                            if BaseSet.base_test_all(hwnd, ratio):
                                cntSucceed += 1
                                logging.info(
                                    f"第{cnt}次：成功绑定窗口{hwnd}，并通过基础测试。\nBindWin_display：“{BindWin_display}”，\tBindWin_mouse：“{BindWin_mouse}”， \t"
                                    f"BindWin_keypad：“{BindWin_keypad}”，\tBindWin_mode：“{BindWin_mode}”")
                                print(
                                    f"第{cnt}次：\tBindWin_display：“{BindWin_display}”，\tBindWin_mouse：“{BindWin_mouse}”， \t"
                                    f"BindWin_keypad：“{BindWin_keypad}”，\tBindWin_mode：“{BindWin_mode}”")
                                # return True
                            else:
                                cntBind += 1
                                print(
                                    f"第{cnt}次绑定成功，但键鼠窗口等功能测试失败：\tBindWin_display：“{BindWin_display}”，\tBindWin_mouse：“{BindWin_mouse}”， \t"
                                    f"BindWin_keypad：“{BindWin_keypad}”，\tBindWin_mode：“{BindWin_mode}”")
                                # OP.Sleep(OPTime.slp_cmd * 10)   # 每次失败就休眠1s
                            # return True
        print(f"尝试组合共{cnt}次，绑定成功{cntBind}次，完全成功{cntSucceed}次。")
        return False


    @staticmethod
    def unbind_window():
        OP.UnBindWindow()

    #返回值：True表示设置成功
    @staticmethod
    def update_window(hwnd:int,
                    windowArea:list[4],windowSize:list[2],
                    clientArea:list[4],clientSize:list[2],
                    clientAreaMidPoint:list[2],
                    windowStates:list[WIN_STATE_CNT])->bool:
        logging.info(f"\n========================进入函数：update_window========================")
        if windowStates[WIN_STATE_AREA_OK]:
            logging.info(f"窗口尺寸和坐标正常，无需调用update_window函数。")
            return True
        logging.info(f"窗口尺寸和坐标存在异常，update_window函数尝试进行修复。")
        OP.SetWindowState(hwnd, 12)  # 激活窗口，再进行后面的操作。
        OP.SetWindowState(hwnd, 7)

        # 注意：GetClientRect和GetWindowRect得到的尺寸是不一样的。Clien只包含游戏主界面，Window还包含更多。
        # 例如Naraka的“窗口化”模式，Window尺寸(0, 0, 1306, 791)，Client尺寸(0, 0, 1280, 720)
        # 例如Naraka的“无边框窗口”模式，Window尺寸(0, 0, 1282, 722)，Client尺寸(0, 0, 1280, 720)
        if OP.SetClientSize(hwnd, OPVal.clientWindowSize_X,
                                 OPVal.clientWindowSize_Y) != 1:
            # if OP.SetWindowSize(hwnd, OPVal.clientWindowSize_X,
            #                      OPVal.clientWindowSize_Y) != 1:
            logging.error(f"OP.SetClientSize设置窗口尺寸失败")
            return False
        OP.Sleep(OPTime.slp_cmd)
        if OP.MoveWindow(hwnd, OPVal.clientWindowPos_X, OPVal.clientWindowPos_Y) != 1 :
            logging.error("OP.MoveWindow移动窗口到[0,0]失败！")
            return False


        tmpClientArea = OP.GetClientRect(hwnd)
        tmpWindowArea = OP.GetWindowRect(hwnd)
        if tmpClientArea[0] != 1:
            logging.error(f"OP.GetClientRect获取client窗口尺寸失败")
            return False
        if not (
                (0 <= tmpClientArea[1] < tmpClientArea[3]) and
                (0 <= tmpClientArea[2] < tmpClientArea[4]) and
                (tmpClientArea[3] <= ScreenResolution[0]) and
                (tmpClientArea[4] <= ScreenResolution[1])
                ):
            logging.error(f"OP.GetClientRect获取client窗口尺寸为非法值："
                          f"{tmpClientArea}，超出了屏幕分辨率范围{ScreenResolution}")
            return False
        if tmpWindowArea[0] != 1:
            logging.error(f"OP.GetWindowRect获取window窗口尺寸失败")
            return False
        if not (
                (0 <= tmpWindowArea[1] < tmpWindowArea[3]) and
                (0 <= tmpWindowArea[2] < tmpWindowArea[4]) and
                (tmpWindowArea[3] <= ScreenResolution[0]) and
                (tmpWindowArea[4] <= ScreenResolution[1])
                ):
            logging.error(f"OP.GetWindowRect获取client窗口尺寸为非法值："
                          f"{tmpWindowArea}，超出了屏幕分辨率范围{ScreenResolution}")
            return False

        # #如果window尺寸等于client尺寸（没有误差），则认为游戏窗口是无边框窗口
        # if (clientSize[0]==windowSize[0]) and (clientSize[1]==windowSize[1]):
        #     isBorderlessWindow = True
        # else:
        #     isBorderlessWindow = False
        # # 设置窗口尺寸后，如果不是无边框窗口则需要重新移动窗口
        # #如果窗口是无边框窗口：直接返回成功，无需移动窗口
        # if isBorderlessWindow:
        #     return True
        # else:


        # 如果窗口是普通窗口（有边框）：分别向x、y方向多移动一些距离，才能使client真正到达左上角
        # 因为op插件给的函数时MoveWindow()不是MoveClient()
        # 如果移动到左上角，需要移动的多余像素点数量，分为x方向和y方向
        windowMoveX = abs(tmpClientArea[1] - tmpWindowArea[1])
        windowMoveY = abs(tmpClientArea[2] - tmpWindowArea[2])
        if OP.MoveWindow(hwnd, -windowMoveX, -windowMoveY):  # 移动窗口到左上角。Naraka的数据是x：-13，y：-58
            logging.info("移动窗口到左上角成功")
        else:
            logging.warning("移动窗口到左上角失败")

        # 获取移动到正确位置的坐标
        tmpClientArea = OP.GetClientRect(hwnd)
        tmpWindowArea = OP.GetWindowRect(hwnd)
        # 输出
        # clientArea = OP.GetClientRect(hwnd)[1:]
        # windowArea = OP.GetWindowRect(hwnd)[1:]
        clientArea[0] = tmpClientArea[1]
        clientArea[1] = tmpClientArea[2]
        clientArea[2] = tmpClientArea[3]
        clientArea[3] = tmpClientArea[4]
        windowArea[0] = tmpWindowArea[1]
        windowArea[1] = tmpWindowArea[2]
        windowArea[2] = tmpWindowArea[3]
        windowArea[3] = tmpWindowArea[4]
        logging.info(f"获取Client窗口坐标成功：{clientArea}")
        logging.info(f"获取Window窗口坐标成功：{windowArea}")
        logging.info(f"设置Client窗口尺寸成功：[{OPVal.clientWindowSize_X}, {OPVal.clientWindowSize_Y}]")

        clientSize[0] = OP.GetClientSize(hwnd)[1]
        clientSize[1] = OP.GetClientSize(hwnd)[2]
        windowSize[0] = abs(windowArea[2] - windowArea[0])
        windowSize[1] = abs(windowArea[3] - windowArea[1])

        # 获取窗口中心点坐标
        clientAreaMidPoint[0] = (clientArea[0] + clientArea[2]) / 2
        clientAreaMidPoint[1] = (clientArea[1] + clientArea[3]) / 2
        logging.info(f"client窗口中心点坐标：{clientAreaMidPoint}")

        # op插件的GetWindowState函数获取窗口是否处于激活状态
        if OP.GetWindowState(hwnd, 1) == 1:
            windowStates[WIN_STATE_ACTIVE] = True
        else:
            windowStates[WIN_STATE_ACTIVE] = False
        logging.info(f"client窗口是否激活：{windowStates[WIN_STATE_ACTIVE]}")
        logging.info(f"窗口尺寸和坐标已修复。")
        return True


# 利用鼠标的移动来获取坐标倍数关系
    @staticmethod
    def getRatio(hwnd:int, ratio:list[2], areaClient: list[4]=OPVal.areaTestRatio) -> bool:
        tryCnt = 0  # 坐标倍数调试次数
        ratioRlt = [-1, -1]
        OP.Sleep(OPTime.slp_cmd)  # 休眠一下
        OP.SetWindowState(hwnd, 12)  # 激活窗口，再进行后面的测试。
        OP.SetWindowState(hwnd, 7)
        while tryCnt < OPVal.cntGetRatio:
            ratioRlt = [-1, -1]
            ratio[0] = ratioRlt[0]
            ratio[1] = ratioRlt[1]
            tryCnt += 1
            # 思路：
            # 1、先获取客户端窗口的坐标，然后计算移动的目标点①：窗口四点的中间点。
            # 2、然后把使用op.MoveTo函数移动鼠标到目标点①，这时候再获取鼠标的实际位置点②。
            # 3、如果点②x坐标/点①x坐标=点②y坐标/点①y坐标 ，那么倍率Ratio=点②x坐标/点①x坐标
            # 4、验证Ratio正确性：计算对于op来说，目标点①所对应的实际目标点③：(③x坐标=①x坐标/Ratio,③y坐标=①y坐标/Ratio)
            # 再次使用op.MoveTo函数移动鼠标到点③，移动后立即判断当前鼠标位置点④和点①坐标是否相同？
            # 如果x、y坐标差值在2以内，就认为相同。返回坐标调试结果：True
            OP.Sleep(OPTime.slp_cmd * tryCnt)  # 先休眠100ms
            tmpArea = areaClient
            origin_pos = OP.GetCursorPos()  # 记录鼠标原位置

            if origin_pos[0] != 1:  # 获取鼠标平面坐标失败，直接退出
                logging.error(f"WindowOp.getRatio函数：GetCursorPos()获取鼠标平面坐标失败1:{origin_pos[1:]}")
                continue
            if origin_pos[1] > ScreenResolution[0] or origin_pos[2] > ScreenResolution[1]:
                logging.error(f"第{tryCnt}次：WindowOp.getRatio函数：GetCursorPos获取鼠标坐标为无效值（超出屏幕分辨率）。"
                              f"屏幕分辨率为{ScreenResolution}，"
                              f"程序获取的鼠标坐标为{origin_pos[1:]}")
                # 暂时这样处理吧
                continue
            logging.info(f"WindowOp.getRatio函数：GetCursorPos()获取鼠标平面坐标成功:{origin_pos[1:]}")
            # 移动鼠标的目的地：窗口的中间点。
            dstPoint1 = [int((tmpArea[0] + tmpArea[2]) / 2), int((tmpArea[1] + tmpArea[3]) / 2)]
            if OP.MoveTo(dstPoint1[0], dstPoint1[1]) != 1:
                logging.info(f"WindowOp.getRatio函数：MoveTo()移动鼠标失败")
                continue
            # 获取鼠标坐标
            tmp_cur_pos = OP.GetCursorPos()  # 该函数返回了一个三元素的元组
            if tmp_cur_pos[0] != 1:  # 获取鼠标平面坐标失败，直接退出
                logging.error(f"WindowOp.getRatio函数：GetCursorPos()获取鼠标平面坐标失败2:{tmp_cur_pos[1:]}")
                continue
            dstPoint2 = tmp_cur_pos[1:]  # 鼠标当前位置
            # 获取坐标倍率
            if dstPoint1[0] != 0 and dstPoint1[1] != 0:
                ratioX = abs(dstPoint2[0] / dstPoint1[0])
                ratioY = abs(dstPoint2[1] / dstPoint1[1])
                logging.info(f"坐标存在倍率关系，x坐标倍率：{ratioX}，y坐标倍率：{ratioY}。")
                ratioRlt = [ratioX, ratioY]
            else:
                logging.error(f"除数为0.移动鼠标到了原点(0, 0)。")
                continue
            # 验证坐标倍率：再次移动
            dstPoint3 = [int(dstPoint1[0] / ratioX), int(dstPoint1[1] / ratioY)]
            OP.MoveTo(dstPoint3[0], dstPoint3[1])
            # 如果按照倍率移动鼠标，能够移动到预期位置（允许误差：±2个像素点），就认为成功！
            dstPoint4 = OP.GetCursorPos()[1:]
            if ((abs(dstPoint4[0] - dstPoint1[0]) <= OPVal.ratio_deviation)
                    and (abs(dstPoint4[1] - dstPoint1[1]) <= OPVal.ratio_deviation)):
                OP.MoveTo(origin_pos[1] / ratioX, origin_pos[2] / ratioY)  # 恢复鼠标到原位置
                # logging.info(f"第{tryCnt}次调试，成功获取坐标倍率系数Ratio={ratioRlt}")
                ratioRlt = [ratioX, ratioY]

                # 如果ratio不在合法范围内，认为获取坐标系倍率失败
                if not ((OPVal.ratio_min <= ratioRlt[0] <= OPVal.ratio_max) and
                        (OPVal.ratio_min <= ratioRlt[1] <= OPVal.ratio_max)):
                    logging.error(f"第{tryCnt}次调试，获取坐标系倍率失败:{ratioRlt}，倍率范围非法。")
                    continue
                else:
                    logging.info(f"第{tryCnt}次调试，成功获取坐标倍率系数Ratio={ratioRlt}")
                    ratio[0] = ratioRlt[0]
                    ratio[1] = ratioRlt[1]
                    return True
        # 尝试多次后，仍然无法获得正确的坐标倍率：
        return False

#——————————————————————————————————————————————————————————————————————————————————
#   键盘的相关操作
#——————————————————————————————————————————————————————————————————————————————————
class KeyOp:
    # 按下键盘的某个键
    @staticmethod
    def PressKey(keyCode: int) -> bool:
        OP.Sleep(OPTime.slp_cmd/2)
        if OP.KeyPress(keyCode) == 1:
            # logging.info(f"PressKey点击一次{keyCode}键成功")
            return True
        logging.error(f"PressKey点击一次{keyCode}键失败")
        return False

    @staticmethod
    def HoldKey(keyCode: int, slpTime: int)->bool:
        OP.Sleep(OPTime.slp_cmd/2)
        if OP.KeyDown(keyCode) == 1:
            OP.Sleep(slpTime)
            if OP.KeyUp(keyCode) == 1:
                return True
        logging.error(f"HoldKey操作{keyCode}失败")
        return False

    # 同时按下两个键
    @staticmethod
    def HoldTwoKey(keyCode1: int, holdTime1, keyCode2: int, holdTime2: int):
        # 先按住keyCode1,然后按住keyCode2，再抬起keyCode2，再抬起keyCode1
        OP.Sleep(OPTime.slp_cmd / 2)
        if OP.KeyDown(keyCode1) == 1:
            OP.Sleep(OPTime.slp_cmd / 2)
            if OP.KeyDown(keyCode2) == 1:
                OP.Sleep(holdTime2)
                if OP.KeyUp(keyCode2) == 1:
                    OP.Sleep(holdTime1)
                    if OP.KeyUp(keyCode1) == 1:
                        return True
        logging.error(f"HoldKey操作{keyCode1}失败")
        return False

    # 检测到用户按下某个键，返回True
    @staticmethod
    def DetectKey(KeyCode:int):
        if OP.GetKeyState(KeyCode):
            return True
        else:
            return False

#判断一个点的坐标是否绝对在指定的区域内
def isPosInAreaAbsolute(point:list[2], area:list[4])->bool:
    # 点point的x坐标要比区域area左上角那一点的x坐标更大，点point的y坐标要比区域area左上角那一点的y坐标更大
    if point[0] >= area[0] and point[1] >= area[1]:
        # 点point的x坐标要比区域area右下角那一点的x坐标更小，点point的y坐标要比区域area右下角那一点的y坐标更小
        if point[0] <= area[2] and point[1] <= area[3]:
            return True
    return False
#判断一个点的坐标是否大概在指定的区域内。errRng是误差范围，默认为2个像素点
def isPosInAreaAbout(point:list[2], area:list[4], errRng:int = 1)->bool:
    # 点point的x坐标要比区域area左上角那一点的x坐标更大，点point的y坐标要比区域area左上角那一点的y坐标更大
    if (point[0] >= area[0] - errRng) and (point[1] >= area[1]- errRng):
        # 点point的x坐标要比区域area右下角那一点的x坐标更小，点point的y坐标要比区域area右下角那一点的y坐标更小
        if (point[0] <= area[2] + errRng) and (point[1] <= area[3] + errRng):
            return True
    return False
#——————————————————————————————————————————————————————————————————————————————————
#   鼠标的相关操作
#——————————————————————————————————————————————————————————————————————————————————
#移动鼠标到目标位置
class MouseOp:
    @staticmethod
    def MoveTo(dstPoint:list[2], ratio:list[2])->bool:
        OP.Sleep(OPTime.slp_moveMouse)
        if OP.MoveTo(dstPoint[0] / ratio[0], dstPoint[1] / ratio[1]) == 1:
            # logging.info(f"移动鼠标成功，目标地址：{dstPoint}")
            return True
        else:
            logging.warning(f"移动鼠标失败！目标位置：{dstPoint}，当前位置：{OP.GetCursorPos()[1:]}")
            return False

    #移动鼠标到目标位置附近范围的随机一个地方，随机的范围可以设置
    @staticmethod
    def MoveToRandom(dstPoint:list[2], ratio:list[2])->bool:
        OP.Sleep(OPTime.slp_moveMouse)
        newDstPoint = OP.MoveToEx(dstPoint[0] / ratio[0], dstPoint[1] / ratio[1],
                            OPVal.random_move_range_x, OPVal.random_move_range_y)
        if newDstPoint != "":
            # logging.info(f"移动鼠标成功，目标地址：({newDstPoint})")
            return True
        else:
            logging.warning(f"随机移动鼠标失败！目标位置：{dstPoint}附近随机范围，当前位置：{OP.GetCursorPos()[1:]}")
            return False

    # 移动鼠标到目标区域内的随机一个地方
    @staticmethod
    def MoveToAreaRandom(dstArea: list[4], ratio:list[2]) -> bool:
        OP.Sleep(OPTime.slp_moveMouse)
        randomX = random.randint(int(dstArea[0]),int(dstArea[2]))
        randomY = random.randint(int(dstArea[1]),int(dstArea[3]))
        newDstPoint = [randomX, randomY]
        # curDstPoint = OP.GetCursorPos()[1:]  # 移动前鼠标位置
        rlt = OP.MoveTo(newDstPoint[0] / ratio[0], newDstPoint[1] / ratio[1])
        curDstPoint2 = OP.GetCursorPos()[1:]  # 移动后鼠标位置
        if isPosInAreaAbout(curDstPoint2, dstArea, MOUSE_MOVE_ERR_RNG):
            if rlt != 0:
                # logging.info(f"移动鼠标成功，目标地址：({newDstPoint})")
                return True
            else:
                logging.warning(f"随机移动鼠标失败！目标区域：{dstArea}范围内随机位置，当前位置：{curDstPoint2}")
                return False
        else:
            logging.warning(f"随机移动鼠标超范围！目标区域：{dstArea}范围内随机位置，当前位置：{curDstPoint2}")
            return False


    #立即单击一下鼠标左键
    @staticmethod
    def LeftClickNow()->bool:
        OP.Sleep(OPTime.slp_click)
        if OP.LeftClick() == 1:
            # logging.info(f"点击鼠标左键成功，点击位置：{OP.GetCursorPos()[1:]}")
            return True
        else:
            logging.warning(f"点击鼠标左键失败")
            return False
    # 单击一下鼠标右键
    @staticmethod
    def RightClickNow() -> bool:
        OP.Sleep(OPTime.slp_click)
        if OP.RightClick() == 1:
            # logging.info(f"点击鼠标左键成功，点击位置：{OP.GetCursorPos()[1:]}")
            return True
        else:
            logging.warning(f"点击鼠标左键失败")
            return False

    #按下鼠标左键一段时间，然后抬起
    @staticmethod
    def LeftHoldNow(holdTime:int)->bool:
        OP.Sleep(OPTime.slp_click)
        if OP.LeftDown() == 1:
            OP.Sleep(holdTime)
            if OP.LeftUp() == 1:
                # logging.info(f"按下并抬起鼠标左键成功，点击位置：{OP.GetCursorPos()[1:]}")
                return True
            else:
                logging.warning(f"抬起鼠标左键失败")
                return False
        else:
            logging.warning(f"按下鼠标左键失败")
            return False


    # 按下鼠标右键一段时间，然后抬起
    @staticmethod
    def RightHoldNow(holdTime: int) -> bool:
        OP.Sleep(OPTime.slp_click)
        if OP.RightDown() == 1:
            OP.Sleep(holdTime)
            if OP.RightUp() == 1:
                # logging.info(f"按下并抬起鼠标右键成功，点击位置：{OP.GetCursorPos()[1:]}")
                return True
            else:
                logging.warning(f"抬起鼠标右 键失败")
                return False
        else:
            logging.warning(f"按下鼠标右键失败")
            return False


    # 鼠标左键点击某个点
    @staticmethod
    def LeftClickPoint(point:list[2], ratio:list[2])->bool:
        if not MouseOp.MoveTo(point, ratio):
            return False
        if not MouseOp.LeftClickNow():
            return False
        return True

    # 鼠标左键点击某个区域内的随机一点
    @staticmethod
    def LeftClickAreaRandom(area: list[4], ratio:list[2]) -> bool:
        if not MouseOp.MoveToAreaRandom(area, ratio):
            return False
        if not MouseOp.LeftClickNow():
            return False
        return True

    # 鼠标右键点击某个点
    @staticmethod
    def RightClickPoint(point: list[2], ratio: list[2]) -> bool:
        if not MouseOp.MoveTo(point, ratio):
            return False
        if not MouseOp.RightClickNow():
            return False
        return True

    # 鼠标右键点击某个区域内的随机一点
    @staticmethod
    def RightClickAreaRandom(area: list[4], ratio: list[2]) -> bool:
        if not MouseOp.MoveToAreaRandom(area, ratio):
            return False
        if not MouseOp.RightClickNow():
            return False
        return True

    # 鼠标左键按住指定的点
    @staticmethod
    def LeftHoldPoint(point: list[2], holdTime:int, ratio: list[2])->bool:
        if not MouseOp.MoveTo(point, ratio):
            return False
        if not MouseOp.LeftHoldNow(holdTime):
            return False
        return True

    # 鼠标右键按住指定的点
    @staticmethod
    def RightHoldPoint(point: list[2], holdTime: int, ratio: list[2]) -> bool:
        if not MouseOp.MoveTo(point, ratio):
            return False
        if not MouseOp.RightHoldNow(holdTime):
            return False
        return True
