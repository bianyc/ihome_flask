# -*- coding: utf-8 -*-
from celery import Celery
from ihome.libs.yuntongxun.send_message import send_message

# 定义celery对象
celery_app = Celery("ihome", broker="redis://127.0.0.1:6379/1")


@celery_app.task
def send_sms(mobile, sms_code, time):
    """发送短信的异步任务"""
    send_message(mobile, sms_code, time)
