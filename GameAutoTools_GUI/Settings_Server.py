#本文件是一些参数设置
from OPFuncs import OPTime, gameLauncherPath


# 下面是一些宏定义
WIN_STATE_CNT = 4    #监测的窗口状态数量
WIN_STATE_EXIST = 0        #窗口是否存在
WIN_STATE_RESPONSE = 1     #窗口是否能正常响应
WIN_STATE_ACTIVE = 2       #窗口是否激活
WIN_STATE_AREA_OK = 3       #窗口四维坐标是否

#游戏模式：无尽试炼、PVE征神-雪满弓刀
GAME_MODE_ALL= ("PVP_WJSL", "PVE_XueManGongDao")
GAME_MODE_PVP_WJSL = "PVP_WJSL"             #无尽试炼
GAME_MODE_PVE_XMGD = "PVE_XueManGongDao"    #PVE征神，雪满弓刀


#======================================================
GAME_MODE_CUR = GAME_MODE_PVE_XMGD          #当前游戏模式
#======================================================

# 时间相关参数
class ParamTime(OPTime):
    slp_Transition = 500  # 过渡界面，休眠时间
    sleep_main_cycle = 50  # 每个周期，主动休眠的时间

    closeWinWait = 5000 # 关闭窗口后，需要等待的时间。这样窗口才能彻底关闭
    gameStartWaitTime = 60000 #启动指定的游戏exe文件后，等一段时间让程序起来，单位：毫秒
    gameStart1ToStart2 = 5000 #游戏启动界面1，到启动界面2的等待时间
    gameStart2ToMainUI = 8000  # 游戏启动界面1，到启动界面2的等待时间

    # ——————————————无尽试炼——————————————
    # 【说明】用户需要长按这个暂停键5秒以上，才能暂停脚本！
    slp_User_Pause = 30000  # 用户主动暂停，则休眠脚本30秒
    slp_After_Start_Game = 15000  # 脚本点击“开始游戏”后，需要休眠的时间。如果不休眠，可能会导致一直点这个区域导致匹配失败。
    TimeLeftS_WJSL_Max = 780  # 一局无尽试炼，最多13min×60s=780秒
    default_InGame_LefTimeS_MAX = 10  # 如果游戏剩余时间大于等于10秒，就不进行完整的get_cur_UI()函数获取界面信息

    # ——————————————PVE雪满弓刀——————————————
    default_InGame_TimeUsed_PVE_XMGD = 70   #打一局PVE雪满弓刀，最少耗时70秒
    slp_After_Select_Hero = 10000  # 脚本选好英雄后，休眠一段时间，防止把等待进入游戏的界面识别为过渡界面，导致进入错误界面处理的函数
    walkToEntry = 4500    #从出生点走到传送点，耗时x秒
    walkToRunShift = 1500  # 按住Shift后，开始奔跑的时间。
    holdTimeMin = 1300      #PVE征神的蓄力最短时间
    holdTimeMax = 1400      #PVE征神的蓄力最长时间




# 计数相关参数
class ParamCnt:
    cntCycActive = 5  # 间隔多少个周期，激活一次窗口
    cntGetRatio = 5 # 最多尝试获取坐标系倍率的次数

    EXE_MIN_WJSL = 20  # 一局无尽试炼，正常的通行证经验值范围：20～100
    EXE_MAX_WJSL = 100
    EXE_DEFAULT_WJSL = 35   # 一局无尽试炼，默认的通行证经验值
    EXE_DEFAULT_XMGD = 20   # 一局PVE雪满弓刀，默认的通行证经验值

    Key_User_Pause = 17  # 用户输入该键，则休眠脚本30秒：目前是：Ctrl（需要长按Ctrl好几秒才行）

    pcsOfF = 5     #PVE征神:每隔多少个周期释放一次F
    pcsOfV = 15     #PVE征神:每隔多少个周期释放一次V

