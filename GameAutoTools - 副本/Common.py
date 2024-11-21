import logging
from Settings_Server import *

log_file_name = "log.txt"

#判断一个点的坐标是否在指定的区域内
def isPosInArea(pointArea:list, rangeArea:list)->bool:
    posInArea = False #默认位置不在区域内
    if pointArea[0] >= list[0] and pointArea[1] >= list[1]:
        if pointArea[0] <= list[2] and pointArea[1] <= list[3]:
            posInArea = True
    return posInArea
