# -*- coding: utf-8 -*-
import json
from flask import current_app, jsonify, request, g, session
from ihome import db, constants
from ihome.api_1_0 import api
from ihome.models import User
from ihome.utlis.response_code import RET
from ihome.utlis.commons import login_required
from ihome.utlis.image_storage import storage


@api.route("/users/avatar", methods=["POST"])
@login_required
def set_user_avatar():
    """
    设置用户头像
    参数：图片数据，用户id
    """
    # 装饰器的代码中已经将user_id保存到g对象中，所以视图中可以直接读取
    user_id = g.user_id
    image_file = request.files.get("avatar")
    if not image_file:
        return jsonify(errno=RET.PARAMERR, errmsg="未上传头像")
    img_data = image_file.read()

    # 上传七牛云
    try:
        image_name = storage(img_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传头像失败")

    # 保存文件名到数据库
    try:
        User.query.filter_by(user_id=user_id).update({"avatar_url": image_name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存头像信息失败")

    avatar_url = constants.QINIU_URL_DOMAIN + image_name

    # 返回
    return jsonify(errno=RET.OK, errmsg="头像上传成功", data={"avatar_url": avatar_url})


@api.route("/users/name", methods=["PUT"])
@login_required
def change_nickname():
    """修改用户昵称/用户名"""
    # 装饰器的代码中已经将user_id保存到g对象中，所以视图中可以直接读取
    user_id = g.user_id

    # 获取用户设置的用户昵称/用户名
    reg_data = request.get_data()
    if not reg_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    data = json.loads(reg_data)
    nickname = data.get("nickname")
    if not nickname:
        return jsonify(errno=RET.PARAMERR, errmsg="名字不能为空")

    # 保存用户昵称name，并同时判断name是否重复（利用数据库的唯一索引)
    try:
        User.query.filter_by(user_id=user_id).update({"nickname": nickname})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="设置用户名错误")

    # 修改session中nickname字段
    session["nickname"] = nickname
    return jsonify(errno=RET.OK, errmsg="OK", data={"nickname": nickname})


@api.route("/user", methods=["GET"])
@login_required
def get_user_info():
    """获取用户个人信息"""
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    if not user:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")

    return jsonify(errno=RET.OK, errmsg="OK", data=user.user_to_dic())


@api.route("/users/auth", methods=["GET"])
@login_required
def get_auth_info():
    """获取用户实名信息"""
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    if not user:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")

    return jsonify(errno=RET.OK, errmsg="OK", data=user.auth_to_dic())


@api.route("/users/auth", methods=["POST"])
@login_required
def set_auth_info():
    """设置实名认证信息"""
    user_id = g.user_id

    # 获取用户设置的实名信息
    reg_data = request.get_data()
    if not reg_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    data = json.loads(reg_data)
    real_name = data.get("real_name")
    id_card = data.get("id_card")

    # 校验
    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 保存实名认证信息
    try:
        User.query.filter_by(user_id=user_id, real_name=None, id_card=None) \
            .update({"real_name": real_name, "id_card": id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存用户实名信息失败")

    return jsonify(errno=RET.OK, errmsg="OK")
