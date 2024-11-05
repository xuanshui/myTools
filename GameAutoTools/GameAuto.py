from ctypes import *
from win32com.client import Dispatch
from Settings_WuJie14X import *
# from Settings_Server import *

# 加载免注册dll
dll = windll.LoadLibrary(path_tools_dll)
# 调用setupW函数
result = dll.setupW(path_opx64_dll)

# 如果result不等于1,则执行失败
if result != 1:
    exit(0)
# 创建对象
op = Dispatch("op.opsoft")
# print version of op 打印op插件的版本
print(op.Ver())
print(op.GetPath())


class Point:
    # 平面坐标
    def __init__(self):
        self.X = -1
        self.Y = -1

    def set_pos(self, x, y):
        self.X = x
        self.Y = y

class Area:
    # 平面区域
    # 绝对坐标：X1左上角X坐标，Y1左上角Y坐标，X2右下角X坐标，Y2右下角Y坐标
    def __init__(self, hwnd_id):
        self.hwnd = hwnd_id
        self.X1 = -1  # 左上角X坐标
        self.Y1 = -1  # Y左上角Y坐标
        self.X2 = -1  # 右下角X坐标
        self.Y2 = -1  # 右下角Y坐标

    def set_area(self, x1, y1, x2, y2):
        self.X1 = x1  # 左上角X坐标
        self.Y1 = y1  # Y左上角Y坐标
        self.X2 = x2  # 右下角X坐标
        self.Y2 = y2  # 右下角Y坐标

class Area2:
    # 平面区域
    # X、Y指区域的起点，绝对坐标
    # W指区域的宽，H指区域的高，W、H不是绝对坐标位置，而是相对于X、Y的相对数值
    def __init__(self, hwnd_id):
        self.H = None
        self.W = None
        self.Y = None
        self.X = None
        self.hwnd = hwnd_id

    def set_area(self, x, y, w, h):
        self.X = x  # X坐标
        self.Y = y  # Y坐标
        self.W = w  # 相对于X的宽
        self.H = h  # 相对于Y的高


