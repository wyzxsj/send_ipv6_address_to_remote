from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.header import Header
from apscheduler.schedulers.blocking import BlockingScheduler

from loguru import logger
import yaml

import socket

import os
import sys

# 添加日志记录
logger.add("info.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", level='INFO', rotation="10 MB", encoding='utf-8')
logger.add("error.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", level='ERROR', rotation="10 MB", encoding='utf-8')
#logger.add("debug.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", level='DEBUG', rotation="10 MB", encoding='utf-8')

host_server = ''    # 邮箱stmp域名
sender_mail = ''    # 发送者邮箱
pwd = ''    # 授权码
receivers_mail = []    # 接收者邮箱列表
cc_mail = []    # 抄送者邮箱列表

eamil_yaml_path = ''
ipv6_yaml_path = ''

base_time_interval = 9999
interval = 999

time = 0


# 初始化状态
def init():
    global eamil_yaml_path, ipv6_yaml_path
    curpath = os.getcwd()
    eamil_yaml_path = os.path.join(curpath, "email.yaml")
    ipv6_yaml_path = os.path.join(curpath, "ipv6.yaml")
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
    global host_server, sender_mail, pwd, receivers_mail, base_time_interval, interval
    host_server = conf['host_server']
    sender_mail = conf['sender_mail']
    pwd = conf['pwd']
    receivers_mail = conf['receivers_mail']
    logger.debug("refresh_status(). host_server:{}, sender_mail:{}, pwd:{}, receivers_mail:{}",
                host_server, sender_mail, pwd, receivers_mail)

    base_time_interval = conf['base_time_interval']
    interval = conf['interval']
    logger.debug("refresh_status(). base_time_interval:{}, interval:{}",
                base_time_interval, interval)


# 获取当前系统ipv6地址
def get_ipv6_from_os():
    addrs = socket.getaddrinfo(socket.gethostname(), None)
    ipv6_new_list = []
    for item in addrs:
        if (item[4][0].startswith("240e")):
            ipv6_new_list.append(item[4][0])

    return ipv6_new_list


# 获取ipv6.yaml中的ipv6地址
def get_ipv6_from_file():
    try:
        with open(ipv6_yaml_path, encoding='utf-8') as f:
            ipv6_from_file = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("get_ipv6_from_file().FileNotFoundError:没有找到文件(ipv6.yaml)或读取文件失败")
        return []
    ipv6_old_list = ipv6_from_file['ipv6']

    return ipv6_old_list


# 更新ipv6.yaml中的ipv6地址
def w_ipv6_to_file(ipv6_new_list):
    ipv6_dict = {'ipv6': ipv6_new_list}
    logger.debug("start write ipv6:{}", ipv6_new_list)
    # 写入到yaml文件
    with open(ipv6_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(ipv6_dict, f)


# 发送ipv6地址到指定邮箱
def send_mail_task(ipv6_list):
    logger.debug("send_mail_task(). host_server:{}, sender_mail:{}, pwd:{}, receivers_mail:{}",
                 host_server, sender_mail, pwd, receivers_mail)

    title = "最新地址"
    mail_content = '<br>'.join(ipv6_list)

    msg = MIMEText(mail_content, 'html', 'utf-8')
    msg['Subject'] = Header(title, 'utf-8')
    msg['From'] = sender_mail
    msg['To'] = ';'.join(receivers_mail)

    try:
        smtp = SMTP_SSL(host_server, 465)
        smtp.set_debuglevel(1)
        smtp.login(sender_mail, pwd)
        smtp.sendmail(sender_mail, receivers_mail, msg.as_string())
        logger.info("邮件发送成功，ipv6地址：{}", ipv6_list)
    except Exception:
        logger.error("Error: 无法发送邮件{}", Exception)
    finally:
        smtp.quit()


# 定时任务
def polling_tasks_1():
    global time, interval
    refresh_status();
    logger.debug("sz_task_1.Hello! time:{}, interval:{}", time, interval)

    time = time + 1
    if interval <= 0:
        interval = 1

    if (time%interval == 0):
        ipv6_list_from_os = get_ipv6_from_os()
        ipv6_list_from_file = get_ipv6_from_file()

        ipv6_list_from_os = sorted(ipv6_list_from_os)
        ipv6_list_from_file = sorted(ipv6_list_from_file)
        result = (ipv6_list_from_os == ipv6_list_from_file)
        logger.debug("sz_task_1.ipv6_list_from_os == ipv6_list_from_file:{},ipv6_list_from_os:{},"
                     "ipv6_list_from_file:{}", result, ipv6_list_from_os, ipv6_list_from_file)
        if not result:
            logger.debug("sz_task_1.ipv6_list_from_os:{}", ipv6_list_from_os)
            logger.debug("sz_task_1.ipv6_list_from_file:{}", ipv6_list_from_file)
            w_ipv6_to_file(ipv6_list_from_os)
            send_mail_task(ipv6_list_from_os)


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
