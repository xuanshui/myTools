--使用方法：
--1、把游戏内的“设置”--“键鼠”--“视角灵敏度”的设置为50
--2、使游戏处于主界面-征神之路
--3、按鼠标的上侧键，脚本自动开始。
Sensibility = 50  --永劫无间的视角灵敏度（1～100）

--全局计数器
CycCnt = 0        --周期计数起点
CycTime = 1000  --周期500ms
PausedTime = 10000 --触发主动暂停，10秒
EndFlg = false  --脚本结束标识，true：运行，false：结束
CurX = 0    --鼠标当前周期所在位置：X坐标
CurY = 0    --鼠标当前周期所在位置：Y坐标
--OutputLogMessage("5\n")

function OnEvent(event, arg)
    --该行的9代表启动按键，可根据自己鼠标侧键编号酌情更换
    if (event == "MOUSE_BUTTON_RELEASED" and arg == 5) then
        OutputLogMessage("==================脚本已启动==================\n")
        while true do
            CycCnt = CycCnt + 1
            Sleep(CycTime )  --周期控制，防止脚本消耗太多资源
            
            --暂停(Caps锁定)或结束(Scroll锁定)脚本
            if PauseAndEnd() then
              OutputLogMessage("==================脚本已被主动结束==================\n")
              break
            end
            
            --打印周期计数
            OutputLogMessage("周期计数: %d\n", CycCnt)
            --打印鼠标当前位置
            CurX, CurY = GetMousePosition()
            OutputLogMessage("鼠标当前周期的位置: (%d,%d)\n", CurX, CurY)
            --打印脚本运行时间
            OutputLogMessage("脚本已运行时间： %d\n", GetRunningTime())
            
            --====【主要功能函数】====
            AutoOperation()

            --结束(Scroll锁定)脚本
            if EndFlg then
                OutputLogMessage("==================脚本已被主动结束==================\n")
                break
            end
        end
    end
end


--主要挂机函数
function AutoOperation()
    OutputLogMessage("======AutoOperation运行中======\n")

    --=======【主界面部分】=======
    MoveMouseTo(60000,60000)      --移动到“开始征神”
    Sleep(400)
    PressAndReleaseMouseButton(1)  --左键点击  
    Sleep(800)
    MoveMouseTo(25000,38000)      --移动到确认弹窗（脚本不管是什么内容，只进行确认操作）
    Sleep(300)
    PressAndReleaseMouseButton(1)
    OutputLogMessage("==开始征神==\n")
    Sleep(16000)                  --休眠16秒，等待进入英雄选择界面
    
    if EndFlg then      --检测是否结束脚本
        return false
    end
    --=======【英雄选择界面】=======
    MoveMouseTo(15100,14100)      --移动到季沧海头像处，然后选中
    Sleep(400)
    PressAndReleaseMouseButton(1)
    Sleep(400)
    MoveMouseTo(60000,56000)      --移动到英雄确认选择按钮
    Sleep(400)
    PressAndReleaseMouseButton(1)
    OutputLogMessage("==英雄选择完成==\n")
    Sleep(34000)                  --选完英雄，休眠34秒

    if EndFlg then      --检测是否结束脚本
        return false
    end

    --=======【过渡动画界面】=======
    PressAndReleaseKey("escape")  --esc跳过过渡动画
    Sleep(800)
    OutputLogMessage("==已跳过过度动画==\n")
    
    if EndFlg then      --检测是否结束脚本
        return false
    end

    --=======【游戏内界面】=======
    Run(2000)                      --【奔跑到P2】
    OutputLogMessage("==已到达P2==\n")
    MoveMouseR(1200, -400)   --调整视角
    GouSuoMove()                    --【钩锁移动到P3】
    OutputLogMessage("==已到达P3==\n")
    
    if EndFlg then      --检测是否结束脚本
        return false
    end
    
    Run(2500)                       --【奔跑到P4，平台终点】
    OutputLogMessage("==已到达P4==\n")
    MoveMouseR(-440, -175)   --调整视角
    
    if EndFlg then      --检测是否结束脚本
        return false
    end
    
    GouSuoMove2()                    --【钩锁飞袭经过P5移动到P6】
    Sleep(1000)  --等待落地
    OutputLogMessage("==已经过P5到达P6==\n")
    
    if EndFlg then      --检测是否结束脚本
        return false
    end
    
    Run(4200)                   --【前进到P7】
    OutputLogMessage("==已到达P7==\n")
    MoveMouseR(-1200,650)        --左转视角，面对小怪
    ClickKey("f", 100)        --F技能使用火球击败小怪
    OutputLogMessage("==已在P7使用技能击败小怪==\n")
    Sleep(2000)                --F技能存在后摇，必须等待动作完成
    
    MoveMouseR(-400,0)        --左转视角
    Run(2000)                   --【前进到P8】
    Sleep(1000)                --P8这里有落差，需要等待落地后摇结束
    OutputLogMessage("==已到达P8==\n")
    
    if EndFlg then      --检测是否结束脚本
        return false
    end
    
    
    MoveMouseR(-2000,0)        --左转视角
    Run(1550)                  --【前进到P8.5】
    MoveMouseR(1000,0)        --右转视角
    Run(1200)                   --【前进到P9】
    OutputLogMessage("==已到达P9==\n")
    
    if EndFlg then      --检测是否结束脚本
        return false
    end
  
    OutputLogMessage("==正在P9执行火炮攻击==\n")
    ClickKey("2", 100)        --切换为远程武器：火炮
    Sleep(400)
    MoveMouseR(720,-100)   --调整视角1，火炮攻击3次
    for fireCnt = 1, 3 do
        FirePao()
        if EndFlg then      --检测是否结束脚本
            return false
        end
    end
    Sleep(400)
    MoveMouseR(-1590,818)   --调整视角2，火炮攻击7次
    for fireCnt = 1, 7 do
        FirePao()
        if EndFlg then      --检测是否结束脚本
            return false
        end
    end
    
    ClickKey("r", 100)        --维修武器
    Sleep(3800)         --等待武器维修完成
    
    for fireCnt = 1, 7 do   --继续在视角2，火炮攻击7次
        FirePao()
        if EndFlg then      --检测是否结束脚本
            return false
        end
    end
    
    MoveMouseR(-795,0)   --调整视角3
    Run(2300)                   --【前进到P10】
    OutputLogMessage("==已到达P10，即将执行3次蚊子防漏攻击==\n")
    MoveMouseR(0,-420)   --调整视角1，右转
    FirePao()           --火炮攻击，击败可能存在的蚊子
    MoveMouseR(4318,0)   --调整视角2，右转
    FirePao()           --火炮攻击，击败可能存在的蚊子
    MoveMouseR(1818,0)   --调整视角2，右转
    FirePao()           --火炮攻击，击败可能存在的蚊子
    
    if EndFlg then      --检测是否结束脚本
        return false
    end


    --移动视角，前往宝箱处开箱
    MoveMouseR(-1477,0)   --调整视角，左转
    Run(2100)                     --【前进到P11】
    ClickKey("e", 100)        --E开箱
    Sleep(800)
    OutputLogMessage("==已到达P11宝箱处，并E开箱==\n")
    
    PauseAndEnd()
    if EndFlg then      --检测是否结束脚本
        return false
    end

    PressAndReleaseKey("escape")    --ESC返回大厅
    Sleep(400) 
    MoveMouseTo(34000,46000)        --移动鼠标到“返回大厅”
    Sleep(900)
    PressAndReleaseMouseButton(1)
    Sleep(900)
    --后面是跳过结算画面
    PressAndReleaseKey("spacebar")
    Sleep(15000)                --等待最长的结算画面结束
    --空格跳过结算界面，执行5次
    for SkipCnt = 1, 5 do
        PressAndReleaseKey("spacebar")
        Sleep(2000)
    end
    --这里应该是防止有ESC弹窗，点右下角的那个“ESC跳过”的小字
    MoveMouseTo(64000,64000)
    Sleep(400)
    PressAndReleaseMouseButton(1)
    Sleep(800)

    return true