#游戏相关的信息：比如界面之类的
class GameInfo:
    # 窗口名
    windowName_game = "Naraka"   #游戏窗口名。NeacProtect  Naraka
    windowName_NeteaseStarter = "永劫无间"  #网易的启动器的窗口名
    windowName_EpicStarter = "Epic Games 启动器"             #Epic的启动器窗口名  SystemTray  Epic Games启动器

    # 游戏启动器的绝对路径
    gameLauncherPath = gameLauncherPath

    #——————————————————————————各个UI界面——————————————————————————————————————————————————
    # ——————————————————————错误界面————————————————————————

    UI_Err_Other = -1                #未记录的其他错误界面
    UI_Err_Main_LoseServerConnect = -2    #主界面错误：提示，失去服务器连接
    UI_Err_LogIn_AccountError = -3       #登录界面2错误：提示，账号异常
    #——————————————————————游戏内————————————————————————
    UI_PVP_Game_In_WJSL = 50  # 游戏内界面：无尽试炼
    # UI_PVP_Game_Dad = 51  # 游戏内界面，死亡，待返魂
    UI_PVE_Game_In_1_W = 60  # 游戏内界面：PVE征神，未到达传送点，长按W前往传送点
    UI_PVE_Game_In_2_E = 61  # 游戏内界面：PVE征神，到达传送点，可以E传送
    UI_PVE_Game_In_3_ESC = 62  # 游戏内界面：PVE征神，传送后出现的过渡动画，可以ESC跳过
    UI_PVE_Game_In_4_Battle = 63  # 游戏内界面：PVE征神，局内战斗界面
    UI_PVE_Game_In_5_Succeed = 64  # 游戏内界面：PVE征神，通关成功，可以ESC返回大厅

    # ——————————————————————游戏登录界面————————————————————————
    UI_LogIn_Announcement = 1     #登录界面1：公告
    UI_LogIn_AgeRatingReminder = 2  #登录界面2：适龄提示
    # ——————————————————————游戏外————————————————————————
    # ———————主界面———————
    UI_PVP_Main_Prepare = 1     # 吃鸡模式的主界面，未点击“开始游戏”
    UI_PVP_Main_Entering = 2    # 吃鸡模式下，点击“开始游戏”后，等待进入游戏的界面
    UI_Daily_Msg = 3            # 开启游戏后，进入主界面可能会遇到弹窗，右下角区域“今日不再提示”，可以ESC退出该界面
    UI_PVE_Main_Prepare = 4     # PVE征神模式的主界面，未点击“开始征神”
    UI_PVE_Main_Sure = 5  # PVE征神模式的主界面，取消勾选疲劳值，点击“开始征神”后的确认界面
    # ———————选择界面———————
    UI_PVP_Select_Hero = 30  # 选择界面：选择英雄，无尽试炼（各个模式应该是通用的）。
    UI_PVE_Select_Hero = 31  # 选择界面：选择英雄，PVE征神。
    UI_PVP_Select_Point = 32  # 选择界面：选择跳点，无尽试炼没有跳点选择界面。
    # ———————结算界面：无尽试炼———————
    UI_PVP_Game_End_WJSL_1 = 100  # 无尽试炼结算界面1-击败信息：无需操作，游戏数秒内自动跳过
    UI_PVP_Game_End_WJSL_2 = 101  # 无尽试炼结算界面2-击败信息：可以按下空格来跳过
    UI_PVP_Game_End_WJSL_3 = 102  # 无尽试炼结算界面3-段位信息：可以按下空格来跳过
    UI_PVP_Game_End_WJSL_4 = 104  # 无尽试炼结算界面4-经验信息：先OCR获取通行证经验值，然后可以按下空格来跳过
    UI_PVP_Game_End_WJSL_5 = 105  # 无尽试炼结算界面5-用户等级：可以按下空格来跳过
    # ———————结算界面：PVE征神———————
    UI_PVE_Game_End_1 = 110  # PVE征神结算界面1-伤害+用时信息
    UI_PVE_Game_End_2 = 111  # PVE征神结算界面2-本局获得的各种经验数值、奖励：先OCR获取通行证经验值，然后可以按下空格来跳过
    UI_PVE_Game_End_3 = 112  # PVE征神结算界面3-段位信息：可以按下空格来跳过
    UI_PVE_Game_End_4 = 114  # PVE征神结算界面4-潜能信息：可以按下空格来跳过
    UI_PVE_Game_End_5 = 115  # PVE征神结算界面5-首次获得：可以按下ESC来跳过
    UI_PVE_Game_End_6 = 116  # PVE征神结算界面6-恭喜获得：可以按下Space来跳过
    # ———————ESC选择界面———————
    UI_ESC_Selection_InGame = 220  # 游戏内，按到了ESC的弹窗，可以返回游戏/返回大厅
    UI_ESC_Selection_OutGame = 221  # 游戏外，主界面，按到了ESC的弹窗，可以返回游戏/退出游戏
    # ———————其他界面———————
    UI_Transition = 0  # 过渡界面
    # # ———————可以主动跳过的界面———————
    # UI_Skip_Space = 250  # 可以跳过的界面：空格跳过：skipPic1.bmp，skipPic2.bmp
    # UI_Skip_ESC = 251  # 可以跳过的界面，ESC跳过：skipPic3.bmp



