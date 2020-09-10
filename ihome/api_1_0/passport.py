# -*- coding: utf-8 -*-
import json
import re
from flask import current_app, jsonify, session, request
from sqlalchemy.exc import IntegrityError
from ihome.api_1_0 import api
from ihome import redis_store, db
from ihome.models import User
from ihome.utlis.response_code import RET


@api.route("/users", methods=['POST'])
def register():
    """
    注册
    请求的参数： 手机号、短信验证码、密码、确认密码
    参数格式：json
    """

    # 获取请求的json，返回字典
    reg_data = request.get_data()
    data = json.loads(reg_data)
    mobile = data.get('mobile')
    sms_code = data.get('sms_code')
    password = data.get('password')
    password2 = data.get('password2')

    # 校验参数
    if not all([mobile, sms_code, password, password2]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 判断手机号格式
    if not re.match(r'1[3578]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")
    # 判断两次密码是否一致
    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg="两次密码输入不一致")
    # 从redis中取出真是短信验证码
    try:
        real_sms_code = redis_store.get("sms_code_{}".format(mobile))
    except Exception as e:
        current_app.logger.errer(e)
        return jsonify(errno=RET.DBERR, errmsg="读取真实短信验证码异常")
    # 短信验证码是否过时
    if not real_sms_code:
        jsonify(errno=RET.NODATA, errmsg="短信验证码过期失效")
    # 删除短信验证码，防止重复校验
    try:
        redis_store.delete("sms_code_{}".format(mobile))
    except Exception as e:
        current_app.logger.errer(e)
    # 校验短信验证码
    if sms_code != real_sms_code:
        return jsonify(errno=RET.PARAMERR, errmsg="短信验证码输入错误")

    # 判断手机号是否注册
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     current_app.logger.errer(e)
    # else:
    #     if user:
    #         return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")

    # 保存用户的注册数据到数据库
    user = User(nickname=mobile, mobile=mobile)
    # user.get_password_hash(password)
    user.password_hash = password  # 设置属性

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.errer(e)
        return jsonify(errno=RET.DATAEXIST, errmsg="手机号已存在")
    except Exception as e:
        db.session.rollback()
        current_app.logger.errer(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库异常")

    # 保存登录状态到session中
    session['nickname'] = mobile
    session['mobile'] = mobile
    session['user_id'] = user.user_id

    # 返回
    return jsonify(errno=RET.OK, errmsg="注册成功")
