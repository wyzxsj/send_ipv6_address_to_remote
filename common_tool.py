import ctypes
import sys
import subprocess
import psutil

import log_con

logger = log_con.logger


def get_netcard():
    netcard_names = []
    info = psutil.net_if_addrs()
    for k, v in info.items():
        if len(v) > 4:
            netcard_names.append(k)

    return netcard_names


def is_admin():
    try:
        result = ctypes.windll.shell32.IsUserAnAdmin()
        print(result)
        return result
    except:

        logger.error("Error: 管理员权限获取失败", Exception)
        return False


def restart_netcard():
    netcard_names = get_netcard()
    if is_admin():  # 这里写入需要管理员权限执行的操作
        for netcard_name in netcard_names:   # 如果网卡是开启的，就先关闭它
            enabled = "netsh interface set interface " + netcard_name + " enabled"
            disabled = "netsh interface set interface " + netcard_name + " disabled"
            if psutil.net_if_addrs()[netcard_name].isup:
                subprocess.run(disabled, shell=True, stdout=subprocess.PIPE)
            subprocess.run(enabled, shell=True, stdout=subprocess.PIPE)

    else:
        print('failed')
        if sys.version_info[0] == 3:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)


restart_netcard()
