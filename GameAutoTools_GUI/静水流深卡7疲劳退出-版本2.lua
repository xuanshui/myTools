--使用方法：
--1、要在进入BOSS图之前，即小怪关卡中把断厄斩积攒出来，并保留断厄斩（至少需要把3个据点都打完才行）。
--2、进入BOSS地图后，一定要使2只BOSS都触发一次冰爆从而消耗BOSS血量（顾清寒可以在BOSS还在空中时F穿过去），这样才能保证后续的断厄斩能直接清空BOSS血条。
--3、如果F穿BOSS后马上要被冰冻，不要着急使用宏，等冰冻结束，此时两只BOSS也都在人物旁边，再按上侧键启动脚本，并且按了上侧键之后一定不能移动鼠标！！！否则会导致卡疲劳退出失败！！！
--4、两个关键步骤的时间间隔：普通攻击命中BOSS，点按空格确认退出，实测两者时间间隔为1300～1350均能成功。1300为版本1,1350为版本2.

--全局变量
CurX = 0    --鼠标当前周期所在位置：X坐标
CurY = 0    --鼠标当前周期所在位置：Y坐标
--OutputLogMessage("5\n")

function OnEvent(event, arg)
    --该行的5代表启动按键：上侧键，可根据自己鼠标侧键编号酌情更换
    if (event == "MOUSE_BUTTON_RELEASED" and arg == 5) then
        OutputLogMessage("==================脚本已启动==================\n")
        
        --打印鼠标当前位置
        CurX, CurY = GetMousePosition()
        OutputLogMessage("鼠标当前周期的位置: (%d,%d)\n", CurX, CurY)
        
        --====【主要功能函数】====
        -- 1. 单击右键，触发断厄斩
        PressMouseButton(3)
        Sleep(50)
        ReleaseMouseButton(3)
        Sleep(200)    --必须休眠，等待上一步操作完成
        
        -- 2.再按 ESC，弹出退出界面
        PressAndReleaseKey("escape")
        Sleep(200)    --必须休眠，等待上一步操作完成

        -- 3. 移动鼠标到指定位置“返回大厅”
        MoveMouseTo(32640, 46193)  --“返回大厅”在台式机Desktop（2K屏幕）的绝对位置： 1275÷2560×65535，1015÷1440×65535
        Sleep(200)    --必须休眠，等待上一步操作完成
        
        -- 4. 单击左键
        PressMouseButton(1)
        Sleep(50)
        ReleaseMouseButton(1)

        -- 5. 延时 1000ms
        Sleep(750)

        -- 6. 按空格键，确认返回大厅
        PressAndReleaseKey("spacebar")     
        
        OutputLogMessage("==================脚本已结束==================\n")
    end
end