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

# 城区信息redis缓存过期时间，单位：秒
AREA_REDIS_CACHE_EXPIRE = 7200

# 七牛云域名
QINIU_URL_DOMAIN = "http://qgoudoubx.hd-bkt.clouddn.com/"

# 首页展示最多的房屋数量
HOME_INDEX_MAX_HOUSES = 5

# 首页房屋数据的Redis缓存时间，单位：秒
HOME_HOUSES_REDIS_EXPIRE = 7200

# 房屋详情页面数据Redis缓存时间，单位：秒
HOUSE_DETAIL_REDIS_EXPIRE = 7200

# 房屋详情页展示的评论最大数
HOUSE_DETAIL_COMMENT_MAX_COUNTS = 30



