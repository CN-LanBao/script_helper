# @Time     : 2022/4/2 16:14
# @Author   : ShenYiFan
# -*- coding: utf-8 -*-
import subprocess


def shell_cmd(device_id, cmd):
    """
    在指定设备 shell 中执行命令
    @Author: ShenYiFan
    @Create: 2022/4/2 17:58
    :param device_id: 需要执行命令的设备ID
    :param cmd: 需要执行的命令
    :return: object
    """
    run_result = subprocess.run("adb -s {} shell {}".format(device_id, cmd), shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return run_result


def get_device_ids():
    """
    获取设备ID列表
    @Author: ShenYiFan
    @Create: 2022/4/2 17:51
    :return: list
    """
    cmd = "adb devices | findstr /E device"
    run_out = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout.splitlines()
    device_ids = [info.split()[0] for info in run_out]
    return device_ids
