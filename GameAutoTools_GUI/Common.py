import logging  #日志记录


#调整日志记录形式：以文本形式记录
LOG_FORMAT = "%(asctime)s- %(levelname)s -%(message)s"
log_file_name = "log.txt"
log_file_handler = logging.FileHandler(log_file_name, encoding='GBK')   #GB18030
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, handlers={log_file_handler})
# logging.basicConfig(filename=log_file_name, level=logging.DEBUG, format=LOG_FORMAT)


#————————————————————————————————————————————————————
# 周期自检 periodic self-check:PSC
#————————————————————————————————————————————————————
# 周期自检配置periodic self-check config
# 该检测项的3种属性，最多连续多少次异常就上报故障？故障是否可以恢复？发生故障后，最多连续多少次实时拍正常就恢复上报结果为正常？
class PscCfg:
    contExCnt = 255  # 连续异常上报故障的次数阈值consecutive exception count：默认为255
    contNormCnt = 255  # 连续正常取消上报故障的次数阈consecutive normal count：默认为255
    isRecov = True  # 故障是否可以恢复is recoverable：默认为可以恢复

    @staticmethod
    def init(contExCnt:int = 255, contNormCnt:int = 255, isRecov:bool = True):
        PscCfg.contExCnt = contExCnt      #连续异常上报故障的次数阈值consecutive exception count：默认为255
        PscCfg.contNormCnt = contNormCnt    #连续正常取消上报故障的次数阈consecutive normal count：默认为255
        PscCfg.isRecov = isRecov    #故障是否可以恢复is recoverable：默认为可以恢复
        #如果故障不可恢复，那么就将连续正常取消上报故障的次数阈值设置为255
        if not PscCfg.isRecov:
            PscCfg.contNormCnt = 255
    # def __init__(self, contExCnt:int = 255, contNormCnt:int = 255, isRecov:bool = True):
    #     self.contExCnt = contExCnt      #连续异常上报故障的次数阈值consecutive exception count：默认为255
    #     self.contNormCnt = contNormCnt    #连续正常取消上报故障的次数阈consecutive normal count：默认为255
    #     self.isRecov = isRecov    #故障是否可以恢复is recoverable：默认为可以恢复
    #     #如果故障不可恢复，那么就将连续正常取消上报故障的次数阈值设置为255
    #     if not isRecov:
    #         self.contNormCnt = 255

# 周期自检结果periodic self-check result
class PscRlt:
    contNormCnt = 0  # 连续正常次数consecutive normal count：默认为0
    contExCnt = 0  # 连续异常次数consecutive exception count：默认为0
    maxContExCnt = 0  # 最大连续异常次数max consecutive exception count：默认为0
    totalExCnt = 0  # 异常总次数total exception count：默认为0
    realTimeRlt = True  # 当前拍的检测结果real time self-check result：默认为正常
    reportRlt = True  # 上报的检测结果reported self-check result：默认为正常
    # def __init__(self):
    #     self.contNormCnt = 0        #连续正常次数consecutive normal count：默认为0
    #     self.contExCnt = 0          #连续异常次数consecutive exception count：默认为0
    #     self.maxContExCnt = 0       #最大连续异常次数max consecutive exception count：默认为0
    #     self.totalExCnt = 0         #异常总次数total exception count：默认为0
    #     self.realTimeRlt = True    #当前拍的检测结果real time self-check result：默认为正常
    #     self.reportRlt = True      #上报的检测结果reported self-check result：默认为正常

# 实现周期自检；根据当前拍的检测结果curRlt、该检测项的检测配置pscCfg，更新该检测项的周期自检结果pscRlt
def pSelfCheck(curRlt:bool, pscRlt:PscRlt, pscCfg:PscCfg):
    #更新实时拍结果
    pscRlt.realTimeRlt = curRlt
    # 如果当前拍的故障次数为0（当前拍检测结果为正常）
    if curRlt:
        pscRlt.contNormCnt += 1 #连续正常次数+1
        pscRlt.contExCnt = 0    #连续异常次数清零
        if pscCfg.isRecov:      #如果是可恢复故障：
            if pscRlt.contNormCnt >= pscCfg.contNormCnt: #如果连续正常次数≥当前检测项的周期自检配置中的连续正常取消报故阈值：
                pscRlt.reportRlt = True #将本检测项的检测结果中的上报结果置为正常
    else:
        pscRlt.contNormCnt = 0  #连续正常次数清零
        pscRlt.contExCnt += 1   #连续异常次数+1
        pscRlt.totalExCnt += 1  #异常总次数+1
        if pscRlt.maxContExCnt < pscRlt.contExCnt:  #如果最大连续异常次数＜连续异常次数：
            pscRlt.maxContExCnt = pscRlt.contExCnt  #最大连续异常次数=连续异常次数
        if pscRlt.contExCnt >= pscCfg.contExCnt:    #如果连续异常次数≥连续异常报故障阈值：
            pscRlt.reportRlt = False    #将本检测项的检测结果中的上报结果置为故障



# 周期自检PSC
# 周期自检配置periodic self-check config（一个结构体）
# ｛
# 连续异常报故障阈值consecutive exception count
# 连续正常取消报故阈值consecutive normal count
# 故障是否可以恢复is recoverable
# ｝
# 周期自检结果periodic self-check result（一个结构体）
# 连续正常次数consecutive normal count
# 连续异常次数consecutive exception count
# 最大连续异常次数max consecutive exception count
# 异常总次数total exception count
# 当前拍的检测结果real time self-check result
# 上报的检测结果reported self-check result
# 周期自检逻辑函数
# bool PSC(当前周期是否故障/当前周期的故障次数current self-check result，&所有故障的周期自检结果数组[当前检测项的索引号]all periodic self-check result[current fault index]，当前检测项的周期自检配置current fault periodic self-check config)
#
# 更新检测结果中的实时拍检测结果
# periodic self-check result[current fault index]=current self-check result
#  如果本拍检测结果正常：
# 连续正常次数+1
# 连续异常次数=0
#
# 如果是可恢复故障：
# 如果连续正常次数≥当前检测项的周期自检配置中的连续正常取消报故阈值：
# 将本检测项的检测结果中的上报结果置为正常
#
# 如果本拍检测结果异常：（else）
# 连续正常次数=0
# 连续异常次数+1
# 异常总次数+1
# 如果最大连续异常次数＜连续异常次数：
# 最大连续异常次数=连续异常次数
#
# 如果连续异常次数≥连续异常报故障阈值：
# 将本检测项的检测结果中的上报结果置为故障
#
#
#
#
#
#
# 周期循环做任务的实现方法（这里的当前时间是每毫秒自己减1，不是越来越大）
#
# 时间标志=当前时间+周期时间
# while（True）：
# if 时间标志-当前时间≥所有任务号时间段数组[当前任务号]：
# switch 任务号
# case 任务①：
# 时间标志=当前时间
# case 任务②：
# xxxx
# case 任务③：
# xxx
# （结束switch语句）
# 任务号+1
# if 任务号≥任务号数量：
# 任务号=0
# 任务超时监控(时间标志)
# 【实现逻辑：
# if时间标志-当前时间＞周期时间：
# 任务超时计数+1】
# （if语句结束）
#
# else：（每个任务号的空闲时间）
# xxxx
#
# （if语句结束）