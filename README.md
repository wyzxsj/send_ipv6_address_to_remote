# send_ipv6_address_to_remote
windows下检测本计算机ipv6地址，并将更新的ipv6地址发到指定邮箱

1、使用pyinstaller工具将py文件打包成exe文件

pip install pyinstaller
然后打包exe文件

pyinstaller -F send_email.py

2、把dist目录下的exe文件和模板目录下的两个文件拷贝到执行目录

3、配置email.yaml文件并执行exe就会自动检测本机ipv6地址，并将更新的ipv6地址发到指定邮箱