# 窗口的特征信息：某区域会有特定字符串，屏幕会有某图片
class WinInfo:
    # ============游戏启动界面======================
    # 启动界面1：可以识别特征区域的字符串，如果是“公告”就行
    Area_Char_Game_Start_1 = (612, 196, 669, 230)
    Text_Char_Game_Start_1 = "公告"

    # 启动界面2，识别特征图片：适龄提示16+
    Pic_Char_Game_Start_2 = "/Pic/GameStart2.bmp"
    #=====异常界面=====
    # 启动界面2的故障：“账号异常”，识别特征区域字符串会包含“账号异常”
    Area_Char_Game_Start_2_Err = (523, 332, 758, 364)
    Text_Char_Game_Start_2_Err = "账号异常"
    # 启动界面2的故障：“账号异常”，识别特征图片：适龄提示16+
    Pic_Char_Game_Start_2_Account_Err = "/Pic/gameStart2AccountErr.bmp"

    # ============主界面======================
    # 无尽试炼
    Area_Char_PVP_Main = (1061,644,1211,686)   #该界面的特征区域
    Text_Char_Main_Prepare = "开始游戏"                 #如果是这个界面，特征区域里必然出现的字符串
    Text_Char_Main_Entering = "取消"
    Area_SeasonPass_Name = (98, 0, 200, 26)             #OCR识别该区域，获得通行证/战令名称：“永昼通信证”
    Area_SeasonPass_Level = (106, 23, 192, 41)          #OCR识别该区域，获得通行证/战令等级：“赛季等级XX”
    #PVE雪满弓刀
    Area_Char_PVE_Main = (1054, 641, 1226, 682)     # 特征区域
    Text_Char_PVE_Main = "开始征神"
    Area_Char_PVE_Main_Sure = (496, 325, 789, 373)  #“当前挑战不再积累疲劳，但不产生掉落”
    Text_Char_PVE_Main_Sure = "疲劳"
    Point_PVE_Main_Not_Notify = (595, 445)  # 点击这个点，勾选上“今日不再提示”
    Area_PVE_Main_Sure = (506, 403, 568, 427) # 这个区域是“确定”
    #通用
    Area_Char_Daily_Msg = (1112, 695, 1195, 718)    #识别该区域，可以得到字符串“今日不再提示”。这个界面使用ESC跳过。
    Text_Char_Daily_Msg = "今日不再提示"
    Point_Daily_Msg_Skip = [1103, 705]              #点击该点，可以勾选中“今日不再提示”
    # =====异常界面=====
    Area_Char_Main_Err_LoseServerConnect = (340, 316, 938, 374)
    Text_Char_Main_Err_LoseServerConnect = "失去服务器连接"

    # ============英雄选择界面======================
    # 无尽试炼
    Area_Char_Select_Hero = (1,1,139,49)
    Text_Char_Select_Hero = "英雄选择"
    Area_Hero_Name = (952,103,1141,143)    #在英雄选择界面OCR识别这个区域，能知道选择了什么英雄
    Area_Select_Cur_Hero = (1014,610,1148,636) #在英雄选择界面点击该区域，选择当前英雄
    Text_Select_Cur_Hero = "使用"
    #PVE雪满弓刀
    Area_Char_PVE_Select_Hero = (0, 0, 120, 40)
    Text_Char_PVE_Select_Hero = "英雄选择"
    Area_PVE_Hero_Name = (943, 114, 1194, 153)  # 在英雄选择界面OCR识别这个区域，能知道选择了什么英雄
    Area_PVE_Select_Cur_Hero = (1057,611,1123,634)  # 在英雄选择界面点击该区域，选择当前英雄

    # ============无尽试炼-结算界面======================
    # 结算界面1：
    # 游戏会自动跳过该界面，脚本可以不用识别。
    Area_Char_WJSL_End_1 = (0, 0, 134, 40)
    Text_Char_WJSL_End_1 = "战斗前三甲"
    # 结算界面2：
    Area_Char_WJSL_End_2 = (807, 623, 899, 651)
    Text_Char_WJSL_End_2 = "返回大厅"
    # 结算界面3：
    Area_Char_WJSL_End_3 = (564, 118, 724, 172)
    Text_Char_WJSL_End_3 = "试炼" # 这个特征区域的特征字符串是“试炼X段”
    Area_Skip_WJSL_End_3 = (544, 661, 582, 683)
    # Text_Skip_WJSL_End_3 = "继续"
    # 结算界面4：
    # 如果识别到特征图片EXEUI_Pic.bmp或者OCR指定区域的文本是“恭喜获得”：就认为当前是结算界面4，在本界面可以OCR识别通行证经验值
    Area_Char_WJSL_End_4 = (591, 231, 695, 272)
    Text_Char_WJSL_End_4 = "恭喜获得"
    Area_WJSL_EXE_Area_1 = (697, 373, 720, 393)  # 如果是2位数的通行证经验，该区域是准确的
    # Area_WJSL_EXE_Area_2 = (688, 396, 735, 396)  # 该区域的数字为通行证经验，范围更广、背景更复杂。【成功率比1低很多，作废】
    # 结算界面5：
    # 该界面是游戏等级经验，没什么用。
    Area_Char_WJSL_End_5 = (613, 278, 668, 312)
    Text_Char_WJSL_End_5 = "等级"
    # ============PVE雪满弓刀-结算界面======================
    # 结算界面1：
    # 游戏会自动跳过该界面，脚本可以不用识别。
    Area_Char_XMGD_End_1 = (45, 45, 145, 94)
    Text_Char_XMGD_End_1 = "胜利"
    # 结算界面2：
    Area_Char_XMGD_End_2 = (78, 303, 154, 335)
    Text_Char_XMGD_End_2 = "战斗奖励"
    # Area_Char_XMGD_End_2 = (101, 186, 178, 214)
    # Text_Char_XMGD_End_2 = "宁红夜"
    Area_XMGD_EXE_Area_1 = (194, 389, 212, 405)  # 如果是2位数的通行证经验，该区域是准确的
    # 结算界面3：
    Area_Char_XMGD_End_3 = (612, 281, 670, 312)
    Text_Char_XMGD_End_3 = "等级"  # 这个特征区域的特征字符串是“等级”
    Area_Skip_XMGD_End_3 = (648, 609, 689, 637)
    # Text_Skip_XMGD_End_3 = "继续"
    # 结算界面4：
    # 如果识别到特征图片EXEUI_Pic.bmp或者OCR指定区域的文本是“恭喜获得”：就认为当前是结算界面4，在本界面可以OCR识别通行证经验值
    Area_Char_XMGD_End_4 = (591, 257, 695, 294)
    Text_Char_XMGD_End_4 = "潜能等级"
    # 结算界面5（不一定出现）：
    # 可能出现的“首次获得”某个魂玉，识别右下角有没有“ESC返回”。
    Area_Char_XMGD_End_5 = (1230, 691, 1265, 715)
    Text_Char_XMGD_End_5 = "返回"
    # 结算界面6（不一定出现）：
    # 可能出现的“首次获得”某个魂玉，识别右下角有没有“ESC返回”。
    Area_Char_XMGD_End_6 = (558, 226, 718, 274)
    Text_Char_XMGD_End_6 = "获得"

    # ============游戏内界面======================
    #无尽试炼
    Area_Char_Game_In_WJSL_1 = (35, 5, 67, 30)
    Text_Char_Game_In_WJSL_1 = "排名"
    Pic_Char_Game_In_WJSL_Powder1 = "/Pic/ArmorPowder1.bmp"   #特征图片：护甲粉末。无尽试炼模式一出生就自带
    Pic_Char_Game_In_WJSL_Pill1 = "/Pic/BloodPill1.bmp"  # 特征图片：大包凝血丸。无尽试炼模式一出生就自带
    # Area_Char_Game_Inner_2 = (84, 660, 174, 681)  # 这个用户名，其实在主界面也能识别到。。不能算特征
    # Text_Char_Game_Inner_2 = "初代玄女顾清寒"
    Area_Random_left_move = [240, 180, 900, 550]  # 游戏局内时，鼠标在该区域随机移动
    Area_Time_Left = (1155, 0, 1214, 23)  # 在游戏内，该区域显示本局游戏的剩余时间，格式为“12:23”
    # PVE雪满弓刀
    Area_Char_Game_In_PVE_1 = (59, 60, 130, 115)    #特征区域：OCR识别该区域应该是势比登天
    Text_Char_Game_In_PVE_1 = "势比登天"
    Pic_Char_Game_In_PVE_2 = "/Pic/Char_Game_In_PVE_2.bmp"  # 特征图片，如果找到这个图片，就认为是游戏内界面2
    Area_Char_Game_in_PVE_3 = (1214, 687, 1250, 711) #特征区域，可以跳过的过渡动画
    Text_Char_Game_in_PVE_3 = "跳过"
    Area_Char_Game_in_PVE_4 = (397, 3, 467, 29)  # 特征区域，OCR识别该区域应该是昆仑主母
    Text_Char_Game_in_PVE_4 = "昆仑主母"
    Area_Char_Game_in_PVE_5 = (596, 107, 683, 133)  # 特征区域，OCR识别该区域应该是通关成功
    Text_Char_Game_in_PVE_5 = "通关成功"
    Area_PVE_Return_Home_From_Game = (603, 495, 678, 517)
    Text_PVE_Return_Home_From_Game = "返回大厅"

    # ============ESC弹窗选择界面======================
    #游戏内
    Area_Char_ESC_Select_InGame = (606, 493, 676, 518)
    Text_Char_ESC_Select_InGame = "返回大厅"
    Area_ESC_Select_InGame_ReturnGame = (603, 292, 678, 318)
    Text_ESC_Select_InGame_ReturnGame = "回到游戏"
    Point_ESC_Select_InGame_ReturnGame = (638, 506)

    #游戏外
    #特征区域-特征字符串
    Area_Char_ESC_Select_OutGame = (605, 552, 678, 578)
    Text_Char_ESC_Select_OutGame = "退至桌面"
    #选项：回到游戏
    Area_ESC_Select_OutGame_ReturnGame = (605, 233, 678, 259)
    Text_ESC_Select_OutGame_ReturnGame = "回到游戏"
    Point_ESC_Select_OutGame_ReturnGame = (636, 528)
    #选项：返回登录界面
    Area_ESC_Select_OutGame_ReturnLogIn = (591, 514, 690, 539)
    Text_ESC_Select_OutGame_ReturnLogIn = "返回登录界面"
    Point_ESC_Select_OutGame_ReturnLogIn = (636, 528)
    # 确认弹窗：返回登录界面
    Area_Char_ESC_Select_OutGame_ReturnLogIn_Sure = (545, 328, 738, 368)
    Text_Char_ESC_Select_OutGame_ReturnLogIn_Sure = "是否确定返回登录界面"    #可以用空格进行确定
    #选项：退至桌面（退出游戏）
    Area_ESC_Select_OutGame_ReturnDesktop = (605, 552, 678, 578)
    Text_ESC_Select_OutGame_ReturnDesktop = "退至桌面"
    Point_ESC_Select_OutGame_ReturnDesktop = (639, 567)     #可以用空格进行确定
    #确认弹窗：退至桌面
    Area_ESC_Select_OutGame_ReturnDesktop_Sure = (781, 458, 848, 484)
    Text_ESC_Select_OutGame_ReturnDesktop_Sure = "确认退出"
    Point_ESC_Select_OutGame_ReturnDesktop_Sure = (815, 472)

    # ============错误界面======================
    Area_DialogBox_Title_Name = (557, 216, 736, 281)    #弹窗名：提示/恭喜获得……
    Text_DialogBox_Title_Name_Prompt = "提示"             #对话框弹窗的标题：提示
    Area_DialogBox_Err_Content = (340, 316, 938, 374)   #OCR识别该区域，可以获得对话框弹窗的内容
    # ============其他======================
    Point_Safe_Click = (167,96) # 安全点击区域，如果进入到错误界面，点击这个位置可以安全跳过，不会点进奇怪的界面

