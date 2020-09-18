# -*- coding: utf-8 -*-
import json
from flask import current_app, jsonify, request, g
from ihome import db, constants, redis_store
from ihome.api_1_0 import api
from ihome.models import Area, House, Facility, HouseImage
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


@api.route("/house/info", methods=["POST"])
@login_required
def save_house_info():
    """保存房屋基本信息"""
    # 获取数据
    user_id = g.user_id
    houses = request.get_data()
    if not houses:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    house_data = json.loads(houses)

    title = house_data.get("title")  # 房屋名称标题
    price = house_data.get("price")  # 房屋单价
    area_id = house_data.get("area_id")  # 房屋所属城区的编号
    address = house_data.get("address")  # 房屋地址
    room_count = house_data.get("room_count")  # 房屋包含的房间数目
    acreage = house_data.get("acreage")  # 房屋面积
    unit = house_data.get("unit")  # 房屋布局（几室几厅)
    capacity = house_data.get("capacity")  # 房屋容纳人数
    beds = house_data.get("beds")  # 房屋卧床数目
    deposit = house_data.get("deposit")  # 押金
    min_days = house_data.get("min_days")  # 最小入住天数
    max_days = house_data.get("max_days")  # 最大入住天数

    if not all([
        title, price, area_id, address, room_count, acreage,
        unit, capacity, beds, deposit, min_days, max_days
    ]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断金额是否正确
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="房屋单价或者押金填写错误")

    # 判断城区id是否存在
    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询城区信息数据库异常")
    if not area:
        return jsonify(errno=RET.PARAMERR, errmsg="城区信息有误")

    # 保存房屋信息
    house = House(
        user_id = user_id,
        area_id = area_id,
        title = title,
        price = price,
        address = address,
        room_count = room_count,
        acreage = acreage,
        unit = unit,
        capacity = capacity,
        beds = beds,
        deposit = deposit,
        min_days = min_days,
        max_days = max_days
    )

    # 处理房屋设施信息
    facility_id_l = house_data.get("facility")
    if facility_id_l:
        try:
            # sql: select * from table_name where fac_id in []
            facilities = Facility.query.filter(Facility.fac_id.in_([int(i) for i in facility_id_l])).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询设施信息数据库异常")
        if facilities:
            house.facilities = facilities

    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存房屋信息失败")

    return jsonify(errno=RET.OK, errmsg="OK", data={"house_id": house.house_id})


@api.route('/house/image', methods=["POST"])
@login_required
def save_house_image():
    """
    保存房屋图片信息
    :param: image, house_id
    :return:
    """
    image_file = request.files.get("house_image")
    house_id = request.form.get("house_id")

    if not all([image_file, house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 判断house_id是否存在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询房屋信息错误")
    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    # 上传七牛云
    img_data = image_file.read()
    try:
        image_name = storage(img_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片失败")

    # 保存图片信息到数据库
    house_image = HouseImage(
        house_id=house_id,
        url=image_name
    )
    db.session.add(house_image)

    # 设置房屋主图片
    if not house.index_image_url:
        house.index_image_url = image_name
        db.session.add(house)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片数据异常")

    image_url = constants.QINIU_URL_DOMAIN + image_name

    return jsonify(errno=RET.OK, errmsg="OK", data={"image_url": image_url})

