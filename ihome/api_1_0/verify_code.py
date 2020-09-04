# -*- coding: utf-8 -*-
from flask import current_app, jsonify, make_response
from ihome.api_1_0 import api
from ihome import redis_store, constants
from ihome.utlis.captcha.captcha import captcha
from ihome.utlis.response_code import RET


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
        return jsonify(errno=RET.DBERR, errmsg="save image_code to redis error!")

    # 返回值
    resp = make_response(img_data)
    resp.headers['Content-Type'] = "image/png"
    return resp