end

--封装的跑步函数,无需理会
function Run(t)
    OutputLogMessage("Run:%d\n", t)

    PressKey("w")
    Sleep(10)
    PressKey("lshift")
    Sleep(t)
    ReleaseKey("w")
    ReleaseKey("lshift")
    Sleep(400)  --奔跑动作有后摇，等待后摇结束
end

--封装的长按键位函数，无需理会
function ClickKey(key, time)
    OutputLogMessage("ClickKey\n")

    PressKey(key)
    Sleep(time)
    ReleaseKey(key)
end

--火炮攻击
function FirePao()
    OutputLogMessage("FirePao\n")

    --暂停(Caps锁定)或结束(Scroll锁定)脚本
    PauseAndEnd()

    Sleep(400)
    PressMouseButton(1)
    Sleep(100)
    ReleaseMouseButton(1)
    Sleep(1300)
end

--起钩锁但不飞袭，并等待钩锁落地
function GouSuoMove()
    OutputLogMessage("GouSuoMove\n")

    --暂停(Caps锁定)或结束(Scroll锁定)脚本
    PauseAndEnd()

    ClickKey("q", 100)                    --起钩锁
    Sleep(100)
    PressMouseButton(1)                   --出钩锁
    Sleep(100)
    ReleaseMouseButton(1)
    Sleep(3000)                     --等待钩锁落地
end

--钩锁飞袭，并等待钩锁落地
function GouSuoMove2()
    OutputLogMessage("GouSuoMove2\n")

    --暂停(Caps锁定)或结束(Scroll锁定)脚本
    PauseAndEnd()

    ClickKey("q", 100)                    --起钩锁
    Sleep(100)
    PressMouseButton(1)                   --出钩锁
    Sleep(100)
    ReleaseMouseButton(1)
    Sleep(400)
    PressMouseButton(1)                   --飞袭
    Sleep(100)
    ReleaseMouseButton(1)
    Sleep(2500)                     --等待钩锁落地
end

--调整视角
function MoveMouseR(X, Y)
    --由于脚本是在游戏视角灵敏度22的基础上调的，所以这里要根据实际的视角灵敏度进行比例换算，并取整
    local CurX, CurY
    CurX = math.modf(22/ Sensibility * X)
    CurY = math.modf(22/ Sensibility * Y)
    OutputLogMessage("MoveMouseR:(%d, %d)\n", CurX , CurY )
    
    --暂停(Caps锁定)或结束(Scroll锁定)脚本
    PauseAndEnd()
    
    MoveMouseRelative(CurX, CurY)   --调整视角
    Sleep(400)                 --等待后摇动作结束
end

--脚本的暂停或结束
function PauseAndEnd()
    --如果滚动写锁定，则暂停脚本
    if IsKeyLockOn("scrolllock") then
        OutputLogMessage("===脚本休眠 %d ms===\n",PausedTime)
        Sleep(PausedTime )
    end
    --如果大小写锁定，则退出脚本
    if IsKeyLockOn("capslock") then
        OutputLogMessage("==检测到滚动锁定，准备结束脚本==\n")
        EndFlg = true
        return true
    else
        EndFlg = false
    end
    return false
end