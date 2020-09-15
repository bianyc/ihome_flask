# -*- coding: utf-8 -*-
import functools
from flask import session, g, jsonify
from werkzeug.routing import BaseConverter
from ihome.utlis.response_code import RET


class ReConverter(BaseConverter):
    """定义正则转换器"""
    def __init__(self, url_map, regex):
        # 调用父类的初始化方法
        super(ReConverter, self).__init__(url_map)
        self.regex = regex


# 定义验证登录状态的装饰器
def login_required(view_func):
    # wraps函数的作用是将wrapper内层函数的属性设置为被装饰函数view_func的属性
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        # 判断用户的登录状态
        if user_id:
            # 将user_id保存到g对象中，在视图函数中可以通过g对象获取保存数据
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            # 用户未登录
            return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    return wrapper
