#本文件是一些参数设置

#代码流程控制相关的参数
class CodeControl:
    loop_count = 3    #主循环次数，即游戏的场数
    OCR_sim = 0.8       #OCR的相似度,取值范围 0.1-1.0
    OCR_sleep = 1000

#游戏相关的信息：比如模式之类的
class GameInfo:
    UI_Err = -1             #未获取到界面信息

    #PVP的各个界面
    UI_PVP_Main = 1         #主界面：选择模式：人机/征神，进入游戏
    UI_PVP_Select_Hero = 2  #选择界面：选择英雄
    UI_PVP_Select_Point = 3 #选择界面：选择跳点
    UI_PVP_Game_in = 4      #游戏内界面
    UI_PVP_Game_End1 = 5    #结算界面1-击败信息：可以按下空格来跳过
    UI_PVP_Game_End2 = 6    #结算界面2-经验信息：可以按下空格来跳过


#无界14X屏幕原始分辨率：2880*1800
#界面信息，比如主界面的特征信息是右下角一个红色的“开始”/“取消”
class UIInfo:
    physical_screen_resolution = [2880,1800]   #无界14X屏幕原始分辨率：2880*1800
    ratio_screen = 2.0              #屏幕物理分辨率/窗口矩形分辨率 = 比例，该参数可以修改

    UI_main_area = [2404,1542,2730,1634]
    UI_main_text1 = "开始"
    UI_main_text2 = "取消"

    UI_select_hero_area = [1,2,3,4]
    UI_select_hero_text = "英雄选择"
    UI_select_point_area = [1,2,3,4]
    UI_select_point_text1 = "龙隐洞天"
    UI_select_point_text2 = "聚窟州"

    UI_end_area1 = [1,2,3,4]
    UI_end_text1 = "继续"
    UI_end_area2 = [1,2,3,4]
    UI_end_text2 = "分享"

    UI_game_area = [1,2,3,4]
    UI_game_text = "尚存"