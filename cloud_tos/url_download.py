import requests
import os
import tos
from tos import HttpMethodType

# 从环境变量获取 AK 和 SK 信息。
ak = os.getenv('TOS_ACCESS_KEY')
sk = os.getenv('TOS_SECRET_KEY')
endpoint = "tos-cn-beijing.volces.com"
region = "cn-beijing"
bucket_name = "web-audio"
object_key = "dushunv2.wav"
content = b'test pre_signed_url get_object'
try:
    # 创建 TosClientV2 对象，对桶和对象的操作都通过 TosClientV2 实现
    client = tos.TosClientV2(ak, sk, endpoint, region)
    # 生成带签名的 url，有效时间为3600s
    pre_signed_url_output = client.pre_signed_url(HttpMethodType.Http_Method_Get, bucket=bucket_name, key=object_key, expires=3600)
    print('签名URL的地址为', pre_signed_url_output.signed_url)
    # 使用预签名的url下载对象，以requests为例
    out = requests.get(pre_signed_url_output.signed_url)
    #print(out.content)

except tos.exceptions.TosClientError as e:
    # 操作失败，捕获客户端异常，一般情况为非法请求参数或网络异常
    print('fail with client error, message:{}, cause: {}'.format(e.message, e.cause))
except tos.exceptions.TosServerError as e:
    # 操作失败，捕获服务端异常，可从返回信息中获取详细错误信息
    print('fail with server error, code: {}'.format(e.code))
    # request id 可定位具体问题，强烈建议日志中保存
    print('error with request id: {}'.format(e.request_id))
    print('error with message: {}'.format(e.message))
    print('error with http code: {}'.format(e.status_code))
    print('error with ec: {}'.format(e.ec))
    print('error with request url: {}'.format(e.request_url))
except Exception as e:
    print('fail with unknown error: {}'.format(e))