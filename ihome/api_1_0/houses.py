# -*- coding: utf-8 -*-
import json
from flask import current_app, jsonify, request, g
from ihome import db, constants, redis_store
from ihome.api_1_0 import api
from ihome.models import Area
from ihome.utlis.response_code import RET
from ihome.utlis.commons import login_required
from ihome.utlis.image_storage import storage

@api.route("/areas")
def get_area_info():
    """获取城区信息"""
    # 从redis读取数据
    try:
        resp_json = redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            current_app.logger.info("area_info from redis success")
            return resp_json, 200, {"Content-Type": "application/json"}

    # 查询数据库，读取城区信息
    try:
        area_list = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    area_info = []
    # 将对象转换为字典
    for area in area_list:
        area_info.append(area.to_dic())

    # 将数据转换为json数据
    resp_dic = dict(errno=RET.OK, errmsg="OK", data=area_info)
    resp_json = json.dumps(resp_dic, ensure_ascii=False)

    # 保存到redis缓存
    try:
        redis_store.setex("area_info", constants.AREA_REDIS_CACHE_EXPIRE, resp_json)
    except Exception as e:
        current_app.logger.error(e)

    return resp_json, 200, {"Content-Type": "application/json"}
