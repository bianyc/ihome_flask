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


class CCP(object):
    """自己封装的发送短信的类"""

    # 用来保存CCP类属性
    instance = None

    def __new__(cls):
        # 判断CCP类有没有已经创建好的类，如果有，则返回，没有则创建
        if not cls.instance:
            obj = CCP()
            # 初始化SDK
            obj.sdk = SmsSDK(accId, accToken, appId)
            cls.instance = obj
        return cls.instance

    def send_message(self):
        tid = '容联云通讯创建的模板'
        mobile = '手机号1,手机号2'
        datas = ('变量1', '变量2')
        resp = self.sdk.sendMessage(tid, mobile, datas)
        print(resp)
