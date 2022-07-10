from apscheduler.schedulers.blocking import BlockingScheduler
import log_con
import time

import yaml

import os
import sys

import send_email
import aliyun_ddns
import util.get_ipv6_from_local

logger = log_con.logger
# 发邮件需要的信息
host_server = ''  # 邮箱stmp域名
sender_mail = ''  # 发送者邮箱
pwd = ''  # 授权码
receivers_mail = []  # 接收者邮箱列表
cc_mail = []  # 抄送者邮箱列表

# 阿里云DDNS需要的信息
accessKeyId = ''
accessSecret = ''
domain = ''
name_ipv6s = ''

# 配置文件目录
eamil_yaml_path = ''
ipv6_yaml_path = ''

base_time_interval = 9999
interval = 999
model = 3

times = 0


# 初始化状态
def init():
    global eamil_yaml_path, ipv6_yaml_path
    curpath = os.getcwd()
    eamil_yaml_path = os.path.join(curpath, "conf/email.yaml")
    ipv6_yaml_path = os.path.join(curpath, "conf/ipv6.yaml")
    logger.debug("init().curpath:{}, eamil_yaml_path:{}", curpath, eamil_yaml_path)

    refresh_status()


# 从email中刷新状态
def refresh_status():
    try:
        with open(eamil_yaml_path, mode='r', encoding='utf-8') as emailFile:
            conf = yaml.safe_load(emailFile)
    except FileNotFoundError:
        logger.error("refresh_status().FileNotFoundError:没有找到文件(eamil.yaml)或读取文件失败")
        sys.exit()
    global host_server, sender_mail, pwd, receivers_mail, base_time_interval, interval, model
    global accessKeyId, accessSecret, domain, name_ipv6s

    host_server = conf['host_server']
    sender_mail = conf['sender_mail']
    pwd = conf['pwd']
    receivers_mail = conf['receivers_mail']
    logger.debug("refresh_status(). host_server:{}, sender_mail:{}, pwd:{}, receivers_mail:{}",
                 host_server, sender_mail, pwd, receivers_mail)

    accessKeyId = conf['accessKeyId']
    accessSecret = conf['accessSecret']
    domain = conf['domain']
    name_ipv6s = conf['name_ipv6s']
    logger.debug("refresh_status(). accessKeyId:{}, accessSecret:{}, domain:{}, name_ipv6s:{}",
                 accessKeyId, accessSecret, domain, name_ipv6s)

    model = conf['model']
    base_time_interval = conf['base_time_interval']
    interval = conf['interval']
    logger.debug("refresh_status(). base_time_interval:{}, interval:{}, model:{}",
                 base_time_interval, interval, model)


# 获取ipv6.yaml中的ipv6地址
def get_ipv6_from_file():
    ipv6_old_dic = {}
    try:
        with open(ipv6_yaml_path, encoding='utf-8') as f:
            ipv6_from_file = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("get_ipv6_from_file().FileNotFoundError:没有找到文件(ipv6.yaml)或读取文件失败")
        return []
    if not ipv6_from_file['ipv6']:
        return None
    for line in ipv6_from_file['ipv6']:
        for key in line:
            ipv6_old_dic[key] = line[key]

    return ipv6_old_dic


# 更新ipv6.yaml中的ipv6地址
def w_ipv6_to_file(ipv6_old_dic):
    ipv6_new_list = []
    for key in ipv6_old_dic:
        ipv6_new_list.append({key: ipv6_old_dic[key]})
    ipv6_dict = {'ipv6': ipv6_new_list}
    logger.debug("start write ipv6:{}", ipv6_new_list)
    # 写入到yaml文件
    with open(ipv6_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(ipv6_dict, f, allow_unicode=True)


# 比较ipv6地址列表
def check_ipv6(ipv6_list_from_os, ipv6_list_from_file):
    if len(ipv6_list_from_file) != len(ipv6_list_from_os):
        return False
    if ipv6_list_from_file == ipv6_list_from_os:
        return True
    return False


# 定时任务
def polling_tasks_1():
    global times, interval
    refresh_status()
    logger.debug("sz_task_1.Hello! times:{}, interval:{}", times, interval)

    times = times + 1
    if interval <= 0:
        interval = 1

    if times % interval == 0:
        ipv6_dic_from_os = util.get_ipv6_from_local.get_ipv6_from_os_v2()
        time.sleep(1)
        ipv6_dic_from_file = get_ipv6_from_file()
        if not ipv6_dic_from_file:
            result = False
        else:
            ipv6_list_from_os_com = sorted(ipv6_dic_from_os.items(), key=lambda kv: (kv[0], kv[1]))
            ipv6_list_from_file_com = sorted(ipv6_dic_from_file.items(), key=lambda kv: (kv[0], kv[1]))
            result = check_ipv6(ipv6_list_from_os_com, ipv6_list_from_file_com)
            logger.debug("sz_task_1.ipv6_list_from_os == ipv6_list_from_file:{},ipv6_list_from_os_com:{},"
                         "ipv6_list_from_file_com:{}", result, ipv6_list_from_os_com, ipv6_list_from_file_com)
        if not result:
            ipv6_list_from_os = []
            for key in ipv6_dic_from_os:
                ipv6_list_from_os.append(key+": "+ipv6_dic_from_os[key])
            email_message = {'host_server': host_server, 'sender_mail': sender_mail, 'pwd': pwd,
                             'receivers_mail': receivers_mail}
            ddns_message_ipv6s = {'accessKeyId': accessKeyId, 'accessSecret': accessSecret, 'domain': domain,
                                  'name_ipv6s': name_ipv6s}
            try:
                ipv6 = ipv6_dic_from_os['临时']
            except Exception:
                logger.error("Error: 本地临时ipv6地址获取失败:{}", Exception)
                ipv6 = None
            if model == 1:
                send_email.send_mail_task(ipv6_list_from_os, email_message)
            elif model == 2:
                ddns_result = aliyun_ddns.ddns_ipv6s(ddns_message_ipv6s, ipv6)
            elif model == 3:
                send_email.send_mail_task(ipv6_list_from_os, email_message)
                ddns_result = aliyun_ddns.ddns_ipv6s(ddns_message_ipv6s, ipv6)
            else:
                logger.error("模式选择错误，未执行任何更新ipv6操作")
                return

            if not ddns_result:
                logger.error("Error: ddns失败，建议重启网卡")
            w_ipv6_to_file(ipv6_dic_from_os)


# 定时任务
def shedu_task():
    logger.debug("shedu_task start")
    sheduler = BlockingScheduler(timezone='Asia/Shanghai')
    sheduler.add_job(polling_tasks_1, 'interval', hours=0, minutes=0, seconds=base_time_interval)
    try:
        sheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.error("Error: shedu_task end")
        pass


if __name__ == '__main__':
    init()
    shedu_task()
