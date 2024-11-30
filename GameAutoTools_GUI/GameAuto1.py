import re       #正则表达式
from datetime import datetime, timedelta    #获取时间
from Settings_Server import *
from FaultMonitor import *
from OPFuncs import *


# OP的基础方法
class Automation:
    #初始化
    def __init__(self):

        #——————————窗口相关的属性——————————
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
        self.clientAreaMidPoint = [-1, -1]    #

        self.ratio = [-1, -1]         # 坐标系的x、y倍率。只要屏幕存在缩放，那么倍率就不会为1

        # ——————————周期相关的属性——————————
        self.pcsCnt = 0         #【？】 主循环的次数
        self.errUICnt = 0  # 进入脚本认为可以跳过的界面（错误界面errUI）的次数
        self.battleCnt = 0 # 进入局内战斗界面的次数
        self.gameCnt = 0  # 游戏次数
        self.gameTimeStart = datetime.now() #时间起点
        self.gameTimeLeftStr = ""   # 本局游戏还剩余的时间：游戏右上角显示，这里是字符串。
        self.gameTimeLeftS = 0  # 本局游戏还剩余的时间：游戏右上角显示，这里的时间单位是秒
        self.gameTimeEnd = 0  # 本局游戏应该在什么时间结束，即当前时间+游戏剩余时间
        self.gameTimeUsed = -1   # 本局游戏已用时间，单位秒
        self.EXP = 0  # 脚本本次运行所获取的所有经验值

        self.UI = GameInfo.UI_Err_Other    #游戏的界面类型，-1为非法值表示未获取到界面信息
        self.UI_valid = GameInfo.UI_Err_Other    #游戏的有效界面类型，-1为非法值表示未获取到界面信息

        self.curHero = ""   #当前选择的英雄

        # ——————————不同界面对应的处理方法——————————
        self.dict_UIHandle = {
            #错误界面
            GameInfo.UI_Err_Other: self.Handle_Err_UI,  # 每个周期交替输入ESC、空格
            GameInfo.UI_Err_Main_LoseServerConnect: self.Handle_Err_UI,  # 后续实现，重启游戏
            GameInfo.UI_Err_LogIn_AccountError: self.Handle_Err_UI,  # 后续实现，重启游戏

            #游戏内界面
            #===无尽试炼===
            GameInfo.UI_PVP_Game_In_WJSL: self.Handle_Game_In_WJSL,
            # ===PVE：雪满弓刀===
            GameInfo.UI_PVE_Game_In_1_W:self.Handle_PVE_Game_In_1_W,
            GameInfo.UI_PVE_Game_In_2_E: self.Handle_PVE_Game_In_2_E,
            GameInfo.UI_PVE_Game_In_3_ESC: self.Handle_PVE_Game_In_3_ESC,
            GameInfo.UI_PVE_Game_In_4_Battle: self.Handle_PVE_Game_In_4_Battle,
            GameInfo.UI_PVE_Game_In_5_Succeed: self.Handle_PVE_Game_In_5_Succeed,

            #登录界面
            GameInfo.UI_LogIn_Announcement:self.Handle_LogIn_Announcement,
            GameInfo.UI_LogIn_AgeRatingReminder:self.Handle_LogIn_AgeRatingReminder,

            #主界面
            # ===无尽试炼===
            GameInfo.UI_PVP_Main_Prepare: self.Handle_PVP_Main_Prepare,
            GameInfo.UI_PVP_Main_Entering: self.Handle_PVP_Main_Entering,
            # ===PVE：雪满弓刀===
            GameInfo.UI_PVE_Main_Prepare: self.Handle_PVE_Main_Prepare,
            GameInfo.UI_PVE_Main_Sure: self.Handle_PVE_Main_Sure,
            # 通用界面
            GameInfo.UI_Daily_Msg: self.Handle_Daily_Msg,

            #选择界面：PVP
            GameInfo.UI_PVP_Select_Hero: self.Handle_PVP_Select_Hero,
            GameInfo.UI_PVP_Select_Point: self.Handle_PVP_Select_Point,
            #选择界面：PVE：雪满弓刀
            GameInfo.UI_PVE_Select_Hero: self.Handle_PVE_Select_Hero,

            #结算界面：无尽试炼
            GameInfo.UI_PVP_Game_End_WJSL_1: self.Handle_PVP_Game_End_WJSL_1,
            GameInfo.UI_PVP_Game_End_WJSL_2: self.Handle_PVP_Game_End_WJSL_2,
            GameInfo.UI_PVP_Game_End_WJSL_3: self.Handle_PVP_Game_End_WJSL_3,
            GameInfo.UI_PVP_Game_End_WJSL_4: self.Handle_PVP_Game_End_WJSL_4,
            GameInfo.UI_PVP_Game_End_WJSL_5: self.Handle_PVP_Game_End_WJSL_5,
            #结算界面：PVE：雪满弓刀
            GameInfo.UI_PVE_Game_End_1:self.Handle_PVE_Game_End_1,
            GameInfo.UI_PVE_Game_End_2: self.Handle_PVE_Game_End_2,
            GameInfo.UI_PVE_Game_End_3: self.Handle_PVE_Game_End_3,
            GameInfo.UI_PVE_Game_End_4: self.Handle_PVE_Game_End_4,
            GameInfo.UI_PVE_Game_End_5: self.Handle_PVE_Game_End_5,
            GameInfo.UI_PVE_Game_End_6: self.Handle_PVE_Game_End_6,

            #ESC选择界面
            GameInfo.UI_ESC_Selection_OutGame: self.Handle_ESC_Selection,

            #过渡界面
            GameInfo.UI_Transition: self.Handle_Transition,

        }

    # 游戏启动后，重新获取窗口句柄hwnd、坐标系倍率ratio、窗口信息
    def initSelf(self) -> bool:
        # 重新调用一遍，初始化类的属性
        self.__init__()

        # 【1】如果OP绑定过窗口，解绑OP对象之前绑定的窗口
        if OP.IsBind() == 1:
            OP.UnBindWindow()

        # 【2】初始化OP对象
        if not BaseSet.initOP():  # 初始化失败，直接退出。
            print(f"OP插件免注册操作失败！脚本已退出。\n"
                  f"请检查OP插件的2个dll路径：\n{path_tools_dll}\n{path_opx64_dll}\n是否正确")
            exit(0)

        # 【3】获取窗口句柄
        self.hwnd = WindowOp.get_window_by_name(GameInfo.windowName_game)
        if self.hwnd == 0:
            logging.error(f"未找到窗口“{GameInfo.windowName_game}”")
            return False

        # 【4】绑定窗口句柄到OP对象、获取坐标系倍率
        if not WindowOp.bind_window(self.hwnd, self.ratio):
            logging.error(f"绑定窗口失败")
            print(f"绑定窗口失败，或获取坐标系倍率{self.ratio}失败")
            return False

        # 【5】恢复窗口设置
        # 先初始化窗口
        WindowOp.update_window(self.hwnd,
                               self.windowArea, self.windowSize,
                               self.clientArea, self.clientSize,
                               self.clientAreaMidPoint,
                               self.windowStates)
        # 再判断窗口状态
        if not self.updateWindowState():
            self.recoverWindowState()

        return True


    # 自动化操作：无尽试炼
    def auto_play(self):
        #1、窗口激活
        if OP.SetWindowState(self.hwnd, 12) == 1:  #激活窗口，显示到前台
            OP.SetWindowState(self.hwnd, 7)
            logging.info(f"激活窗口成功")
        else:
            logging.error(f"激活窗口失败")

        #2、主循环
        self.pcsCnt = 0       #周期计数清零

        while True:
            self.pcsCnt += 1  #计数器自增
            OP.Sleep(ParamTime.sleep_main_cycle)# 周期固定休眠时间

            isUINormal = False   # 默认界面为异常，只有非过渡界面才认为是正常的

            # 获取当前的UI界面
            time1 = datetime.now()
            self.UI = self.getCurUI()
            time2 = datetime.now()
            time_UI_Recognition = (time2 - time1).total_seconds()
            if time_UI_Recognition < 0.1:   # 如果识别界面消耗的时间太短了，主动休眠一段时间。
                OP.Sleep(ParamTime.slp_cmd * 2)
            logging.info(f"周期计数：{self.pcsCnt}，本次界面识别耗时：{time_UI_Recognition:.6f}秒")

            if self.UI != GameInfo.UI_Transition:
                # 非过渡界面，才认为是有效界面
                self.UI_valid = self.UI
                isUINormal = True

            # 错误界面监控
            pSelfCheck(isUINormal, PscRltAll[FAULT_TRANSITION_UI], PscCfgAll[FAULT_TRANSITION_UI])
            # 如果错误界面达到故障次数，调用故障处理函数
            if not PscRltAll[FAULT_TRANSITION_UI].reportRlt:
                self.Handle_Err_UI()

            # 利用字典，根据响应的UI直接调用对应的处理函数
            self.dict_UIHandle.get(self.UI)()  # `()` 是用来调用函数的
            # self.dict_UIHandle.get(self.UI, self.Handle_Err_UI())()  # `()` 是用来调用函数的

    # 获取当前的界面类型：主要分2大类，游戏内，游戏外。
    # 游戏内，需要做到快速响应。游戏外，需要做到精准识别。
    def getCurUI(self) -> int:

        # ————————————游戏内界面(无尽试炼模式)-非返魂-识别————————————
        # ===无尽试炼===
        if GAME_MODE_CUR == GAME_MODE_PVP_WJSL:
            # 如果游戏局内时间超过XX秒，直接返回当前界面为游戏内界面。游戏内，每隔N个周期更新游戏剩余时间
            if self.gameTimeLeftS >= ParamTime.default_InGame_LefTimeS_MAX:
                return GameInfo.UI_PVP_Game_In_WJSL

            # 是否为游戏内界面，未死亡：特征1，左上角的“排名”，无尽试炼特有：特征2，护甲粉末，特征3，凝血丸（因为无尽试炼出生就有）
            OP.Sleep(ParamTime.slp_OCR)
            # 如果OCR识别到“排名”，认为是在游戏内
            if WinInfo.Text_Char_Game_In_WJSL_1 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_In_WJSL_1):
                logging.info(f"getCurUI：OCR识别到进入游戏内界面，特征字：{WinInfo.Text_Char_Game_In_WJSL_1}")
                return GameInfo.UI_PVP_Game_In_WJSL

            # 通过查找屏幕截图中是否存在特征图片护甲粉末ArmorPowder1.bmp，来判断是否为游戏内界面
            OP.Sleep(ParamTime.slp_findPic )
            # 找到图片：ArmorPowder
            findPicRlt = GetScrInfo.findPic(WinInfo.Pic_Char_Game_In_WJSL_Powder1, self.clientArea)
            if findPicRlt[0] != -1:
                logging.info(f"getCurUI：找到图片ArmorPowder2.bmp左上角坐标：{findPicRlt[1:]}：此时处于游戏内界面")
                return GameInfo.UI_PVP_Game_In_WJSL

            # #通过查找屏幕截图中是否存在特征图片凝血丸BloodPill1.bmp，来判断是否为游戏内界面
            OP.Sleep(ParamTime.slp_findPic)
            # 找到图片：BloodPill
            findPicRlt = GetScrInfo.findPic(WinInfo.Pic_Char_Game_In_WJSL_Pill1, self.clientArea)
            if findPicRlt[0] != -1:
                logging.info(f"getCurUI：找到图片BloodPill2.bmp左上角坐标：{findPicRlt[1:]}：此时处于游戏内界面")
                return GameInfo.UI_PVP_Game_In_WJSL
        # ===PVE征神，雪满弓刀===
        elif GAME_MODE_CUR == GAME_MODE_PVE_XMGD:
            # 游戏内界面4-战斗界面：如果游戏使用时间未满70秒，直接返回当前界面为游戏内界面-战斗界面。
            if 0 < self.gameTimeUsed < ParamTime.default_InGame_TimeUsed_PVE_XMGD:
                logging.info(f"本局游戏已用{self.gameTimeUsed:.2f}秒，"
                             f"不满{ParamTime.default_InGame_TimeUsed_PVE_XMGD}秒，直接判定当前界面为游戏内战斗界面。")
                return GameInfo.UI_PVE_Game_In_4_Battle
            # # 前提：上一个有效界面是游戏内界面3-到达传送点或游戏内界面4-战斗界面
            # if self.UI_valid == GameInfo.UI_PVE_Game_In_4_Battle or self.UI_valid == GameInfo.UI_PVE_Game_In_3_ESC:
            # 界面入口-2】局内战斗界面-通关暂未成功
            # 如果OCR识别到“昆仑主母”
            if WinInfo.Text_Char_Game_in_PVE_4 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_in_PVE_4):
                logging.info(
                    f"getCurUI：OCR识别到进入游戏内界面4-战斗界面，特征字：{WinInfo.Text_Char_Game_in_PVE_4}")
                return GameInfo.UI_PVE_Game_In_4_Battle
            # 游戏内界面1-未到达传送点，长按W前往传送点
            # 前提：上一个有效界面是英雄选择界面 或 自己
            if self.UI_valid == GameInfo.UI_PVE_Select_Hero or self.UI_valid == GameInfo.UI_PVE_Game_In_1_W:
                # 如果OCR识别到“势比登天”
                if WinInfo.Text_Char_Game_In_PVE_1 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_In_PVE_1):
                    logging.info(f"getCurUI：OCR识别到进入游戏内界面1-未传送，特征字：{WinInfo.Text_Char_Game_In_PVE_1}")
                    return GameInfo.UI_PVE_Game_In_1_W
            # # 游戏内界面2-到达传送点，可以E传送
            # # 前提：上一个有效界面是游戏内界面1-未传送
            # if self.UI_valid == GameInfo.UI_PVE_Game_In_1_W:
            #     findPicRlt = GetScrInfo.findPic(WinInfo.Pic_Char_Game_In_PVE_2, self.clientArea)
            #     if findPicRlt[0] != -1:
            #         logging.info(f"getCurUI：找到“E传送”图片左上角坐标：{findPicRlt}：此时处于游戏内界面2-到达传送点")
            #         return GameInfo.UI_PVE_Game_In_2_E
            # 游戏内界面3-传送后出现的过渡动画，可以ESC跳过
            # 前提：上一个有效界面是游戏内界面2-到达传送点
            if self.UI_valid == GameInfo.UI_PVE_Game_In_1_W or self.UI_valid == GameInfo.UI_PVE_Game_In_3_ESC:
                # 如果OCR识别到“跳过”
                if WinInfo.Text_Char_Game_in_PVE_3 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_in_PVE_3):
                    logging.info(
                        f"getCurUI：OCR识别到进入游戏内界面3-过渡动画，特征字：{WinInfo.Text_Char_Game_in_PVE_3}")
                    return GameInfo.UI_PVE_Game_In_3_ESC
            # 游戏内界面5-通关成功，可以ESC返回大厅
            # 前提：上一个有效界面是游戏内界面4-战斗界面
            if self.UI_valid == GameInfo.UI_PVE_Game_In_4_Battle or self.UI_valid == GameInfo.UI_PVE_Game_In_5_Succeed:
                # 如果OCR识别到“通关成功”
                if WinInfo.Text_Char_Game_in_PVE_5 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_in_PVE_5):
                    logging.info(
                        f"getCurUI：OCR识别到进入游戏内界面5-通关成功，特征字：{WinInfo.Text_Char_Game_in_PVE_5}")
                    return GameInfo.UI_PVE_Game_In_5_Succeed

        # ————————————游戏内界面-返魂-识别————————————
        # 无尽试炼没有这一项内容。正常排位/人机模式才有。
        # # 是否为游戏内界面，已死亡待返魂：特征：中间:有“进入返魂坛复活”的字样
        # OP.Sleep(ParamTime.slp_cmd)
        # if self.captureArea(UI_info.UI_game_dad, picFullName):  # 如果截图指成功
        #     OP.Sleep(code_control.OCR_sleep)
        #     if self.ocrPicText(picFullName) == UI_info.UI_game_dad_text:
        #         logging.info(f"getCurUI：OCR识别到进入游戏内界面：已死亡，待返魂")
        #         return game_info.UI_PVP_Game_dad
        # else:
        #     logging.error(f"captureArea：截图区域{UI_info.UI_game_dad}失败。")


        # ————————————游戏结算界面识别————————————
        # ===无尽试炼===
        if GAME_MODE_CUR == GAME_MODE_PVP_WJSL:
            # 结算界面1：“前三甲”。游戏会自动跳过该界面，脚本可以不用识别。
            # 是否为结算界面1：战斗前三甲？
            OP.Sleep(ParamTime.slp_OCR)
            # OCR识别："战斗前三甲"
            if WinInfo.Text_Char_WJSL_End_1 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_WJSL_End_1):
                logging.info(f"getCurUI：OCR识别到进入结算界面1：战斗前三甲")
                return GameInfo.UI_PVP_Game_End_WJSL_1

            # 是否为结算界面2：积分榜？
            OP.Sleep(ParamTime.slp_OCR)
            # OCR识别："返回大厅"
            if WinInfo.Text_Char_WJSL_End_2 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_WJSL_End_2):
                logging.info(f"getCurUI：OCR识别到进入结算界面2：积分榜")
                return GameInfo.UI_PVP_Game_End_WJSL_2

            # 是否为结算界面3：无尽试炼等阶？
            OP.Sleep(ParamTime.slp_OCR)
            # OCR识别："试炼"
            if WinInfo.Text_Char_WJSL_End_3 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_WJSL_End_3):
                logging.info(f"getCurUI：OCR识别到进入结算界面3：无尽试炼等阶")
                return GameInfo.UI_PVP_Game_End_WJSL_3

            # 当前界面是否为结算界面4-通行证经验值界面？下面两个方式都可以认为是经验结算界面
            OP.Sleep(ParamTime.slp_OCR)
            # OCR识别："恭喜获得"
            if WinInfo.Text_Char_WJSL_End_4 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_WJSL_End_4):
                logging.info(f"getCurUI：OCR识别到进入结算界面4：通行证经验")
                return GameInfo.UI_PVP_Game_End_WJSL_4

            # 当前界面是否为结算界面5-游戏等级经验，没什么用。
            OP.Sleep(ParamTime.slp_OCR)
            # OCR识别："等级"
            if WinInfo.Text_Char_WJSL_End_5 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_WJSL_End_5):
                logging.info(f"getCurUI：OCR识别到进入结算界面5：游戏等级经验")
                return GameInfo.UI_PVP_Game_End_WJSL_5
        # ===PVE征神，雪满弓刀===
        elif GAME_MODE_CUR == GAME_MODE_PVE_XMGD:
            # 结算界面1：伤害/用时
            # # OCR识别到"胜利"，且上一个界面为游戏内成功通关
            # if self.UI_valid == GameInfo.UI_PVE_Game_In_5_Succeed:
            if WinInfo.Text_Char_XMGD_End_1 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_XMGD_End_1):
                OP.Sleep(ParamTime.slp_OCR)
                if not WinInfo.Text_Char_XMGD_End_2 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_XMGD_End_2):
                    logging.info(f"getCurUI：OCR识别到进入结算界面1：伤害/用时")
                    return GameInfo.UI_PVE_Game_End_1

            # 是否为结算界面2：各类经验
            # OCR识别："战斗奖励"，且上一个界面为结算界面1
            if self.UI_valid == GameInfo.UI_PVE_Game_End_1 or self.UI_valid == GameInfo.UI_PVE_Game_End_2:
                if WinInfo.Text_Char_XMGD_End_2 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_XMGD_End_2):
                    logging.info(f"getCurUI：OCR识别到进入结算界面2：各类经验")
                    return GameInfo.UI_PVE_Game_End_2

            # 是否为结算界面3：用户等级
            # OCR识别："等级"，且上一个界面为结算界面2
            if self.UI_valid == GameInfo.UI_PVE_Game_End_2 or self.UI_valid == GameInfo.UI_PVE_Game_End_3:
                if WinInfo.Text_Char_XMGD_End_3 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_XMGD_End_3):
                    logging.info(f"getCurUI：OCR识别到进入结算界面3：用户等级")
                    return GameInfo.UI_PVE_Game_End_3

            # 是否为结算界面4-潜能等级
            # OCR识别："潜能等级"，且上一个界面为结算界面3
            if self.UI_valid == GameInfo.UI_PVE_Game_End_3 or self.UI_valid == GameInfo.UI_PVE_Game_End_4:
                if WinInfo.Text_Char_XMGD_End_4 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_XMGD_End_4):
                    logging.info(f"getCurUI：OCR识别到进入结算界面3：潜能等级")
                    return GameInfo.UI_PVE_Game_End_4

            # 是否为结算界面5-恭喜获得，不一定会出现。
            # OCR识别："返回"，且上一个界面为结算界面
            if GameInfo.UI_PVE_Game_End_1 <= self.UI_valid <= GameInfo.UI_PVE_Game_End_4:
                if WinInfo.Text_Char_XMGD_End_5 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_XMGD_End_5):
                    logging.info(f"getCurUI：OCR识别到进入结算界面5-恭喜获得")
                    return GameInfo.UI_PVE_Game_End_5

            # 是否为结算界面6-恭喜获得，不一定会出现。
            # OCR识别："获得"，且上一个界面为结算界面
            if GameInfo.UI_PVE_Game_End_1 <= self.UI_valid <= GameInfo.UI_PVE_Game_End_5:
                if WinInfo.Text_Char_XMGD_End_6 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_XMGD_End_6):
                    logging.info(f"getCurUI：OCR识别到进入结算界面5-恭喜获得")
                    return GameInfo.UI_PVE_Game_End_6

        # ————————————主界面识别————————————
        # ===无尽试炼===
        if GAME_MODE_CUR == GAME_MODE_PVP_WJSL:
            # 是否为主界面-未点击“开始游戏”
            OP.Sleep(ParamTime.slp_OCR)
            # OCR识别："开始游戏"
            if WinInfo.Text_Char_Main_Prepare in GetScrInfo.ocrAreaText(WinInfo.Area_Char_PVP_Main):
                logging.info(f"getCurUI：OCR识别到进入主界面-未点击“开始游戏”")
                return GameInfo.UI_PVP_Main_Prepare

            # 是否为主界面-已点击“开始游戏”，正在匹配玩家
            OP.Sleep(ParamTime.slp_OCR)
            # OCR识别："取消"
            if WinInfo.Text_Char_Main_Entering in GetScrInfo.ocrAreaText(WinInfo.Area_Char_PVP_Main):
                logging.info(f"getCurUI：OCR识别到进入主界面-已点击“开始游戏”，正在匹配玩家")
                return GameInfo.UI_PVP_Main_Entering
        # ===PVE征神，雪满弓刀===
        elif GAME_MODE_CUR == GAME_MODE_PVE_XMGD:
            # 【界面入口-1】主界面
            # OCR识别："开始征神"
            if WinInfo.Text_Char_PVE_Main in GetScrInfo.ocrAreaText(WinInfo.Area_Char_PVE_Main):
                logging.info(f"getCurUI：OCR识别到进入主界面-未点击“开始征神”")
                return GameInfo.UI_PVE_Main_Prepare
            # 前提：上一个界面是主界面
            if self.UI_valid == GameInfo.UI_PVE_Main_Prepare or self.UI_valid == GameInfo.UI_PVE_Main_Sure:
                if WinInfo.Text_Char_PVE_Main_Sure in GetScrInfo.ocrAreaText(WinInfo.Area_Char_PVE_Main_Sure):
                    logging.info(f"getCurUI：OCR识别到进入主界面-关闭疲劳的确认界面")
                    return GameInfo.UI_PVE_Main_Sure

        # 是否为主界面-消息弹窗
        OP.Sleep(ParamTime.slp_OCR)
        # OCR识别："取消"
        if WinInfo.Text_Char_Daily_Msg in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Daily_Msg):
            logging.info(f"getCurUI：OCR识别到进入主界面-已点击“开始游戏”，正在匹配玩家")
            return GameInfo.UI_Daily_Msg

        # ————————————游戏开始：英雄选择界面识别————————————
        # ===无尽试炼===
        if GAME_MODE_CUR == GAME_MODE_PVP_WJSL:
            # 是否为英雄选择界面？
            OP.Sleep(ParamTime.slp_OCR)
            # OCR识别："英雄选择"
            if WinInfo.Text_Char_Select_Hero in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Select_Hero):
                logging.info(f"getCurUI：OCR识别到进入英雄选择界面")
                return GameInfo.UI_PVP_Select_Hero
        # ===PVE征神，雪满弓刀===
        elif GAME_MODE_CUR == GAME_MODE_PVE_XMGD:
            # 前一个界面是主界面/消息弹窗界面/不勾选疲劳确认界面
            if (self.UI_valid == GameInfo.UI_PVE_Main_Prepare
                    or self.UI_valid == GameInfo.UI_Daily_Msg
                    or self.UI_valid == GameInfo.UI_PVE_Main_Sure
                    or self.UI_valid == GameInfo.UI_PVE_Select_Hero):
                # OCR识别："英雄选择"
                if WinInfo.Text_Char_PVE_Select_Hero in GetScrInfo.ocrAreaText(WinInfo.Area_Char_PVE_Select_Hero):
                    logging.info(f"getCurUI：OCR识别到进入英雄选择界面")
                    return GameInfo.UI_PVE_Select_Hero
        # ————————————游戏开始：跳点选择界面识别————————————
        # # 是否为跳点选择界面【无尽试炼没有跳点选择】
        # OP.Sleep(ParamTime.slp_OCR)
        # OCR识别“英雄选择”
        # if WinInfo.Text_Char_Select_Hero in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Select_Hero):
        #     logging.info(f"getCurUI：OCR识别到进入英雄选择界面")
        #     return GameInfo.UI_PVP_Select_Hero

        # ————————————登录界面识别————————————
        # OP.Sleep(ParamTime.slp_OCR)
        # OCR识别："公告"
        if WinInfo.Text_Char_Game_Start_1 in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_Start_1):
            logging.info(f"getCurUI：OCR识别到进入登录界面1：公告界面")
            return GameInfo.UI_LogIn_Announcement

        # OP.Sleep(ParamTime.slp_OCR)
        # 找到图片："适龄提示16+"
        if GetScrInfo.findPic(WinInfo.Pic_Char_Game_Start_2, self.clientArea)[0] >= 0:
            logging.info(f"getCurUI：OCR识别到进入登录界面2：适龄提示")
            return GameInfo.UI_LogIn_AgeRatingReminder

        # ————————————错误界面识别————————————
        # 主界面错误：提示，失去服务器连接
        # OP.Sleep(ParamTime.slp_OCR)
        # OCR识别："失去服务器链接"
        if WinInfo.Text_Char_Main_Err_LoseServerConnect in GetScrInfo.ocrAreaText(
                WinInfo.Area_Char_Main_Err_LoseServerConnect):
            logging.info(f"getCurUI：OCR识别到主界面错误：失去服务器连接")
            return GameInfo.UI_Err_Main_LoseServerConnect

        # 登录界面2：错误：提示，账号异常
        # OP.Sleep(ParamTime.slp_OCR)
        # OCR识别："账号异常"
        if WinInfo.Text_Char_Game_Start_2_Err in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_Start_2_Err):
            logging.info(f"getCurUI：OCR识别到启动界面错误：账号异常")
            return GameInfo.UI_Err_LogIn_AccountError

        # 未录入信息的其他错误界面，弹窗名称是“提示”
        # OP.Sleep(ParamTime.slp_OCR)
        if WinInfo.Text_DialogBox_Title_Name_Prompt in GetScrInfo.ocrAreaText(WinInfo.Area_DialogBox_Title_Name):
            Prompt = GetScrInfo.ocrAreaText(WinInfo.Area_DialogBox_Err_Content)
            logging.info(f"getCurUI：OCR识别到对话框弹窗，提示错误信息：{Prompt}")
            return GameInfo.UI_Err_Other


        # ————————————不符合上述任何一种界面：过渡界面————————————
        # 不符合任何一个特征，就认为进入了过渡界面。什么也不做，等待指定的时间：10秒
        logging.error(f"getCurUI：进入过渡界面。")
        return GameInfo.UI_Transition

