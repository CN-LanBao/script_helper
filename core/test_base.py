# @Time     : 2022/4/2 17:32
# @Author   : ShenYiFan
# -*- coding: utf-8 -*-
import time
from tkinter import END
import util


class TestBase(object):

    def __init__(self, home_page):
        # 主窗口
        self.home_page = home_page
        # 主窗口日志区域
        self.log_text_area = self.home_page.log_text_area
        # 模拟按键字典
        self.keyevent_dict = {
            "5": "CALL", "6": "ENDCALL", "3": "HOME", "82": "MENU", "4": "BACK",
            "84": "SEARCH", "27": "CAMERA", "80": "FOCUS", "26": "POWER", "83": "NOTIFICATIO",
            "91": "MUTE", "164": "VOLUME_MUTE", "24": "VOLUME_UP", "25": "VOLUME_DOWN", "66": "ENTER",
            "111": "ESCAPE", "23": "DPAD_CENTER", "19": "DPAD_UP", "20": "DPAD_DOWN", "21": "DPAD_LEFT",
            "22": "DPAD_RIGHT", "122": "MOVE_HOME", "123": "MOVE_END", "92": "PAGE_UP", "93": "PAGE_DOWN",
            "67": "DEL", "112": "FORWARD_DEL", "124": "INSERT", "61": "TAB", "143": "NUM_LOCK",
            "115": "CAPS_LOCK", "121": "BREAK", "116": "SCROLL_LOCK", "168": "ZOOM_IN", "169": "ZOOM_OUT"
        }
        pass

    def log(func):
        """
         装饰器，写入log控件
         @Author: ShenYiFan
         @Create: 2022/4/14 11:16
         :return: None
         """
        def wrapper(self, *args, **kwargs):
            # 先检查 device id 是否存在
            if self.home_page.device_id_check():
                # 接受返回信息，写入日志区域
                device_id, message, returncode = func(self, *args, **kwargs)
            else:
                # 缺少设备 ID，打印一下日志
                device_id, message, returncode = "", "设备 ID 为空！请选择设备后再操作！", -1

            # 解锁才能写入
            self.log_text_area.configure(state="normal")
            # 非 0 皆为 FAIL
            returncode = "PASS" if 0 == returncode else "FAIL"
            # 写入新日志
            self.log_text_area.insert(
                END, "{} {} {} {}\n".format(
                    time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), device_id, message, returncode))
            # 聚焦最后一行
            self.log_text_area.see(END)
            # 再次锁定
            self.log_text_area.configure(state="disable")
        return wrapper

    @log
    def input_keyevent(self, device_id, key=None):
        """
        执行 adb shell input keyevent 命令
        @Author: ShenYiFan
        @Create: 2022/4/2 17:46
        :param device_id: 需要执行命令的设备ID
        :param key: 输入的Key
        :return: int
        """
        cmd = "input keyevent {}".format(key)
        result = util.shell_cmd(device_id, cmd)
        return device_id, cmd, result.returncode

    # def
