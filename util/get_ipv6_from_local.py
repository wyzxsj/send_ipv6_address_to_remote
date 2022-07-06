import socket

import subprocess
import log_con

logger = log_con.logger


# 获取当前系统ipv6地址(新)
def get_ipv6_from_os_v2():
    ipv6_new_dic = {}
    proc = subprocess.Popen("netsh interface ipv6 show address",
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, encoding="gbk")
    for line in iter(proc.stdout.readline, 'b'):
        if '公用' in line or '临时' in line:
            if '首选项' in line:
                ipv6_new_dic[line.split()[0]] = line.split()[4]
        print(line.split())
        if not subprocess.Popen.poll(proc) is None:
            if line == "":
                break
    proc.stdout.close()
    logger.debug("get_ipv6(), ipv6_data: {}", ipv6_new_dic)
    return ipv6_new_dic


# 获取当前系统ipv6地址(老)
def get_ipv6_from_os_v1():
    addrs = socket.getaddrinfo(socket.gethostname(), None)
    ipv6_new_list = []
    for item in addrs:
        if item[4][0].startswith("240e"):
            ipv6_new_list.append(item[4][0])
    # if len(ipv6_new_list) > 2:
    #     logger.error("ERROR: 系统ipv6地址异常，建议重启网卡")
    #     return get_ipv6_from_file()
    return ipv6_new_list


get_ipv6_from_os_v2()