# ==========PVP无尽试炼===================================
    # 游戏内的操作，无尽试炼
    def Handle_Game_In_WJSL(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        # 重复进行空手右键蓄力
        logging.info("【进入游戏局内界面：】")
        if self.getGameTimeLeft():
            logging.info(f"本局游戏剩余时间：{self.gameTimeLeftStr}")
        # 下面进行一次右键蓄力
        if MouseOp.RightClickAreaRandom(WinInfo.Area_Random_left_move, self.ratio):
            logging.info("游戏局内界面：使用右键蓄力成功")


    # 主界面，未点击“开始游戏”
    def Handle_PVP_Main_Prepare(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        logging.info("【进入主界面：未点击“开始游戏”】")
        if MouseOp.LeftClickAreaRandom(WinInfo.Area_Char_PVP_Main, self.ratio):
            # self.gameTime += 1 #这里获取游戏次数不对，因为可能存在匹配失败，多次点击“开始游戏”的情况
            logging.info("主界面：点击“开始游戏”成功，正在匹配……")
            # 点击开始后进入游戏，休眠等15秒进游戏：尝试匹配15秒
            OP.Sleep(ParamTime.slp_After_Start_Game)

    # 主界面，已经点击“开始游戏”，正在匹配玩家，当前特征区域显示“取消”
    def Handle_PVP_Main_Entering(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        logging.info("【进入主界面：正在匹配】")
        if MouseOp.LeftClickAreaRandom(WinInfo.Area_Char_PVP_Main, self.ratio):
            logging.info(f"主界面：等待{ParamTime.slp_After_Start_Game}"
                            f"秒后游戏未开始，匹配失败，取消匹配，等待下一次脚本点击“开始游戏”")



    # 进入游戏，选择英雄的界面
    def Handle_PVP_Select_Hero(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        logging.info("【进入英雄选择界面：】")
        if MouseOp.LeftClickAreaRandom(WinInfo.Area_Select_Cur_Hero, self.ratio):
            self.curHero = GetScrInfo.ocrAreaText(WinInfo.Area_Hero_Name)
            logging.info(f"已选择：{self.curHero}")


    # 进入游戏，选择跳点的界面
    def Handle_PVP_Select_Point(self):
        # 不选跳点，随机跳点，等待进入游戏
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()


    # 无尽试炼-结算界面1：这个界面显示几秒钟后，游戏能够会自行跳过
    def Handle_PVP_Game_End_WJSL_1(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        logging.info("【已跳过结算界面1】")

    # 无尽试炼-结算界面2：空格跳过
    def Handle_PVP_Game_End_WJSL_2(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        # 后续：OCR识别获取击败数量
        logging.info("【进入结算界面2】")
        if MouseOp.LeftClickAreaRandom(WinInfo.Area_Char_WJSL_End_2, self.ratio):
            logging.info("跳过了结算界面2")

    # 无尽试炼-结算界面3：空格跳过
    def Handle_PVP_Game_End_WJSL_3(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        # 后续：OCR识别获取增加的经验
        logging.info("【进入结算界面3】")
        if MouseOp.LeftClickAreaRandom(WinInfo.Area_Skip_WJSL_End_3, self.ratio):
            logging.info("跳过了结算界面3")

    # 无尽试炼-结算界面4：OCR获取通行证经验值，空格跳过
    def Handle_PVP_Game_End_WJSL_4(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        self.gameCnt += 1
        # 后续：OCR识别获取增加的经验
        logging.info("【进入结算界面4】")
        # 获取经验值EXP
        curEXP = self.getEXP_WJSJ()
        if curEXP > 0 :
            self.EXP += curEXP
            logging.info(f"本局游戏经验值：{curEXP}(若为0则表示OCR识别经验值失败。)")
        else:
            logging.warning(f"OCR识别经验值失败。")
        logging.info(f"本次脚本已获取游戏经验值：{self.EXP}")
        if KeyOp.PressKey(OPKeyCode.Space):
            logging.info("使用空格跳过结算界面4")

    # 无尽试炼-结算界面5：空格跳过
    def Handle_PVP_Game_End_WJSL_5(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        logging.info("【进入结算界面5】")
        if KeyOp.PressKey(OPKeyCode.Space):
            logging.info("使用空格跳过结算界面5")

# ==========PVE雪满弓刀===================================
    def Handle_PVE_Game_In_1_W(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        #从出生点走到传送点，耗时10秒
        # KeyOp.HoldKey(OPKeyCode.W, ParamTime.walkToEntry)
        KeyOp.HoldTwoKey(OPKeyCode.W, ParamTime.walkToEntry, OPKeyCode.Shift, ParamTime.walkToRunShift)
        OP.Sleep(ParamTime.slp_cmd)
        # 到达传送点，按E传送
        KeyOp.PressKey(OPKeyCode.E)
        # 再按一次E
        OP.Sleep(ParamTime.slp_cmd)
        KeyOp.PressKey(OPKeyCode.E)

    def Handle_PVE_Game_In_2_E(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        #到达传送点，按E传送
        KeyOp.PressKey(OPKeyCode.E)

    def Handle_PVE_Game_In_3_ESC(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        #可以ESC跳过的界面
        KeyOp.PressKey(OPKeyCode.ESC)

    def Handle_PVE_Game_In_4_Battle(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()

        self.battleCnt += 1
        # 第一次进入局内战斗界面时，初始化游戏开始时间
        if self.battleCnt == 1:
            self.gameTimeStart = datetime.now()
        # 计算目前已用时间
        self.gameTimeUsed = (datetime.now() - self.gameTimeStart).total_seconds()

        # 固定操作：右键蓄力+右键(左蓄+右键容易变成振刀。)
        holdTime = random.randint(ParamTime.holdTimeMin, ParamTime.holdTimeMax)
        MouseOp.RightHoldPoint(self.clientAreaMidPoint, holdTime, self.ratio)
        delayTime = random.randint(650,800)
        OP.Sleep(delayTime) #这个时间可以调整：蓄力完成后到点击右键的延时
        MouseOp.RightClickPoint(self.clientAreaMidPoint, self.ratio)
        # 每隔pcsOfF个周期放一次F
        if self.pcsCnt % ParamCnt.pcsOfF == 0:
            OP.Sleep(600)  # 这个时间可以调整：右键攻击到F的延时
            if KeyOp.PressKey(OPKeyCode.F):
                logging.info(f"尝试释放F技能")
        # 每隔pcsOfV个周期放一次V
        if self.pcsCnt % ParamCnt.pcsOfV == 0:
            OP.Sleep(500)  # 这个时间可以调整：F到V的延时
            if KeyOp.PressKey(OPKeyCode.V):
                logging.info(f"尝试释放V技能")

    def Handle_PVE_Game_In_5_Succeed(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        #按ESC，然点击固定区域，然后再点击空格
        KeyOp.PressKey(OPKeyCode.ESC)
        OP.Sleep(1000)
        # 如果OCR识别到“返回大厅”
        if WinInfo.Text_PVE_Return_Home_From_Game in GetScrInfo.ocrAreaText(WinInfo.Area_PVE_Return_Home_From_Game):
            logging.info(f"成功输入ESC，识别到“{WinInfo.Text_PVE_Return_Home_From_Game}”")
            #点击“返回大厅”这个区域
            MouseOp.LeftClickAreaRandom(WinInfo.Area_PVE_Return_Home_From_Game, self.ratio)
            logging.info(f"成功点击“{WinInfo.Text_PVE_Return_Home_From_Game}”")
            OP.Sleep(1500)
            KeyOp.PressKey(OPKeyCode.Space) #空格确定

    def Handle_PVE_Main_Prepare(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        self.battleCnt = 0
        MouseOp.LeftClickAreaRandom(WinInfo.Area_Char_PVE_Main, self.ratio)
        OP.Sleep(2000)  # 点击“开始征神”后，休眠2秒。防止一直点击。

    def Handle_PVE_Main_Sure(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        # 先勾选“今日不再提示”
        MouseOp.LeftClickPoint(WinInfo.Point_PVE_Main_Not_Notify, self.ratio)
        OP.Sleep(1000)
        # 然后点击确定
        MouseOp.LeftClickAreaRandom(WinInfo.Area_PVE_Main_Sure, self.ratio)

    def Handle_PVE_Select_Hero(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        MouseOp.LeftClickAreaRandom(WinInfo.Area_PVE_Select_Cur_Hero, self.ratio)
        OP.Sleep(ParamTime.slp_After_Select_Hero)

    def Handle_PVE_Game_End_1(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        KeyOp.PressKey(OPKeyCode.Space)

    def Handle_PVE_Game_End_2(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        EXPStr = GetScrInfo.ocrAreaText(WinInfo.Area_XMGD_EXE_Area_1)
        EXPstr_int = re.findall(r"\d+", EXPStr)[0]
        try:
            curEXP = int(EXPstr_int)
        except ValueError:
            print(f"Error: '{EXPstr_int}' is not a valid integer.")
            curEXP = ParamCnt.EXE_DEFAULT_WJSL
        self.EXP += curEXP
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
        logging.info("【进入主界面：发现每日消息弹窗】")
        if MouseOp.LeftClickPoint(WinInfo.Point_Daily_Msg_Skip, self.ratio):
            if KeyOp.PressKey(OPKeyCode.ESC):
                logging.info("已跳过每日消息弹窗。")

    # 如果在游戏局外，按下了ESC，会弹出这个界面。直接点击返回游戏即可。
    def Handle_ESC_Selection(self):
        # 移动到“返回游戏”，然后点击
        MouseOp.LeftClickPoint(WinInfo.Point_ESC_Select_OutGame_ReturnGame, self.ratio)
        logging.warning("误触ESC的界面：尝试跳出错误界面，点击一次“返回游戏”")

    # 过渡界面
    @staticmethod
    def Handle_Transition():
        OP.Sleep(ParamTime.slp_Transition)


    # # 非以上任何一个界面，可以空格跳过的界面
    # @staticmethod
    # def Handle_Skip_Space():
    #     if KeyOp.PressKey(OPKeyCode.Space):
    #         logging.warning("可以空格跳过的界面：尝试跳出错误界面，输入一次“空格”")
    #
    # # 非以上任何一个界面，可以ESC跳过的界面
    # @staticmethod
    # def Handle_Skip_ESC():
    #     if KeyOp.PressKey(OPKeyCode.ESC):
    #         logging.warning("可以ESC跳过的界面：尝试跳出错误界面，输入一次“ESC”")
    #
    # 非以上任何一个界面。异常界面。
    def Handle_Err_UI(self):
        # 检测用户输入暂停键:如果用户按下暂停键，则休眠30秒
        self.UserPause()
        # 不是上面的界面，则认为是错误界面信息，重新获取界面类型。并尝试以下3种方法跳出错误界面：
        # 1、按空格，2、按ESC，3、鼠标点击客户端中心位置

        self.errUICnt += 1
        # 移动鼠标到安全位置，点一下。
        # MouseOp.LeftClickPoint(WinInfo.Point_Safe_Click, self.ratio)
        # logging.warning(f"尝试跳出错误界面：鼠标点击客户端{WinInfo.Point_Safe_Click}位置一次")
        logging.error(f"连续{PscRltAll[FAULT_TRANSITION_UI].contExCnt}次识别到过渡界面，判定当前界面为错误界面，尝试跳出……")
        OP.Sleep(ParamTime.slp_cmd)
        if self.errUICnt % 2 == 0:
            if KeyOp.PressKey(OPKeyCode.Space):
                logging.warning("尝试跳出错误界面：输入一次“空格”")
        else:
            if KeyOp.PressKey(OPKeyCode.ESC):
                logging.warning("尝试跳出错误界面：输入一次“ESC”")




    #————————————————————————————————————————————————————————————————————
    # 更新窗口状态信息：#窗口是否存在、窗口是否正常响应、窗口是否激活、窗口尺寸是否正确
    # 只要所有检测项有一个异常，就返回False
    def updateWindowState(self)->bool:
        winStateRlt = True
        # op插件的GetWindowState函数获取窗口是否处于存在
        if OP.GetWindowState(self.hwnd, 0) == 1:
            self.windowStates[WIN_STATE_EXIST] = True  # 窗口还存在
        else:
            self.windowStates[WIN_STATE_EXIST] = False  # 窗口不存在了
            winStateRlt = False

        # op插件的GetWindowState函数获取窗口是否处于存在
        if OP.GetWindowState(self.hwnd, 6) == 1:
            self.windowStates[WIN_STATE_RESPONSE] = True  # 窗口可以正常响应
        else:
            # 【】【】【这个状态有问题】无论怎么获取，只要在后台，那就无响应。
            self.windowStates[WIN_STATE_RESPONSE] = False  # 窗口无响应
            # winStateRlt = False

        # op插件的GetWindowState函数获取窗口是否处于激活状态
        if OP.GetWindowState(self.hwnd, 1) == 1:
            self.windowStates[WIN_STATE_ACTIVE] = True #激活
        else:
            self.windowStates[WIN_STATE_ACTIVE] = False #未激活
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
            print("启动游戏。")

        # 【2-发现问题】窗口是否正常响应？无响应则重新启动程序
        # 【】【】有问题。目前这个状态会一直报故障。先不管。
        if not self.windowStates[WIN_STATE_RESPONSE]:
            # 【2-解决办法】重启游戏
            # self.closeGame()
            # self.startGame()
            print("关闭游戏。")
            print("启动游戏。")

        # 【3-发现问题】窗口是否处于激活状态（在前台显示）？未激活则激活窗口
        if self.pcsCnt % ParamCnt.cntCycActive == 0:  # 每5个周期激活一次窗口。不能每个周期都检查，不然就没法关闭游戏了。
            if not self.windowStates[WIN_STATE_ACTIVE]:  # 如果当前不是激活状态
                if OP.SetWindowState(self.hwnd, 12) == 1:  # 激活窗口，显示到前台
                    OP.SetWindowState(self.hwnd, 7)
                    logging.info(f"检测到窗口未激活，尝试激活窗口成功。")
                else:
                    logging.error(f"检测到窗口未激活，尝试激活窗口失败！")

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
        if self.hwnd != 0:  #如果绑定过窗口先解绑
            OP.UnBindWindow()
            self.hwnd = 0
        # 如果游戏窗口还存在，先关闭窗口。最多尝试关闭3次窗口（15s）
        retryCnt = 0
        while retryCnt < 3:
            if OP.GetWindowState(self.hwnd, 0) != 1: #窗口不存在
                # 窗口已经被关闭了，退出循环
                self.windowStates[WIN_STATE_EXIST] = False
                self.windowStates[WIN_STATE_RESPONSE] = False
                self.windowStates[WIN_STATE_ACTIVE] = False
                self.windowStates[WIN_STATE_AREA_OK] = False
                break
            retryCnt += 1

            #发送指令：关闭窗口
            #  【】 【】 【】有问题。不要这样关闭，使用ESC，然后在游戏内点击来关闭。
            # ————————————————————————————————————————————————————————————————————
            if OP.SetWindowState(self.hwnd,0) != 1:
            # ————————————————————————————————————————————————————————————————————
            
                logging.error(f"尝试第{retryCnt}关闭窗口失败！")
            OP.Sleep(ParamTime.closeWinWait) # 每次发送完关闭窗口的指令后，等待5秒

    # ————————————————————————————————————————————————————————————————————
    # 启动游戏：如果脚本是以管理员权限运行的话，那么程序也能以管理员权限启动
    def startGame(self)->bool:
        #只有先关闭现有的游戏窗口，才能重新启动游戏# 如果游戏窗口不存在了，再启动游戏
        if not self.windowStates[WIN_STATE_EXIST] :
            # 但是这里有一个问题。。运行这个程序会有弹窗，提示需要管理员权限。需要输入一个向左、然后一个Enter，才能运行程序。
            # 不过如果本脚本是以管理员权限运行的，那么也不会弹窗提示需要管理员权限了。

            #  【】 【】 【】有问题。这样启动后，游戏会提示异常。
            # ————————————————————————————————————————————————————————————————————
            OP.WinExec(GameInfo.gameLauncherPath, 1)   #用最近的大小和位置显示,激活。  |
            # ————————————————————————————————————————————————————————————————————

            OP.Sleep(ParamTime.gameStartWaitTime)  # 启动后，等一段时间秒，让程序起来再说

            if not self.initSelf():
                logging.error(f"初始化失败。")
                return False

            if not self.entryGame():
                return False

            return True
        logging.error(f"游戏窗口尚未关闭，无法重新启动游戏。")
        return False



    # 启动游戏后，怎么进入游戏正常界面
    def entryGame(self):
        # 尝试6次吧，如果不行，就进入失败，需要关闭游戏，然后重启游戏
        tryCnt = 0
        while tryCnt < 5:
            tryCnt += 1
            # 如果识别到了特征区域的特征字符串，就认为进入了启动界面1
            if GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_Start_1) == WinInfo.Text_Char_Game_Start_1:
                KeyOp.PressKey(OPKeyCode.Space)#按下空格
            # 等待一段时间
            OP.Sleep(ParamTime.gameStart1ToStart2)
            # 跳过启动界面2
            if GetScrInfo.findPic(WinInfo.Pic_Char_Game_Start_2, self.clientArea)[2] > 0:
                MouseOp.LeftClickPoint(WinInfo.Point_Safe_Click, self.ratio)   #点击屏幕内的安全点
            #等待一段时间
            OP.Sleep(ParamTime.gameStart2ToMainUI)
            # 跳过启动界面2后，如果识别到了特征图片“账号异常”。该故障不可恢复。需要关闭游戏，然后重启游戏
            if GetScrInfo.findPic(WinInfo.Pic_Char_Game_Start_2_Account_Err, self.clientArea)[2] > 0:
                logging.critical(f"账号异常！必须关闭游戏再重启游戏。")
                return False
            # 跳过启动界面2后，如果识别到了特征区域的特征字符串“账号异常”。该故障不可恢复。需要关闭游戏，然后重启游戏
            elif WinInfo.Text_Char_Game_Start_2_Err in GetScrInfo.ocrAreaText(WinInfo.Area_Char_Game_Start_2_Err):
                logging.critical(f"账号异常！必须关闭游戏再重启游戏。")
                return False
            self.getCurUI()
            # 如果最后进入到游戏主界面/每日消息弹窗界面，那么就认为游戏启动成功
            if self.UI == GameInfo.UI_PVP_Main_Prepare or self.UI == GameInfo.UI_Daily_Msg:
                return True
        # 多次尝试，仍然失败
        return False


    # 通过截图然后OCR识别指定区域，来获取本局游戏剩余时间
    def getGameTimeLeft(self)->bool:
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

    #判断一个字符串是不是正确的时间格式，例如“06:23”是正确的
    @staticmethod
    def is_valid_time_format(time_str:str)->bool:
        # 正则表达式匹配 "分钟:秒" 格式
        pattern = r'^[0-5]?[0-9]:[0-5]?[0-9]$'
        # 使用 re.match 来检查字符串是否匹配
        if re.match(pattern, time_str):
            return True
        else:
            return False

    #检测用户输入暂停键，则休眠脚本
    @staticmethod
    def UserPause():
        if KeyOp.DetectKey(ParamCnt.Key_User_Pause):
            logging.critical(f"检测到用户输入暂停键，脚本休眠{ParamTime.slp_User_Pause}ms")
            OP.Sleep(ParamTime.slp_User_Pause)


    # 获取无尽试炼模式的经验值
    @staticmethod
    def getEXP_WJSJ()->int:
        OP.Sleep(ParamTime.slp_OCR)
        EXPstr =  GetScrInfo.ocrAreaText(WinInfo.Area_WJSL_EXE_Area_1)  # 如果截图指成功
        # logging.info(f"getEXP_WJSJ：OCR识别到经验值字符串：{EXPstr}")
        EXPstr_int = re.findall(r"\d+",EXPstr)[0]
        try:
            EXE1 = int(EXPstr_int)
        except ValueError:
            print(f"Error: '{EXPstr_int}' is not a valid integer.")
            EXE1 = ParamCnt.EXE_DEFAULT_WJSL
        # logging.info(f"getEXP_WJSJ：OCR识别到经验值：{curEXP}")
        # 经验值有自己的合理范围，如果不在合理范围内，就置0
        if not(ParamCnt.EXE_MIN_WJSL <= EXE1 <= ParamCnt.EXE_MAX_WJSL):
            EXE1 = ParamCnt.EXE_DEFAULT_WJSL
            logging.warning(f"OCR识别通行证经验值失败，记为默认经验值{ParamCnt.EXE_DEFAULT_WJSL}。")
        return EXE1




def RunAuto():
    auto = Automation()
    if auto.initSelf():
        #初始化成功，开始自动化
        auto.auto_play()


if __name__ == "__main__":
    RunAuto()