# OP的基础方法
class Automation:
    #初始化
    def __init__(self):
        # 创建com对象
        self.op = Dispatch("op.opsoft")
        self.hwnd = 0  # 窗口句柄
        self.send_hwnd = 0
        self.UI = game_info.UI_Err    #游戏的界面类型，-1为非法值表示未获取到界面信息
        self.real_screen_resolution = [1440,900]    #实际的屏幕分辨率，该参数可以修改
        self.ratio_screen = 2 #屏幕物理分辨率/窗口矩形分辨率 = 比例，该参数可以修改
        print("初始化成功init")

    # 基础设置
    def set_base(self):
        # 输出插件版本号
        print("op ver:", self.op.Ver())
        print("path:", self.op.GetPath())  # 获取全局路径
        self.op.SetShowErrorMsg(2)  # 设置是否弹出错误信息,默认是打开：0:关闭，1:显示为信息框，2:保存到文件,3:输出到标准输出

    def clear_window(self):
        self.op.UnBindWindow()

    #  r=self.op.WinExec("notepad",1); #运行可执行文件,0：隐藏，1：用最近的大小和位置显示,激活
    #  print("Exec notepad:",r);

    # 获取程序的窗口句柄
    # 非0：获取成功，返回窗口句柄。0：获取失败
    def get_window_by_name(self, cur_window_name):
        # 测试窗口接口
        self.hwnd = op.FindWindow("", cur_window_name)  # 通过窗口名称查找窗口句柄
        if self.hwnd != 0:
            print(f"找到窗口：{cur_window_name}，parent hwnd:{self.hwnd}")
            # print(self.op.GetClientRect(self.hwnd))
            # print(self.op.GetWindowRect(self.hwnd))
            print(self.op.GetClientSize(self.hwnd))
            if self.op.GetWindowRect(self.hwnd)[0] != 0 :
                self.real_screen_resolution = self.op.GetWindowRect(self.hwnd)[1:]  #获取实际的屏幕分辨率
                self.ratio_screen = int(UI_info.physical_screen_resolution[0] / self.real_screen_resolution[2])#获取比例
            send_hwnd = op.FindWindowEx(self.hwnd, "Edit", "")  # 通过父窗口找子窗口，从而进行字符串输入
            if send_hwnd != 0:
                print(f"找到子窗口child hwnd:{send_hwnd}")
            return self.hwnd
        else:
            print(f"未找到窗口：{cur_window_name}")
            return 0

    # 绑定窗口hwnd，方便后面进行后台操作、获取相对坐标位置
    # 返回值：1成功，0失败
    def bind_window(self):
        # 绑定指定的窗口,并指定这个窗口的屏幕颜色获取方式(normal前台),鼠标仿真模式(normal前台),
        # 键盘仿真模式(normal前台),以及模式设定(0/1:都一样).
        # 绑定窗口后，一定要记得释放窗口UnBindWindow()，否则游戏可能异常
        # 绑定之后,所有的坐标都相对于窗口的客户区坐标(不包含窗口边框)
        r = self.op.BindWindow(self.hwnd, "normal", "normal", "normal", 0)
        if r == 0:
            print(f"绑定窗口{window_name}失败。bind false")
        else:
            print(f"成功绑定窗口{window_name}")
        return r

    # 自动化操作
    def auto_play(self, range_r:int) -> int:
        #1、窗口激活，获取窗口4点坐标
        print(self.op.SetWindowState(self.hwnd,1))  #激活窗口，显示到前台
        tmp_area = self.op.GetWindowRect(self.hwnd) #返回5个参数，第一个是0（失败）或1（成功）
        if tmp_area[0] != 1 : #获取窗口4点坐标失败，直接退出
            #【出口】1
            print(f"获取窗口4点坐标失败，无法进行自动化操作。{tmp_area}")
            #return -1
        window_area = tmp_area[1:]  # 窗口的4点区域坐标
        print("窗口的4点区域坐标：", window_area)
        # 移动鼠标到区域的中间
        self.op.MoveTo((window_area[0] + window_area[2]) / 2, (window_area[1] + window_area[3]) / 2)

        #2、移动窗口到左上角
        # self.op.SetClientSize(self.hwnd, 0, 0)
        if self.op.MoveWindow(self.hwnd, 0, 0): #移动窗口到左上角
            print("移动窗口到左上角")
        else:
            print("移动窗口到左上角失败")

        #3、获取鼠标坐标
        tmp_cur_pos = self.op.GetCursorPos()  # 该函数返回了一个三元素的元组
        if tmp_cur_pos[0] != 1:  #获取鼠标平面坐标失败，直接退出
            # 【出口】2
            print(f"获取鼠标平面坐标失败，无法进行自动化操作。{tmp_cur_pos}")
            # return -2
        cur_pos = tmp_cur_pos[1:]  # 鼠标当前位置

        #4、主循环
        count = 0
        while count < code_control.loop_count:  #循环次数
            count += 1  #计数器自增
            #获取当面界面信息，频率：1次/秒
            self.UI = self.get_cur_UI()
            # 主界面
            if self.UI == game_info.UI_PVP_Main:
                print("进入主界面")

            # 选择英雄界面
            elif self.UI == game_info.UI_PVP_Select_Hero:
                pass
            # 选择跳点界面
            elif self.UI == game_info.UI_PVP_Select_Point:
                pass
            # 结算界面1
            elif self.UI == game_info.UI_PVP_Game_End1:
                pass
            # 结算界面2
            elif self.UI == game_info.UI_PVP_Game_End2:
                pass
            # 游戏内界面
            elif self.UI == game_info.UI_PVP_Game_in:
                pass
            # 非法界面
            else:
                #不是上面的界面，则认为是错误界面信息，重新获取界面类型
                pass
            #1-判断当前界面


    def get_cur_UI(self)->int:
        #是否为主界面：
        if self.get_area_text(UI_info.UI_main_area) == UI_info.UI_main_text1 or self.get_area_text(UI_info.UI_main_area) == UI_info.UI_main_text2:
            return game_info.UI_PVP_Main
        self.op.Sleep(code_control.OCR_sleep)
        #是否为英雄选择界面
        if self.get_area_text(UI_info.UI_select_hero_area) == UI_info.UI_select_hero_text:
            return game_info.UI_PVP_Select_Hero
        self.op.Sleep(code_control.OCR_sleep)
        # 是否为跳点选择界面：龙隐洞天/聚窟州
        if self.get_area_text(UI_info.UI_select_point_area) == UI_info.UI_select_point_text1 or self.get_area_text(UI_info.UI_select_point_area) == UI_info.UI_select_point_text2:
            return game_info.UI_PVP_Select_Point
        self.op.Sleep(code_control.OCR_sleep)
        # 是否为结算界面，两个结算画面的特征其实都一样，这里就返回UI_PVP_Game_End1
        if self.get_area_text(UI_info.UI_end_area1) == UI_info.UI_end_text1 or self.get_area_text(UI_info.UI_end_area2) == UI_info.UI_end_text2:
            return game_info.UI_PVP_Game_End1
        self.op.Sleep(code_control.OCR_sleep)
        # 是否为游戏内界面
        if self.get_area_text(UI_info.UI_game_area) == UI_info.UI_game_text:
            return game_info.UI_PVP_Game_in
        #不符合任何一个特征，就算错误
        return game_info.UI_Err

    #获取指定区域内的文字
    def get_area_text(self, area)->str:
        self.op.Sleep(code_control.OCR_sleep);
        #对指定区域area进行OCR文字识别
        text = self.op.OcrAuto(area[0]/self.ratio_screen, area[1]/self.ratio_screen, area[2]/self.ratio_screen,
                               area[3]/self.ratio_screen, code_control.OCR_sim)
        print(f"OCR识别：{text}")

        # ret = self.op.Capture(area[0]/self.ratio_screen, area[1]/self.ratio_screen, area[2]/self.ratio_screen,
        #                       area[3]/self.ratio_screen, "tmp_screen1.bmp")
        # if ret != 1:
        #     print("截图失败1")
        # ret = self.op.Capture(area[0], area[1], area[2],area[3], "tmp_screen2.bmp")
        # if ret != 1:
        #     print("截图失败2")
        # ret = self.op.Capture(0, 0, 10000, 10000, "tmp_screen3.bmp")
        # if ret != 1:
        #     print("截图失败3")
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
        self.op.Sleep(1000)
        self.op.MoveTo(cur_pos[0], cur_pos[1])
        self.op.Sleep(1000)
        self.op.LeftUp()
        self.op.RightDown()
        self.op.RightUp()

    def auto_move_click(self):
        self.op.MoveTo(200, 200)
        self.op.Sleep(200)
        self.op.LeftClick()
        self.op.Sleep(1000)
        r = self.op.SendString(self.send_hwnd, "Hello World!")
        print("SendString ret:", r)
        self.op.Sleep(1000)
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
    auto.set_base()
    auto.get_window_by_name(window_name)
    if auto.bind_window() != 0 :    #绑定窗口成功的前提下才自动游戏
        auto.auto_play(20)
    auto.clear_window() #脚本结束，释放窗口

if __name__ == "__main__":
    window_name = "1-主界面_20241102.png（2879×1799像素, 2.21MB）- 2345看图王 - 第1/12张 100% "
    code_control = CodeControl()
    game_info = GameInfo()
    UI_info = UIInfo()

    run_automation()