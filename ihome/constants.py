# -*- coding: utf-8 -*-

# 图片验证码存入Redis过期时间，单位：秒
IMG_CODE_REDIS_EXPIRE = 180

# 短信验证码存入Redis过期时间，单位：秒
SMS_CODE_REDIS_EXPIRE = 300

# 手机发送短信记录
SEND_SMS_REDIS_EXPIRE = 60

# 登录错误尝试次数
LOGIN_MAX_ERROR_TIMES = 5

# 登录错误限制的时间, 单位：秒
LOGIN_ERROR_FORBID_TIME = 600

