# -*- coding: utf-8 -*-

from qiniu import Auth, put_data, etag
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
access_key = '544pMCKTpgxE1rcNHkkh2zJELSDLcTpKhvoctHd7'
secret_key = 'H092TdOdOZ68i1zqf07n8NKrVaNSIPa0BD0zcxND'


def storage(img_data):
    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'byc-ihome'

    # 上传后保存的文件名
    # key = 'my-python-logo.png'

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    # 要上传文件的本地路径
    # localfile = './sync/bbb.jpg'

    ret, info = put_data(token, None, img_data)
    # print(ret)
    # print('==' * 10)
    # print(info)
    if info.status_code == 200:
        # 上传成功
        return ret.get("key")
    else:
        # 失败
        raise Exception("上传七牛云失败")


# if __name__ == '__main__':
#     with open(r'storage_test.jpg', 'rb') as f:
#         data = f.read()
#     storage(data)
