"""
对象存储服务
上传文件到TOS并生成预签名URL
"""
import os
import tos
from datetime import timedelta
from django.conf import settings
from django.utils import timezone


class StorageService:
    """TOS对象存储服务"""
    
    def __init__(self, bucket_name=None):
        """
        初始化存储服务
        
        Args:
            bucket_name: 自定义bucket名称，默认使用settings中的TOS_BUCKET_NAME
        """
        self.ak = settings.TOS_ACCESS_KEY
        self.sk = settings.TOS_SECRET_KEY
        self.endpoint = settings.TOS_ENDPOINT
        self.region = settings.TOS_REGION
        self.bucket_name = bucket_name or settings.TOS_BUCKET_NAME
        self.client = None
    
    def get_client(self):
        """获取TOS客户端"""
        if self.client is None:
            self.client = tos.TosClientV2(
                self.ak,
                self.sk,
                self.endpoint,
                self.region
            )
        return self.client
    
    def upload_file(self, local_file_path, object_key=None):
        """
        上传文件到对象存储
        
        Args:
            local_file_path: 本地文件路径
            object_key: 对象存储中的key，默认使用文件名
            
        Returns:
            tuple: (success, object_key, error_message)
        """
        try:
            if not os.path.exists(local_file_path):
                return False, None, f"文件不存在: {local_file_path}"
            
            # 如果未指定object_key，使用文件名
            if object_key is None:
                object_key = os.path.basename(local_file_path)
            
            client = self.get_client()
            
            print(f"正在上传文件到TOS: {local_file_path} -> {object_key}")
            
            # 上传文件
            client.put_object_from_file(
                self.bucket_name,
                object_key,
                local_file_path
            )
            
            print(f"✅ 文件上传成功: {object_key}")
            return True, object_key, None
            
        except tos.exceptions.TosClientError as e:
            error_msg = f"TOS客户端错误: {e.message}"
            print(f"❌ {error_msg}")
            return False, None, error_msg
        except tos.exceptions.TosServerError as e:
            error_msg = f"TOS服务器错误: {e.message}"
            print(f"❌ {error_msg}")
            return False, None, error_msg
        except Exception as e:
            error_msg = f"上传失败: {str(e)}"
            print(f"❌ {error_msg}")
            return False, None, error_msg
    
    def generate_presigned_url(self, object_key, expires=3600):
        """
        生成预签名URL
        
        Args:
            object_key: 对象存储中的key
            expires: 过期时间（秒），默认3600秒（1小时）
            
        Returns:
            tuple: (success, presigned_url, expire_time, error_message)
        """
        try:
            client = self.get_client()
            
            print(f"正在生成预签名URL: {object_key}, 有效期: {expires}秒")
            
            # 生成预签名URL
            result = client.pre_signed_url(
                tos.HttpMethodType.Http_Method_Get,
                bucket=self.bucket_name,
                key=object_key,
                expires=expires
            )
            
            # 计算过期时间（使用Django的timezone.now()以支持时区）
            expire_time = timezone.now() + timedelta(seconds=expires)
            
            print(f"✅ 预签名URL生成成功")
            print(f"   URL: {result.signed_url[:100]}...")
            print(f"   过期时间: {expire_time}")
            
            return True, result.signed_url, expire_time, None
            
        except tos.exceptions.TosClientError as e:
            error_msg = f"TOS客户端错误: {e.message}"
            print(f"❌ {error_msg}")
            return False, None, None, error_msg
        except tos.exceptions.TosServerError as e:
            error_msg = f"TOS服务器错误: {e.message}"
            print(f"❌ {error_msg}")
            return False, None, None, error_msg
        except Exception as e:
            error_msg = f"生成预签名URL失败: {str(e)}"
            print(f"❌ {error_msg}")
            return False, None, None, error_msg
    
    def upload_and_get_url(self, local_file_path, object_key=None, expires=3600):
        """
        上传文件并生成预签名URL（一步到位）
        
        Args:
            local_file_path: 本地文件路径
            object_key: 对象存储中的key
            expires: URL过期时间（秒）
            
        Returns:
            tuple: (success, presigned_url, expire_time, error_message)
        """
        # 上传文件
        success, obj_key, error = self.upload_file(local_file_path, object_key)
        if not success:
            return False, None, None, error
        
        # 生成预签名URL
        return self.generate_presigned_url(obj_key, expires)
    
    def delete_file(self, object_key):
        """
        删除对象存储中的文件
        
        Args:
            object_key: 对象存储中的key
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            client = self.get_client()
            
            print(f"正在删除文件: {object_key}")
            
            client.delete_object(self.bucket_name, object_key)
            
            print(f"✅ 文件删除成功: {object_key}")
            return True, None
            
        except Exception as e:
            error_msg = f"删除文件失败: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg

