from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.header import Header
import log_con

logger = log_con.logger


# 发送ipv6地址到指定邮箱
def send_mail_task(ipv6_list, email_message):
    host_server = email_message['host_server']
    sender_mail = email_message['sender_mail']
    pwd = email_message['pwd']
    receivers_mail = email_message['receivers_mail']
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
        logger.debug("smtp.quit()")
        smtp.quit()
