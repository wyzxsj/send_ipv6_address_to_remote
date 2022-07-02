from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109.DescribeSubDomainRecordsRequest import DescribeSubDomainRecordsRequest
from urllib.request import urlopen
import json

import log_con

logger = log_con.logger

client = ''


def update(record_id, rr, ip_type, value):  # 修改域名解析记录
    from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
    request = UpdateDomainRecordRequest()
    request.set_accept_format('json')
    request.set_RecordId(record_id)
    request.set_RR(rr)
    request.set_Type(ip_type)
    request.set_Value(value)
    response = client.do_action_with_exception(request)


def add(record_id, rr, ip_type, value):  # 添加新的域名解析记录
    from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
    request = AddDomainRecordRequest()
    request.set_accept_format('json')
    request.set_DomainName(record_id)
    request.set_RR(rr)  # https://blog.zeruns.tech
    request.set_Type(ip_type)
    request.set_Value(value)
    response = client.do_action_with_exception(request)


def ddns_ipv6s(ddns_message_ipv6s):
    accessKeyId = ddns_message_ipv6s['accessKeyId']
    accessSecret = ddns_message_ipv6s['accessSecret']
    domain = ddns_message_ipv6s['domain']
    name_ipv6s = ddns_message_ipv6s['name_ipv6s']
    for name_ipv6 in name_ipv6s:
        ddns_message_ipv6 = {'accessKeyId': accessKeyId, 'accessSecret': accessSecret, 'domain': domain,
                        'name_ipv6': name_ipv6}
        try:
            ddns_ipv6(ddns_message_ipv6)
        except Exception:
            logger.error("Error: ddns获取本机对外ipv6地址失败:{}", Exception)
            return False


def ddns_ipv6(ddns_message_ipv6):
    global client
    accessKeyId = ddns_message_ipv6['accessKeyId']
    accessSecret = ddns_message_ipv6['accessSecret']
    domain = ddns_message_ipv6['domain']
    name_ipv6 = ddns_message_ipv6['name_ipv6']
    client = AcsClient(accessKeyId, accessSecret, 'cn-hangzhou')

    request = DescribeSubDomainRecordsRequest()
    request.set_accept_format('json')
    request.set_DomainName(domain)
    request.set_SubDomain(name_ipv6 + '.' + domain)
    request.set_Type("AAAA")
    response = client.do_action_with_exception(request)  # 获取域名解析记录列表
    domain_list = json.loads(response)  # 将返回的JSON数据转化为Python能识别的
    try:
        ip = urlopen('https://api-ipv6.ip.sb/ip').read()  # 使用IP.SB的接口获取ipv6地址
    except Exception:
        logger.error("Error: ddns获取本机对外ipv6地址失败:{}", Exception)
        return False
    ipv6 = str(ip, encoding='utf-8')
    logger.debug("get_domain_message(). accessKeyId:{}, accessSecret:{}, domain:{}, name_ipv6:{}, ipv6{}",
                 accessKeyId, accessSecret, domain, name_ipv6, ipv6)
    if domain_list['TotalCount'] == 0:
        add(domain, name_ipv6, "AAAA", ipv6)
        logger.info("新建域名解析成功")
    elif domain_list['TotalCount'] == 1:
        if domain_list['DomainRecords']['Record'][0]['Value'].strip() != ipv6.strip():
            update(domain_list['DomainRecords']['Record'][0]['RecordId'], name_ipv6, "AAAA", ipv6)
            logger.info("修改域名解析成功")
        else:  # https://blog.zeruns.tech
            logger.info("IPv6地址没变")
    elif domain_list['TotalCount'] > 1:
        from aliyunsdkalidns.request.v20150109.DeleteSubDomainRecordsRequest import DeleteSubDomainRecordsRequest
        request = DeleteSubDomainRecordsRequest()
        request.set_accept_format('json')
        request.set_DomainName(domain)
        request.set_RR(name_ipv6)  # https://blog.zeruns.tech
        request.set_Type("AAAA")
        response = client.do_action_with_exception(request)
        add(domain, name_ipv6, "AAAA", ipv6)
        logger.info("修改域名解析成功")
