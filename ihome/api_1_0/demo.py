# -*- coding: utf-8 -*-
from . import api
from ihome import models


@api.route('/index')
def index():
    return 'hello flask'

