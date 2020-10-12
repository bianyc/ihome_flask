# -*- coding: utf-8 -*-
import json
from datetime import datetime
from flask import current_app, jsonify, request, g, session
from ihome import db, constants, redis_store
from ihome.api_1_0 import api
from ihome.models import Area, House, Facility, HouseImage, User, Order
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


@api.route("/user/houses", methods=["GET"])
@login_required
def get_user_houses():
    """获取房东发布的房源信息条目"""
    user_id = g.user_id
    try:
        # House.query.filter_by(user_id=user_id)
        user = User.query.get(user_id)
        houses = user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")
    houses_li = []
    if houses:
        for house in houses:
            houses_li.append(house.to_basic_dict())
    return jsonify(errno=RET.OK, errmsg="OK", data={"houses": houses_li})


@api.route("/houses/index", methods=["GET"])
def get_houses_index():
    """获取主页幻灯片展示的房屋基本信息"""
    try:
        ret = redis_store.get("home_page_houses")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if ret:
            current_app.logger.info("houses index info from redis success")
            return ret, 200, {"Content-Type": "application/json"}
    try:
        # 查询数据库，返回房屋订单数目最多的5条数据
        houses = House.query.order_by(House.order_count.desc()).limit(constants.HOME_INDEX_MAX_HOUSES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    if not houses:
        return jsonify(errno=RET.NODATA, errmsg="查询无数据")
    houses_list = []
    for house in houses:
        # 如果房屋未设置主图片，则跳过
        if not house.index_image_url:
            continue
        houses_list.append(house.to_basic_dict())
    # 将数据转换为json，并保存到redis缓存
    resp_dic = dict(errno=RET.OK, errmsg="OK", data=houses_list)
    resp_json = json.dumps(resp_dic, ensure_ascii=False)

    try:
        redis_store.setex("home_page_houses", constants.HOME_HOUSES_REDIS_EXPIRE, resp_json)
    except Exception as e:
        current_app.logger.error(e)

    return resp_json, 200, {"Content-Type":"application/json"}


@api.route("house/<house_id>")
def get_house_detail(house_id):
    """获取房屋详情"""
    # 前端在房屋详情页面展示时，如果浏览页面的用户不是该房屋的房东，则展示预定按钮，否则不展示
    # 所以需要后端返回登录用户的user_id
    # 尝试获取用户登录的信息，若登录，则返回给前端登录用户的user_id，否则返回user_id=-1
    user_id = session.get("user_id", "-1")

    # 校验参数
    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数缺失")

        # 先从redis缓存中获取信息
    try:
        ret = redis_store.get("house_detail_info_{}".format(house_id))
    except Exception as e:
        current_app.logger.error(e)
    else:
        if ret:
            current_app.logger.info("houses detail info from redis success")
            return ret, 200, {"Content-Type": "application/json"}

    # 查询数据库
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据库失败")
    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    # 将房屋对象数据转换为字典
    resp_dic = dict(errno=RET.OK, errmsg="OK", data={"user_id": user_id, "house": house.detail_to_dict()})
    resp_json = json.dumps(resp_dic, ensure_ascii=False)

    # 存入redis缓存
    try:
        redis_store.setex("house_detail_info_{}".format(house_id), constants.HOUSE_DETAIL_REDIS_EXPIRE, resp_json)
    except Exception as e:
        current_app.logger.error(e)

    return resp_json, 200, {"Content-Type": "application/json"}

# GET /api/v1.0/houses?sd=2017-12-01&ed=2017-12-31&aid=10&sk=new&p=1
@api.route("/houses")
def get_house_list():
    """房屋列表信息（搜索页面）"""
    start_date = request.args.get("sd", "")  # 用户想要的起始时间
    end_date = request.args.get("ed", "")  # 用户想要的结束时间
    area_id = request.args.get("aid", "")  # 区域编号
    sort_key = request.args.get("sk", "")  # 排序关键字
    page = request.args.get("p")  # 页数

    # 处理时间
    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        if start_date and end_date:
            assert start_date <= end_date
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="日期参数错误")

    # 判断area_id
    if area_id:
        try:
            area = Area.query.get(area_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询区域信息数据库异常")
        else:
            if not area:
                return jsonify(errno=RET.PARAMERR, errmsg="区域参数错误")

    # 判断page
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    redis_keys = "house_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)
    # 从redis缓存获取数据
    try:
        resp_json = redis_store.hget(redis_keys, page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            current_app.logger.info("get house info from redis success")
            return resp_json, 200, {"Content-Type": "application/json"}

    # 过滤条件的参数列表容器
    filter_params = []

    # 时间条件
    conflict_orders = None
    try:
        if start_date and end_date:
            # 查询冲突订单: select * from Order where Order.begin_date <= end_date and Order.end_date >= start_date;
            conflict_orders = Order.query.filter(Order.begin_date <= end_date, Order.end_date >= start_date).all()
        elif start_date:
            conflict_orders = Order.query.filter(Order.end_date >= start_date).all()
        elif end_date:
            conflict_orders = Order.query.filter(Order.begin_date <= end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if conflict_orders:
        # 从订单中获取冲突的房屋id
        conflict_house_ids = [order.house_id for order in conflict_orders]
        # 如果不为空，讲条件添加到条件查询列表
        if conflict_house_ids:
            filter_params.append(House.house_id.notin_(conflict_house_ids))

    # 区域条件
    if area_id:
        filter_params.append(House.area_id == area_id)

    # 查询数据库, 补充排序条件
    if sort_key == "booking": # 订单量 入住最多
        house_query = House.query.filter(*filter_params).order_by(House.order_count.desc())
    elif sort_key == "price-inc": # 价格由低到高
        house_query = House.query.filter(*filter_params).order_by(House.price.asc())
    elif sort_key == "price-des": # 价格由高到低
        house_query = House.query.filter(*filter_params).order_by(House.price.desc())
    else: # 新旧
        house_query = House.query.filter(*filter_params).order_by(House.create_time.desc())

    # 处理分页
    try:
        #                                   当前页数     每页显示数据量                                 自动错误输出
        paginate_obj = house_query.paginate(page=page, per_page=constants.HOUSE_LIST_PAGE_CAPACITY, error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    # 获取页面数据
    page_houses = paginate_obj.items
    houses = []
    for house in page_houses:
        houses.append(house.to_basic_dict())

    # 获取总页数
    total_page = paginate_obj.pages

    # return jsonify(errno=RET.OK, errmsg="OK", data={"total_page": total_page, "current_page": page, "houses": houses})
    resp_dict = dict(errno=RET.OK, errmsg="OK", data={"total_page": total_page, "current_page": page, "houses": houses})
    resp_json = json.dumps(resp_dict, ensure_ascii=False)

    # 保存到Redis缓存
    if page <= total_page:
        try:
            # redis_store.hset(redis_keys, page, resp_json)
            # redis_store.expire(redis_keys, constants.HOUSE_LIST_REDIS_EXPIRE)

            # 创建管道对象，可以一次执行多个语句
            pipe_line = redis_store.pipeline()
            # 开启多个语句记录
            pipe_line.multi()
            pipe_line.hset(redis_keys, page, resp_json)
            pipe_line.expire(redis_keys, constants.HOUSE_LIST_REDIS_EXPIRE)
            # 执行
            pipe_line.execute()
        except Exception as e:
            current_app.logger.error(e)

    return resp_json, 200, {"Content-Type": "application/json"}