# ————————————————————————————————————————————————————————————————————
# #代码流程控制相关的参数
# class CodeControl1:
#     gameSoftwarePath = "D:/EpicGames/NARAKABLADEPOINT/StartGame.exe"    # 无界14
#     # gameSoftwarePath = "D:/EpicGame/NARAKABLADEPOINT/StartGame.exe" # 服务器
#     # clientWindowSize_X = 1280   #设置Naraka窗口的尺寸：宽
#     # clientWindowSize_Y = 720      #设置Naraka窗口的尺寸：高
#     clientWindowSize_X = 1280  # 设置Naraka窗口的尺寸：宽
#     clientWindowSize_Y = 800  # 设置Naraka窗口的尺寸：高
#
#     ## 启动指定的游戏exe文件后，等一段时间秒，让程序起来，显示出界面后再说，单位：毫秒，这里是80秒
#     gameRestartWaitTime1 = 80000
#     ## 启动指定的游戏exe文件后，等一段时间秒，让程序起来，显示出界面后再说，单位：毫秒，这里是10秒
#     gameRestartWaitTime2 = 10000
#
#     loop_count = 5    #主循环次数，即游戏的场数
#
#     OCR_sim = 0.8       #OCR的相似度,取值范围 0.1-1.0
#     FindPic_sim = 0.9       #查找图片的相似度
#
#     #【说明】用户需要长按这个暂停键5秒以上，才能暂停脚本！
#     key_user_paused = 17    #用户输入该键，则休眠脚本30秒：目前是：Ctrl（需要长按Ctrl好几秒才行）
#     sleep_user_paused = 30000   #用户按下暂停键，则休眠30秒
#     sleep_after_start_game = 15000  #脚本点击“开始游戏”后，需要休眠的时间。如果不休眠，可能会导致一直点这个区域导致匹配失败。
#
#     sleep_main_cycle = 200  #每个周期，主动休眠的时间
#
#     Common_sleep = 100  #各个普通操作之间的睡眠时间，100毫秒
#     OCR_sleep = 200     #每次进行OCR之前，休眠的时间
#     Capture_sleep = 200 #每次截屏前，休眠的时间
#     FindPic_sleep = 200 #每次查找图片前，休眠的时间
#     Move_sleep = 100    #每次移动鼠标前，休眠的时间
#     Click_sleep = 100  # 每次点击鼠标前，休眠的时间
#
#     Random_range_x = 10   #随机移动鼠标时，随机范围，单位：像素点
#     Random_range_y = 10  # 随机移动鼠标时，随机范围，单位：像素点
#
#     HoldTimeStart = 1100    #蓄力时间随机范围的最小值
#     HoldTimeEnd = 3500      #蓄力时间随机范围的最大值
#
#     GameInTimeS_MAX = 20    #如果游戏剩余时间大于等于20秒，就不进行完整的get_cur_UI()函数获取界面信息
#     Critical_Failure_Max_Cnt = 10 # 连续N个周期发生严重故障，重启游戏



