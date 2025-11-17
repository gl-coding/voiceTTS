import os
import tos
import requests
from tos import HttpMethodType

# 从环境变量获取 AK 和 SK 信息。
ak = os.getenv('TOS_ACCESS_KEY')
sk = os.getenv('TOS_SECRET_KEY')
# your endpoint 和 your region 填写Bucket 所在区域对应的Endpoint。# 以华北2(北京)为例，your endpoint 填写 tos-cn-beijing.volces.com，your region 填写 cn-beijing。
endpoint = "tos-cn-beijing.volces.com"
region = "cn-beijing"
# 桶名称
bucket_name = "web-audio"
# 对象名称
object_key = "dushunv2.wav"
# 本地文件路径
file_name = "data/dushunv2.wav"

def file_upload(file_name, object_key):
    try:
        # 创建 TosClientV2 对象，对桶和对象的操作都通过 TosClientV2 实现
        client = tos.TosClientV2(ak, sk, endpoint, region)
        # 将本地文件上传到目标桶中
        # file_name为本地文件的完整路径。
        client.put_object_from_file(bucket_name, object_key, file_name)
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

def pre_signed_url_get(object_key):
    try:
        # 创建 TosClientV2 对象，对桶和对象的操作都通过 TosClientV2 实现
        client = tos.TosClientV2(ak, sk, endpoint, region)
        # 生成带签名的 url，有效时间为3600s
        pre_signed_url_output = client.pre_signed_url(HttpMethodType.Http_Method_Get, bucket=bucket_name, key=object_key, expires=3600)
        print('签名URL的地址为', pre_signed_url_output.signed_url)
        # 使用预签名的url下载对象，以requests为例
        out = requests.get(pre_signed_url_output.signed_url)
        with open("data/dushunv2_get.wav", 'wb') as f:
            f.write(out.content)
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

def file_delete(object_key):
    try:
        # 创建 TosClientV2 对象，对桶和对象的操作都通过 TosClientV2 实现
        client = tos.TosClientV2(ak, sk, endpoint, region)
        client.create_bucket(bucket_name)
        # 生成删除文件的签名url，有效时间为3600s
        out = client.pre_signed_url(tos.HttpMethodType.Http_Method_Delete, bucket=bucket_name, key=object_key, expires=3600)
        print('签名URL的地址为', out.signed_url)
        # 使用预签名删除对象，以requests为例说明。
        out = requests.delete(out.signed_url)
        out.close()
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

if __name__ == "__main__":
    file_upload(file_name, object_key)
    pre_signed_url_get(object_key)
    #file_delete(object_key)