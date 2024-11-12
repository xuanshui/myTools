#本文件是一些参数设置
path_tools_dll = "D:/code/Python/Tools/op-0.4.5_with_model/tools.dll"
path_opx64_dll = "D:/code/Python/Tools/op-0.4.5_with_model/op_x64.dll"
#代码流程控制相关的参数
class CodeControl:
    clientWindowSize_X = 1280
    clientWindowSize_Y = 720

    loop_count = 5    #主循环次数，即游戏的场数

    OCR_sim = 0.8       #OCR的相似度,取值范围 0.1-1.0
    FindPic_sim = 0.9       #查找图片的相似度

    #【说明】用户需要长按这个暂停键5秒以上，才能暂停脚本！
    key_user_paused = 17    #用户输入该键，则休眠脚本30秒：目前是：Ctrl（需要长按Ctrl好几秒才行）
    sleep_user_paused = 30000   #用户按下暂停键，则休眠30秒
    sleep_after_start_game = 15000  #脚本点击“开始游戏”后，需要休眠的时间。如果不休眠，可能会导致一直点这个区域导致匹配失败。

    sleep_main_cycle = 500  #主循环每500ms进行一次

    Common_sleep = 100  #各个普通操作之间的睡眠时间，100毫秒
    OCR_sleep = 200     #每次进行OCR之前，休眠的时间
    Capture_sleep = 200 #每次截屏前，休眠的时间
    FindPic_sleep = 200 #每次查找图片前，休眠的时间
    Move_sleep = 100    #每次移动鼠标前，休眠的时间
    Click_sleep = 100  # 每次点击鼠标前，休眠的时间

    Random_range_x = 10   #随机移动鼠标时，随机范围，单位：像素点
    Random_range_y = 10  # 随机移动鼠标时，随机范围，单位：像素点

    HoldTimeStart = 1100    #蓄力时间随机范围的最小值
    HoldTimeEnd = 5000      #蓄力时间随机范围的最大值

class KeyCode:
    ESC = 27
    Cap = 20
    Space = 32

#游戏相关的信息：比如模式之类的
class GameInfo:
    UI_Err = -1             #未获取到界面信息

    #PVP的各个界面
    UI_PVP_Main_Prepare = 1         #主界面：选择模式：人机/征神，进入游戏，准备界面，未点击“开始游戏”
    UI_PVE_Main_Enter = 2   #主界面：选择模式：人机/征神，进入游戏，已经点击“开始游戏”，等待进入游戏
    UI_PVP_Select_Hero = 20  #选择界面：选择英雄
    UI_PVP_Select_Point = 30 #选择界面：选择跳点
    UI_PVP_Game_in = 40      #游戏内界面
    UI_PVP_Game_dad = 41    # 游戏内界面，死亡，待返魂
    UI_PVP_Game_End1 = 50    #结算界面1-击败信息：可以按下空格来跳过
    UI_PVP_Game_End2 = 51    #结算界面2-经验信息：可以按下空格来跳过

    UI_Skip_Space = 100   #可以跳过的界面：空格跳过：skipPic1.bmp，skipPic2.bmp
    UI_Skip_ESC = 101       #可以跳过的界面，ESC跳过：skipPic3.bmp

    UI_Return_game = 120 #返回游戏：ReturnGame.bmp


#无界14X屏幕原始分辨率：2880*1800
#界面信息，比如主界面的特征信息是右下角一个红色的“开始”/“取消”
class UIInfo:
    physical_screen_resolution = [2880,1800]   #无界14X屏幕原始分辨率：2880*1800
    # physical_screen_resolution = [1280, 720]  # 无界14X屏幕原始分辨率：2880*1800
    ratio_screen = 2.0              #屏幕物理分辨率/窗口矩形分辨率 = 比例，该参数可以修改

    # UI_main_area = [2404,1542,2730,1634]
    UI_main_area = [1061,644,1211,686]
    UI_main_text1 = "开始游戏"
    UI_main_text2 = "取消"

    UI_select_hero_area = [1,1,139,49]
    UI_select_hero_text = "英雄选择"
    UI_Cur_hero = [952,103,1141,143]    #在英雄选择界面OCR识别这个区域，能知道选择了什么英雄
    UI_Select_cur_hero = [1014,610,1148,636] #在英雄选择界面点击该区域，选择当前英雄
    UI_Select_cur_hero_text = "使用"

    UI_select_point_area = [976,15,1090,56]
    UI_select_point_text1 = "聚窟州"
    # UI_select_point_text2 = "龙隐洞天"

    # UI_end_area1 = [542,661,581,684]
    # UI_end_text1 = "继续"
    # UI_end_area2 = [719,661,756,685]
    # UI_end_text2 = "分享"
#============武道争锋START======================
    UI_end_area1 = [807, 623, 899, 651]
    UI_end_text1 = "返回大厅"
    UI_end_area2 = [544,661,582,683]
    UI_end_text2 = "继续"

    UI_game_area = [35, 5, 67, 30]
    UI_game_text = "排名"
    UI_game_area2 = [84, 660, 174, 681]
    UI_game_text2 = "初代玄女顾清寒"
# ============武道争锋END========================

    # UI_game_area = [34, 7, 65, 28]
    # UI_game_text = "尚存"


    UI_Random_left_move = [240, 180, 900, 550]  #游戏局内时，鼠标在该区域随机移动

    UI_game_end1 = [489, 268, 535, 294]
    UI_game_end1_text = "击败"
    UI_game_end11 = [75,267,113,294]
    UI_game_end11_text = "玩家"
    UI_end_kill_num = [488,314,534,343] #结算界面1-击败信息：OCR识别这个区域，能知道击败数量
    UI_end_hurt_num = [657,316,707,345] #结算界面1-伤害信息，OCR识别该区域，能获取本局伤害值

    UI_game_end2 = [78, 266, 138, 292]
    UI_game_end2_text = "英雄印"
    UI_game_end2_value = [214,168,262,188]  #结算界面2-经验信息：OCR该区域，得到经验值“+13”之类的字符串
    UI_game_end2_level = [140,168,182,188]  #结算界面2-经验信息：OCR识别这个区域，能知道当前等级

    UI_game_dad = [564,190,682,214]
    UI_game_dad_text = "进入返魂坛复活"