# #游戏相关的信息：比如模式之类的
# class GameInfo1:
#     UI_Err = -1             #未获取到界面信息
#
#     #PVP的各个界面
#     UI_PVP_Main_Prepare = 1         #主界面：选择模式：人机/征神，进入游戏，准备界面，未点击“开始游戏”
#     UI_PVE_Main_Enter = 2   #主界面：选择模式：人机/征神，进入游戏，已经点击“开始游戏”，等待进入游戏
#     UI_PVP_Select_Hero = 20  #选择界面：选择英雄
#     UI_PVP_Select_Point = 30 #选择界面：选择跳点
#     UI_PVP_Game_in = 40      #游戏内界面
#     UI_PVP_Game_dad = 41    # 游戏内界面，死亡，待返魂
#     UI_PVP_Game_End1 = 50    #结算界面2-击败信息：可以按下空格来跳过
#     UI_PVP_Game_End2 = 51    #结算界面3-段位信息：可以按下空格来跳过
#     UI_PVP_Game_End4 = 54   # 结算界面4-经验信息：先OCR获取通行证经验值，然后可以按下空格来跳过
#
#     UI_Skip_Space = 100   #可以跳过的界面：空格跳过：skipPic1.bmp，skipPic2.bmp
#     UI_Skip_ESC = 101       #可以跳过的界面，ESC跳过：skipPic3.bmp
#
#     UI_Return_game = 120 #返回游戏：ReturnGame.bmp
#
#     EXE_MIN = 20    #一局无尽试炼，默认的通行证经验值范围：20～100
#     EXE_MAX = 100
#
#     TimeLeftS_Max = 780 #一局无尽试炼，最多13min×60s=780秒

