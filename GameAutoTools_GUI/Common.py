import logging  #日志记录
from ruamel.yaml import YAML    #yaml配置文件的读写，该软件包能在写入时保留注释
from typing import Any  #函数参数类型
import os   #文件操作
from enum import Enum

#————————————————————————————————————————————————————
# 日志记录相关
#————————————————————————————————————————————————————
#调整日志记录形式：以文本形式记录
LOG_FORMAT = "%(asctime)s- %(levelname)s -%(message)s"
log_file_name = "log.txt"
log_file_handler = logging.FileHandler(log_file_name, encoding='GBK')   #GB18030
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, handlers={log_file_handler})
# logging.basicConfig(filename=log_file_name, level=logging.DEBUG, format=LOG_FORMAT)

#日志级别
class LogLevel(Enum):
    info = 1
    warning = 2
    error = 3
    critical = 4

#————————————————————————————————————————————————————
# 配置文件读写 yaml格式：默认名称config.yaml，文件编码格式：utf-8
#————————————————————————————————————————————————————
class RwYaml:
    # 初始化
    def __init__(self, filename = 'config.yml', **kwargs):
        """
        Args:
            self.config: YAML配置字典
            *keys: 不定长参数，表示嵌套的键路径
            value: 要写入的值
            **kwargs: 其他关键字参数
                - create_dirs: 是否创建目录（默认True）
                - encoding: 文件编码（默认utf-8）
                - indent: YAML缩进（默认2）
                - width: 每行最大宽度（默认80）
                - preserve_quotes: 是否保留引号（默认False）
                - sort_keys: 是否排序键（默认False）
        """

        # 类属性
        self.filename = filename
        self.config = {}           #yaml文件的所有配置信息
        self.file_exist = True  #yaml文件是否存在
        self.file_read_success = True   #yaml文件读取是否成功
        self.file_write_success = True  #yaml文件写入是否成功

        # 初始化yaml
        self.yaml = YAML()  #这里不能传入参数 typ='safe'， 不然注释会被删除。
        # 处理关键字参数
        self.yaml_create_dirs = kwargs.get('create_dirs', False)  # 默认不创建目录
        self.yaml_encoding = kwargs.get('encoding', 'utf-8')  # 文件编码（默认utf-8）
        self.yaml_indent = kwargs.get('indent', 2)  # YAML缩进（默认2）
        self.yaml_width = kwargs.get('width', 80)  # 每行最大宽度（默认80）
        self.yaml_preserve_quotes = kwargs.get('preserve_quotes', False)  # 是否保留引号（默认False）
        self.yaml_sort_keys = kwargs.get('sort_keys', False)  # 是否排序键（默认False）
        # 如果需要创建目录
        if self.yaml_create_dirs:
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        self.yaml.preserve_quotes = self.yaml_preserve_quotes
        self.yaml.width = self.yaml_width
        self.yaml.indent(mapping=self.yaml_indent, sequence=self.yaml_indent, offset=self.yaml_indent)
        self.yaml.sort_keys = self.yaml_sort_keys

        if not os.path.exists(self.filename):
            print(f"❌ 配置文件 {self.filename} 不存在")
            self.file_exist = False
            self.file_read_success = False
        try:
            if self.file_exist:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.config = self.yaml.load(f)

        except Exception as e:
            print(f"❌ 读取文件时出错: {e}")
            self.file_read_success = False

    # 不定长参数获取yaml值
    def read_value(self, *keys, default=None):
        """
            通过不定长参数获取嵌套的YAML值

            Args:
                self.config: YAML配置字典
                *keys: 不定长参数，表示嵌套的键路径
                default: 默认值，当键不存在时返回

            Returns:
                配置值或默认值

            Example:
                read_value('database', 'host')  # 获取 config['database']['host']
                read_value('server', 'port', default=8080)  # 带默认值
            """
        current = self.config
        try:
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return default
            return current
        except (KeyError, TypeError):
            return default

    def read_with_type_conversion(self, *keys, default=None, convert_to=None):
        """
        读取配置值并进行类型转换

        Args:
            self.config: 配置字典
            *keys: 键路径
            default: 默认值
            convert_to: 转换的目标类型 (int, float, bool, str, list)

        Returns:
            转换后的值
        usage:
            port = read_with_type_conversion('database', 'port', convert_to=int, default=3306)
        """
        value = self.read_value(*keys, default=default)

        if convert_to and value is not None:
            try:
                if convert_to == bool:
                    if isinstance(value, str):
                        return value.lower() in ('true', '1', 'yes', 'on')  #如果值包含这些字符串，就认为是True
                    return bool(value)
                elif convert_to == int:
                    return int(value)
                elif convert_to == float:
                    return float(value)
                elif convert_to == str:
                    return str(value)
                elif convert_to == list:
                    if isinstance(value, str):
                        return [item.strip() for item in value.split(',')]
                    return list(value) if hasattr(value, '__iter__') else [value]
                else:
                    return convert_to(value)
            except (ValueError, TypeError):
                return default

        return value


    def read_with_validation(self, *keys, default=None, validator=None):
        """
        读取配置值并验证

        Args:
            self.config: 配置字典
            *keys: 键路径
            default: 默认值
            validator: 验证函数，返回True表示有效

        Returns:
            验证通过的值，否则返回默认值

        usage:
            # 验证端口号范围
            valid_port = read_with_validation('server', 'port',
                default=8080,
                validator=lambda x: isinstance(x, int) and 1 <= x <= 65535
            )

            # 验证日志级别
            valid_log_level = read_with_validation('logging', 'level',
                default='INFO',
                validator=lambda x: x in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            )
        """
        value = self.read_value(*keys, default=default)

        if validator and not validator(value):
            print(f"⚠️ 配置值验证失败: {'.'.join(keys)} = {value}")
            return default

        return value

    # 保留注释的写入
    def write_value(self, *keys, value: Any = None) -> bool:
        """
        通过不定长参数设置嵌套的YAML值
        Args:
            self.config: YAML配置字典
            *keys: 不定长参数，表示嵌套的键路径
            value: 要写入的值
        Example:
            # 写入简单值
            write_value('database', 'host', value='localhost')
            # 写入复杂值
            write_value('database', 'settings', value={'port': 3306, 'timeout': 30})
        """
        if not keys:
            raise ValueError("至少需要一个键")

        current = self.config

        # 创建嵌套结构
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]

        # 设置最终值
        current[keys[-1]] = value

        # 写入YAML文件
        try:
            with open(self.filename, 'w', encoding=self.yaml_encoding) as f:
                self.yaml.dump(self.config, f)
            print(f"成功写入信息[{value}]到路径{keys}（ {self.filename}文件）(保留注释)")
            return True
        except Exception as e:
            print(f"写入文件时出错: {e}")
            self.file_write_success = False
            return False


