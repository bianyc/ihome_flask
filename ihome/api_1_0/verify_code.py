# -*- coding: utf-8 -*-
import random
from flask import current_app, jsonify, make_response, request
from ihome.api_1_0 import api
from ihome import redis_store, constants
from ihome.models import User
from ihome.utlis.captcha.captcha import captcha
from ihome.utlis.response_code import RET
from ihome.libs.yuntongxun.send_message import send_message


# 127.0.0.1/api/v1.0/image_codes/<image_code_id>
@api.route('/image_codes/<image_code_id>')
def get_image_code(image_code_id):
    """
    获取图片验证码
    :parameter image_code_id: 验证码编号
    :return: 正常：返回图片  异常：返回json（异常信息）
    """
    # 业务逻辑处理
    # 获取图片
    text, img_data = captcha.captcha()

    # 将验证码真实值和对应编号存入Redis，设置期限
    # 单条维护记录，使用字符串存储
    # redis_store.set("img_code_{}".format(image_code_id), text)
    # redis_store.expire("img_code_{}".format(image_code_id), constants.IMG_CODE_REDIS_EXPIRE)
    # 存储并同时设置过期时间     编号                                过期时间                     真实值
    try:
        redis_store.setex("img_code_{}".format(image_code_id), constants.IMG_CODE_REDIS_EXPIRE, text)
    except Exception as e:
        current_app.logger.errer(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码失败")

    # 返回值
    resp = make_response(img_data)
    resp.headers['Content-Type'] = "image/png"
    return resp


# 127.0.0.1/api/v1.0/sms_codes/<mobile>?image_code=&image_code_id=
@api.route("/sms_codes/<re(r'1[3578]\d{9}'):mobile>")
def get_sms_code(mobile):
    """获取短信验证码"""
    # 获取参数
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")

    # 校验参数
    if not all([image_code, image_code_id]):
        # 参数不完整
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 业务逻辑处理
    # 1.Redis中取出真是验证码值
    try:
        real_img_code = redis_store.get("img_code_{}".format(image_code_id))
    except Exception as e:
        current_app.logger.errer(e)
        return jsonify(errno=RET.DBERR, errmsg="Redis数据库异常")
    # 2.判断图片验证码是否过期
    if not real_img_code:
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码失效")
    # 删除Redis图片验证码，防止同一图片重复验证
    try:
        redis_store.delete("img_code_{}".format(image_code_id))
    except Exception as e:
        current_app.logger.errer(e)
    # 3.与用户填写的值进行对比
    if str(real_img_code, encoding='utf-8').lower() != image_code.lower():
        # 表示用户输入图片验证码错误
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")
    # 判断60s内是否向该手机发送过短信
    try:
        send_status = redis_store.get("send_mobile_{}".format(mobile))
    except Exception as e:
        current_app.logger.errer(e)
    else:
        if send_status:
            return jsonify(errno=RET.REQERR, errmsg="请求过于频繁，请60s后重试")
    # 4.判断手机号是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.errer(e)
    else:
        if user:
            return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")
    # 5.如果手机号不存在，则生成短信验证码
    sms_code = "%06d" % random.randint(0, 999999)
    # 6.保存真实验证码
    try:
        redis_store.setex("sms_code_{}".format(mobile), constants.SMS_CODE_REDIS_EXPIRE, sms_code)
        # 该手机号发送短信的记录，防止其60s内重复发送
        redis_store.setex("send_mobile_{}".format(mobile), constants.SEND_SMS_REDIS_EXPIRE, 1)
    except Exception as e:
        current_app.logger.errer(e)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码失败")

    # 发送短信
    time = str(int(constants.SMS_CODE_REDIS_EXPIRE / 60))
    try:
        status = send_message(str(mobile), sms_code, time)
    except Exception as e:
        current_app.logger.errer(e)
        return jsonify(errno=RET.THIRDERR, errmsg="发送异常")

    # 返回值
    if status == 0:
        return jsonify(errno=RET.OK, errmsg="发送成功")
    else:
        return jsonify(errno=RET.THIRDERR, errmsg="发送失败")