#
# #无界14X屏幕原始分辨率：2880*1800
# #界面信息，比如主界面的特征信息是右下角一个红色的“开始”/“取消”
# class UIInfo1:
#     physical_screen_resolution = [2880,1800]   #无界14X屏幕原始分辨率：2880*1800
#     # physical_screen_resolution = [1280, 720]  # 无界14X屏幕原始分辨率：2880*1800
#     ratio_screen = 2.0              #屏幕物理分辨率/窗口矩形分辨率 = 比例，该参数可以修改
#
#     # UI_main_area = [2404,1542,2730,1634]
#     UI_main_area = [1061,644,1211,686]
#     UI_main_text1 = "开始游戏"
#     UI_main_text2 = "取消"
#
#     UI_select_hero_area = [1,1,139,49]
#     UI_select_hero_text = "英雄选择"
#     UI_Cur_hero = [952,103,1141,143]    #在英雄选择界面OCR识别这个区域，能知道选择了什么英雄
#     UI_Select_cur_hero = [1014,610,1148,636] #在英雄选择界面点击该区域，选择当前英雄
#     UI_Select_cur_hero_text = "使用"
#
#     UI_select_point_area = [976,15,1090,56]
#     UI_select_point_text1 = "聚窟州"
#     # UI_select_point_text2 = "龙隐洞天"
#
#     # UI_end_area1 = [542,661,581,684]
#     # UI_end_text1 = "继续"
#     # UI_end_area2 = [719,661,756,685]
#     # UI_end_text2 = "分享"
# #============武道争锋START======================
#     #结算界面1：
#     #游戏会自动跳过该界面，脚本可以不用识别。
#
#     # 结算界面2：
#     UI_end_area1 = [807, 623, 899, 651]
#     UI_end_text1 = "返回大厅"
#
#     # 结算界面3：
#     UI_end_area2 = [544, 661, 582, 683]
#     UI_end_text2 = "继续"
#
#     # 结算界面4：
#     #如果识别到特征图片EXEUI_Pic.bmp或者OCR指定区域的文本是“恭喜获得”：就认为当前是结算界面4，在本界面可以OCR识别通行证经验值
#     UI_end_area4 = [591, 231, 695, 272]
#     UI_end_text4 = "恭喜获得"
#     UI_EXE_area_1 = [697, 373, 720, 393]    #如果是2位数的通行证经验，该区域是准确的
#     UI_EXE_area_2 = [688, 396, 735, 396]    #该区域的数字只有通行证经验，但是范围更广、背景更复杂，粗略级别。
#
#     # 结算界面5：
#     # 该界面是游戏等级经验，没什么用。
#
#     # 游戏内界面：
#     UI_game_area = [35, 5, 67, 30]
#     UI_game_text = "排名"
#     UI_game_area2 = [84, 660, 174, 681]
#     UI_game_text2 = "初代玄女顾清寒"
#     UI_time_left = [1155, 0, 1214, 23]  #在游戏内，该区域显示本局游戏的剩余时间，格式为“12:23”
# # ============武道争锋END========================
#     UI_safe_click_area = [167,96] # 安全点击区域，如果进入到错误界面，点击这个位置可以安全跳过，不会点进奇怪的界面
#
#     # UI_game_area = [34, 7, 65, 28]
#     # UI_game_text = "尚存"
#
#
#     UI_Random_left_move = [240, 180, 900, 550]  #游戏局内时，鼠标在该区域随机移动
#
#     UI_game_end1 = [489, 268, 535, 294]
#     UI_game_end1_text = "击败"
#     UI_game_end11 = [75,267,113,294]
#     UI_game_end11_text = "玩家"
#     UI_end_kill_num = [488,314,534,343] #结算界面1-击败信息：OCR识别这个区域，能知道击败数量
#     UI_end_hurt_num = [657,316,707,345] #结算界面1-伤害信息，OCR识别该区域，能获取本局伤害值
#
#     UI_game_end2 = [78, 266, 138, 292]
#     UI_game_end2_text = "英雄印"
#     UI_game_end2_value = [214,168,262,188]  #结算界面2-经验信息：OCR该区域，得到经验值“+13”之类的字符串
#     UI_game_end2_level = [140,168,182,188]  #结算界面2-经验信息：OCR识别这个区域，能知道当前等级
#
#     UI_game_dad = [564,190,682,214]
#     UI_game_dad_text = "进入返魂坛复活"