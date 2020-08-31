# -*- coding: utf-8 -*-
from flask import Blueprint, current_app

html = Blueprint('html', __name__)


# 127.0.0.1:5000/()
# 127.0.0.1:5000/(index.html)
# 127.0.0.1:5000/register.html
# 127.0.0.1:5000/favicon.ico   # 浏览器认为的网站标识， 浏览器会自己请求这个资源
@html.route("/<re(r'.*'):html_name>")
def get_html(html_name):
    """提供html文件"""
    # 如果html_name为""， 表示访问的路径是/ ,请求的是主页
    if not html_name:
        html_name = "index.html"

    # 如果资源名不是favicon.ico
    if html_name != "favicon.ico":
        html_name = "html/" + html_name

    # flask提供的返回静态文件的方法
    return current_app.send_static_file(html_name)