# 使用增强的字典类访问yaml的信息

class ConfigDict(dict):
    """增强的字典类，支持点符号访问和嵌套获取"""
    """
    使用方法如下：
    yml = RwYaml(filename = 'config.yml')
    if yml.file_read_success:
    # 读取配置表成功，才能进行操作
        conf_dict = ConfigDict(yml.config)  # 从config.yml文件中读取的配置信息
        print(f"App名称: {config_dict.app.name}")  # 点符号访问
        print(f"数据库端口: {config_dict['database']['port']}")  # 字典访问
        print(f"嵌套获取: {config_dict.get_nested('database.host')}")
        config_dict.set_nested('new.nested.value', 'test')
        print(f"新设置的值: {config_dict.get_nested('new.nested.value')}")
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 递归转换嵌套字典
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = ConfigDict(value)

    def __getattr__(self, key):
        """支持点符号访问"""
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        """支持点符号设置"""
        if isinstance(value, dict):
            value = ConfigDict(value)
        self[key] = value

    def get_nested(self, path: str, default: Any = None) -> Any:
        """获取嵌套值，支持点分隔路径"""
        keys = path.split('.')
        current = self

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    # def get_sub_nested(self, path: str, default: Any = None):

    def set_nested(self, path: str, value: Any) -> None:
        """设置嵌套值"""
        keys = path.split('.')
        current = self

        for key in keys[:-1]:
            if key not in current:
                current[key] = ConfigDict()
            current = current[key]

        current[keys[-1]] = value

    @classmethod
    def from_yaml(cls, file_path: str) -> 'ConfigDict':
        """从YAML文件加载"""
        yaml = YAML(typ='safe')
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.load(f) or {}
        return cls(data)

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