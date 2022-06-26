# send_ipv6_address_to_remote
windows下检测本计算机ipv6地址，并将更新的ipv6地址发到指定邮箱


#安装必要的库和阿里云的SDK
pip install aliyun-python-sdk-core-v3
pip install aliyun-python-sdk-domain
pip install aliyun-python-sdk-alidns
pip install requests


# 源码使用方式
1、把dist目录下的exe文件和模板目录下的两个文件拷贝到执行目录conf/

2、配置email.yaml文件并运行main.py


#windows下打包发布成exe文件
1、使用pyinstaller工具将py文件打包成exe文件

`pip install pyinstaller`

然后打包exe文件

`pyinstaller -F send_email.py`

2、把dist目录下的exe文件和模板目录下的两个文件拷贝到执行目录conf/

3、配置email.yaml文件并执行exe就会自动检测本机ipv6地址，并将更新的ipv6地址发到指定邮箱或进行DDNS解析

# exe文件使用方式
下载release下的exe.zip文件，解压到任意目录，配置email.yaml文件并执行exe