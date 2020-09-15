# -*- coding: utf-8 -*-
from flask import current_app, jsonify, request, g
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

