# @Time     : 2022/4/2 15:11
# @Author   : ShenYiFan
# -*- coding: utf-8 -*-
import os
import sys
import time
import threading
import tkinter
from tkinter import ttk
from tkinter import scrolledtext
from tkinter.filedialog import askdirectory
from core import util
from core.test_base import TestBase


class HomePage(tkinter.Tk):

    def __init__(self):
        # 构建主窗口
        super().__init__()
        self.title("测试助手")

        # 基础信息字典(log 保存路径、截图和录像保存路径)
        self.config_dict = {
            "log_folder": os.path.dirname(os.path.realpath(sys.argv[0])),
            "screenshot_folder": os.path.dirname(os.path.realpath(sys.argv[0])),
            "device_temp_folder": "storage/emulated/0"
        }

        # 获取 PC 显示参数
        self.pc_width, self.pc_height = self.winfo_screenwidth(), self.winfo_screenheight()

        # 主窗口总布局（左：功能区，右：日志区）
        self._fixed_window(self, 0.6, 0.6)
        # 限制功能区框架大小
        self.function_part, self.log_part = \
            tkinter.LabelFrame(self, borderwidth=0, width=690, height=self.pc_height * 0.6), \
            tkinter.LabelFrame(self, borderwidth=0)
        self.function_part.grid(row=0, column=0, sticky="n"), self.log_part.grid(row=0, column=1, sticky="n")
        # 关闭框架随内部控件改变尺寸
        self.function_part.grid_propagate(False), self.function_part.grid_propagate(False)

        # 内部构建 (依赖关系：日志区 <- 测试类 <- 功能区)
        self._build_menu()
        self._build_log_part()
        # 测试类实例
        self.test_base = TestBase(self)
        self._build_function_part()

    def _build_menu(self):
        """
        构建菜单栏
        @Author: ShenYiFan
        @Create: 2022/4/6 10:56
        :return: None
        """
        def build_settings_page():
            """
            构建设置弹窗页面
            @Author: ShenYiFan
            @Create: 2022/4/6 13:59
            :return: None
            """
            def select_folder(entry):
                """
                选取文件夹路径
                @Author: ShenYiFan
                @Create: 2022/4/6 15:47
                :param entry: 需要填充的控件
                :return: None
                """
                folder = askdirectory()
                if folder:
                    entry.delete(0, "end")
                    entry.insert(0, folder)

            def save():
                """
                确认变更，修改属性，关闭窗口
                @Author: ShenYiFan
                @Create: 2022/4/6 16:38
                :return: None
                """
                self.config_dict["log_folder"], self.config_dict["screenshot_folder"], \
                    self.config_dict["device_temp_folder"] = \
                    log_folder_entry.get(), screenshot_folder_entry.get(), temp_folder_entry.get()
                settings_page.destroy()

            # 构建设置页面
            settings_page = tkinter.Toplevel()
            settings_page.title("设置")
            # 防止选择路径时，该窗口被置于底层
            settings_page.transient(self)
            self._fixed_window(settings_page, 0.3, 0.1)

            # 构建细节信息
            ttk.Label(settings_page, text="日志保存路径：").grid(row=0, column=0)
            ttk.Label(settings_page, text=r"截图/录像保存路径：").grid(row=1, column=0)

            log_folder_entry, screenshot_folder_entry = \
                ttk.Entry(settings_page, width=50), ttk.Entry(settings_page, width=50)
            log_folder_entry.insert(0, self.config_dict["log_folder"])
            screenshot_folder_entry.insert(0, self.config_dict["screenshot_folder"])
            log_folder_entry.grid(row=0, column=1), screenshot_folder_entry.grid(row=1, column=1)

            ttk.Button(settings_page, text="路径选择",
                       command=lambda entry=log_folder_entry: select_folder(entry)).grid(row=0, column=2)
            ttk.Button(settings_page, text="路径选择",
                       command=lambda entry=screenshot_folder_entry: select_folder(entry)).grid(row=1, column=2)

            # 临时保存路径为设备内部路径，暂且只能手动填写
            ttk.Label(settings_page, text=r"设备文件临时路径：").grid(row=2, column=0)
            temp_folder_entry = ttk.Entry(settings_page, width=50)
            temp_folder_entry.grid(row=2, column=1)
            temp_folder_entry.insert(0, self.config_dict["device_temp_folder"])

            ttk.Button(settings_page, text="保存", command=save).grid(row=3, column=0, sticky=tkinter.W)
            ttk.Button(settings_page, text="取消", command=settings_page.destroy).grid(row=3, column=2, sticky=tkinter.E)

            # 聚焦
            settings_page.focus()

        def build_info_page():
            """
            构建关于弹窗页面
            @Author: ShenYiFan
            @Create: 2022/4/6 14:13
            :return: None
            """
            # 构建关于页面
            info_page = tkinter.Toplevel()
            info_page.transient(self)
            info_page.title("关于")
            self._fixed_window(info_page, 0.2, 0.075)
            # 构建细节信息
            label_list = ["日期：2022/04/15", "版本：v0.2", "作者：shenyf0921"]
            [ttk.Label(info_page, text=text).pack() for text in label_list]
            # 聚焦
            info_page.focus()

        # 创建根菜单并关联窗口
        root = tkinter.Menu(self)
        self["menu"] = root
        root.add_cascade(label="设置", command=build_settings_page)
        root.add_cascade(label="关于", command=build_info_page)

    def _build_function_part(self):
        """
        构建功能区
        @Author: ShenYiFan
        @Create: 2022/4/14 15:20
        :return: None
        """
        def build_device_cbo():
            """
            构建选择设备ID的下拉框
            @Author: ShenYiFan
            @Create: 2022/4/2 16:45
            :return: None
            """
            def update_device_cbo():
                """
                间隔更新设备ID
                @Author: ShenYiFan
                @Create: 2022/4/2 16:47
                :return: None
                """
                while True:
                    time.sleep(5)
                    cur_value, self.device_cbo["value"] = self.device_cbo.get(), util.get_device_ids()
                    # 所选设备仍在连接，仅更新备选值；所选设备不在连接，更新备选值且置空当前值
                    # TODO: 弹窗提示断连
                    if cur_value not in self.device_cbo["value"]:
                        self.device_cbo.set("")

            # 创建总框架
            device_group = tkinter.LabelFrame(self.function_part, borderwidth=0)
            device_group.grid(row=0, sticky="W")
            ttk.Label(device_group, text="设备 ID：").grid(row=0, column=0)
            self.device_cbo = ttk.Combobox(master=device_group, width=30)
            self.device_cbo.grid(row=0, column=1)

            # 每十秒更新一次下拉框
            update_td = threading.Thread(target=update_device_cbo)
            update_td.daemon = True
            update_td.start()

        def build_test_btn():
            """
            构建测试按键
            @Author: ShenYiFan
            @Create: 2022/4/12 11:09
            :return: None
            """
            def build_simulate_group():
                """
                构建模拟按键部分
                @Author: ShenYiFan
                @Create: 2022/4/12 17:54
                :return: None
                """
                # 创建总框架
                simulate_group = tkinter.LabelFrame(self.function_part, borderwidth=0)
                simulate_group.grid(row=2, column=0)
                # 创建所有的模拟按键按钮
                simulate_btn = \
                    [ttk.Button(simulate_group, text=name, width=15,
                                command=lambda key=key_code: self.test_base.input_keyevent(self.device_cbo.get(), key))
                     for key_code, name in self.test_base.keyevent_dict.items()]
                # 设置模拟按键布局，按键自动换行
                for index, btn in enumerate(simulate_btn):
                    btn.grid(row=int(index / 6), column=index % 6)
                # 创建显示/隐藏按钮
                ttk.Button(self.function_part, text="模拟按键(keyevent)", width=32,
                           command=
                           lambda widgets=[simulate_group]: self._switch_display(widgets)).grid(row=1, column=0,
                                                                                                sticky="W")

            def build_screen_group():
                """
                构建截屏录屏按键
                @Author: ShenYiFan
                @Create: 2022/4/12 18:17
                :return:
                """
                # 创建总框架
                screen_group = tkinter.LabelFrame(self.function_part, borderwidth=0)
                screen_group.grid(row=4, column=0, sticky="W")
                # 截图并导出按键
                ttk.Button(screen_group, text="截图并导出", width=15,
                           command=
                           lambda: self.test_base.screenshot_and_pull(self.device_cbo.get())).grid(row=0, column=0)
                # 创建显示/隐藏按钮
                ttk.Button(self.function_part, text="录屏/截图", width=32,
                           command=
                           lambda widgets=[screen_group]: self._switch_display(widgets)).grid(row=3, column=0,
                                                                                              sticky="W")

            # 构建模拟按键按钮
            build_simulate_group()
            # 构建截屏录屏按键
            build_screen_group()

        # 构建设备选择下拉框
        build_device_cbo()
        # 构建测试按键
        build_test_btn()

    def _build_log_part(self):
        """
        构建日志区域
        @Author: ShenYiFan
        @Create: 2022/4/13 16:58
        :return: None
        """
        def clear_log():
            """
            清空所有日志
            @Author: ShenYiFan
            @Create: 2022/4/14 10:49
            :return: None
            """
            # 需要先解锁再删除
            self.log_text_area.configure(state="normal")
            self.log_text_area.delete("1.0", tkinter.END)
            self.log_text_area.configure(state="disabled")

        # 标题与按键组
        ttk.Label(self.log_part, text="运行日志：").grid(row=0, column=0, sticky="W")
        ttk.Button(self.log_part, text="清空日志 🧺", command=clear_log).grid(row=0, column=1, sticky="e")
        # 日志区域
        self.log_text_area = scrolledtext.ScrolledText(self.log_part, width=63, height=47)
        self.log_text_area.grid(row=1, column=0, columnspan=2), self.log_text_area.configure(state="disabled")

    def _fixed_window(self, window, width_ratio, height_ratio):
        """
        修改窗口大小并置于屏幕中间
        @Author: ShenYiFan
        @Create: 2022/4/2 15:54
        :param window: 窗口对象
        :param width_ratio: 相对于PC的横向比例
        :param height_ratio: 相对于PC的纵向比例
        :return: None
        """
        pc_width, pc_height = self.winfo_screenwidth(), self.winfo_screenheight()
        # 计算窗口大小和居中坐标
        win_width, win_height = int(pc_width * width_ratio), int(pc_height * height_ratio)
        win_xAxis, win_yAxis = int((pc_width - win_width) / 2), int((pc_height - win_height) / 2)
        # 修正窗口大小和居中 (widthxheight+x+y)
        window.geometry("{}x{}+{}+{}".format(win_width, win_height, win_xAxis, win_yAxis))
        # 禁止修改窗口大小
        window.resizable(False, False)

    @staticmethod
    def _switch_display(widgets):
        """
        将指定的页面元素（限 grid 布局）显示或隐藏
        @Author: ShenYiFan
        @Create: 2022/4/12 13:18
        :return: None
        """
        for widget in widgets:
            if widget.grid_info():
                widget.grid_remove()
            else:
                widget.grid()

    def device_id_check(self):
        """
        检查 Device ID 是否为空，若空则弹窗提示
        @Author: ShenYiFan
        @Create: 2022/4/14 14:15
        :return: bool
        """
        def build_warning_page():
            """
            构建警告弹窗
            @Author: ShenYiFan
            @Create: 2022/4/14 14:38
            :return: None
            """
            def unlock_and_destroy():
                """
                解锁主窗口并关闭警告弹窗
                @Author: ShenYiFan
                @Create: 2022/4/14 14:59
                :return:
                """
                # 解锁主窗口
                self.attributes("-disabled", 0)
                warning_page.destroy()

            # 禁用主窗口
            self.attributes("-disabled", 1)
            # 创建临时弹窗
            warning_page = tkinter.Toplevel()
            warning_page.transient(self)
            # 构建弹窗信息
            warning_page.title("警告！")
            self._fixed_window(warning_page, 0.15, 0.05)
            ttk.Label(warning_page, text="设备 ID 为空！请选择设备后再操作！").pack()
            confirm_btn = ttk.Button(warning_page, text="我已知晓", command=unlock_and_destroy)
            confirm_btn.pack()
            # 重新绑定窗口关闭事件，防止无法正常解锁主窗口
            warning_page.protocol("WM_DELETE_WINDOW", unlock_and_destroy)

            # 聚焦
            warning_page.focus()

        if not self.device_cbo.get():
            build_warning_page()
        return bool(self.device_cbo.get())


a = HomePage()
a.mainloop()
