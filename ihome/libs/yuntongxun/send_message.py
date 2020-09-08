# -*- coding: utf-8 -*-
import re
from ihome.libs.yuntongxun.SmsSDK import SmsSDK


# accId = '容联云通讯分配的主账号ID'
# accToken = '容联云通讯分配的主账号TOKEN'
# appId = '容联云通讯分配的应用ID'
#
#
# def send_message():
#     sdk = SmsSDK(accId, accToken, appId)
#     tid = '容联云通讯创建的模板'
#     mobile = '手机号1,手机号2'
#     datas = ('变量1', '变量2')
#     resp = sdk.sendMessage(tid, mobile, datas)
#     print(resp)
#
#
# send_message()


accId = '8aaf07086010a0eb016036566f1c10e1'
accToken = '1223d13a009747efbf371665582bd0d8'
appId = '8aaf07086010a0eb016036566f7010e8'


def send_message(mobile, sms_code, time):
    sdk = SmsSDK(accId, accToken, appId)
    tid = '1'
    # mobile = '15510119848'
    data = (sms_code, time)
    resp = sdk.sendMessage(tid, mobile, data)
    re_find = re.findall(r'{"statusCode":"(.*?)",', resp)
    if re_find:
        status_code = str(re_find[0])
        if status_code == "000000":
            return 0
        else:
            return -1
    else:
        return -1


# if __name__ == '__main__':
#     send_message()
