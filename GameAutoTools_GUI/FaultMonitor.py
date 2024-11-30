# 故障监控相关信息
from  Common import *

#===================宏定义=========================
FAULT_CNT = 10              #故障监控中，所有故障类型的总数
FAULT_TRANSITION_UI = 0     #过渡界面异常

#===================所有的故障=========================
PscCfgAll = []
PscRltAll = []
for i in range(FAULT_CNT):
    cfg = PscCfg()
    rlt = PscRlt
    PscCfgAll.append(cfg)
    PscRltAll.append(rlt)


#===================具体的故障=========================
# 过渡界面：连续识别到5次过渡界面，认为发生故障。故障可恢复，恢复条件：识别到1次非过渡界面
PscCfgAll[FAULT_TRANSITION_UI].init(5, 1, True)