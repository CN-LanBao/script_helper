# @Time     : 2022/4/2 17:32
# @Author   : ShenYiFan
# -*- coding: utf-8 -*-
import os
import subprocess
import time
from tkinter import END
from core import util


class TestBase(object):

    def __init__(self, home_page):
        # 主窗口
        self.home_page = home_page
        # 主窗口日志区域
        self.log_text_area = self.home_page.log_text_area
        # 配置字典
        self.config_dict = self.home_page.config_dict

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
            result = "[PASS]" if 0 == returncode else "[FAIL]"
            # 写入新日志
            self.log_text_area.insert(
                END, "{} {} {} {}\n".format(
                    time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), device_id, message, result))
            # 聚焦最后一行
            self.log_text_area.see(END)
            # 再次锁定
            self.log_text_area.configure(state="disable")
            return device_id, message, returncode
        return wrapper

    @log
    def input_keyevent(self, device_id, key=None):
        """
        执行 adb shell input keyevent 命令
        @Author: ShenYiFan
        @Create: 2022/4/2 17:46
        :param device_id: 需要执行命令的设备ID
        :param key: 输入的Key
        :return: str, str, int
        """
        cmd = "input keyevent {}".format(key)
        result = util.shell_cmd(device_id, cmd)
        return device_id, cmd, result.returncode

    def screenshot_and_pull(self, device_id):
        """
        截图并导出
        @Author: ShenYiFan
        @Create: 2022/4/14 17:59
        :param device_id: 需要执行命令的设备ID
        :return: str, str, int
        """
        # 截图
        temp_path = self.config_dict["device_temp_folder"]
        file_path = os.path.join(temp_path, time.strftime("%Y_%m_%d_%H_%M_%S.png", time.localtime()))
        # / \ 两种符号不能混用，路径格式化
        file_path = file_path.replace("\\", "/")
        _, _, return_code = self._screenshot(device_id, file_path)

        # 截图成功才继续导出
        if 0 == return_code:
            # 导出
            pull_path = self.config_dict["screenshot_folder"]
            self._pull(device_id, file_path, pull_path)

    @log
    def _screenshot(self, device_id, file_path):
        """
        截图
        @Author: ShenYiFan
        @Create: 2022/4/15 10:09
        :param device_id: 需要执行命令的设备ID
        :param file_path: 截图文件保存路径
        :return: str, str, int
        """
        cmd = "screencap {}".format(file_path)
        result = util.shell_cmd(device_id, cmd)
        if 0 != result.returncode:
            # 截图失败，打印失败信息
            return device_id, result.stderr, result.returncode
        return device_id, cmd, result.returncode

    @log
    def _pull(self, device_id, file_path, pull_path):
        """
        从设备中导出文件
        @Author: ShenYiFan
        @Create: 2022/4/15 10:16
        :param device_id: 需要执行命令的设备ID
        :param file_path: 设备内文件路径
        :param pull_path: 导出本地路径
        :return: str, str, int
        """
        cmd = "adb -s {} pull {} {}".format(device_id, file_path, pull_path)
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True)
        return device_id, cmd, result.returncode
