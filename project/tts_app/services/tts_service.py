"""
TTS语音生成服务
支持本地TTS和云服务TTS
"""
import os
import json
import uuid
from datetime import datetime
from django.conf import settings


class LocalTTSService:
    """本地TTS服务"""
    
    def __init__(self):
        self.model_name = settings.LOCAL_TTS_MODEL
        self.tts = None
    
    def load_model(self):
        """加载本地TTS模型"""
        if self.tts is None:
            try:
                from TTS.api import TTS
                print(f"正在加载本地TTS模型: {self.model_name}")
                self.tts = TTS(self.model_name, progress_bar=False)
                print("✅ 本地TTS模型加载成功")
                return True
            except Exception as e:
                print(f"❌ 本地TTS模型加载失败: {e}")
                return False
        return True
    
    def generate_speech(self, text):
        """
        生成语音
        
        Args:
            text: 英文文本
            
        Returns:
            tuple: (success, file_path, error_message)
        """
        try:
            # 加载模型
            if not self.load_model():
                return False, None, "模型加载失败"
            
            # 生成唯一文件名
            filename = f"local_{uuid.uuid4().hex[:12]}_{int(datetime.now().timestamp())}.wav"
            output_path = os.path.join(settings.AUDIO_OUTPUT_DIR, filename)
            
            # 生成语音
            print(f"正在生成语音（本地）: {text[:50]}...")
            self.tts.tts_to_file(text=text, file_path=output_path)
            
            print(f"✅ 本地语音生成成功: {output_path}")
            return True, output_path, None
            
        except Exception as e:
            error_msg = f"本地TTS生成失败: {str(e)}"
            print(f"❌ {error_msg}")
            return False, None, error_msg


class CloudTTSService:
    """火山引擎云TTS服务（使用OpenSpeech API）"""
    
    def __init__(self):
        self.appid = settings.VOLC_APPID
        self.access_token = settings.VOLC_ACCESS_TOKEN
        self.cluster = getattr(settings, 'VOLC_CLUSTER', 'volcano_tts')
    
    def generate_speech(self, text):
        """
        生成语音（云服务）
        
        Args:
            text: 英文文本
            
        Returns:
            tuple: (success, file_path, error_message)
        """
        try:
            import base64
            import requests
            import json
            
            # 配置火山引擎OpenSpeech TTS服务
            voice_type = "BV504_streaming"  # 英文语音
            host = "openspeech.bytedance.com"
            api_url = f"https://{host}/api/v1/tts"
            
            header = {"Authorization": f"Bearer;{self.access_token}"}
            
            request_json = {
                "app": {
                    "appid": self.appid,
                    "token": self.access_token,
                    "cluster": self.cluster
                },
                "user": {
                    "uid": "388808087185088"
                },
                "audio": {
                    "voice_type": voice_type,
                    "encoding": "wav",
                    "speed_ratio": 1.0,
                    "volume_ratio": 1.0,
                    "pitch_ratio": 1.0,
                },
                "request": {
                    "reqid": str(uuid.uuid4()),
                    "text": text,
                    "text_type": "plain",
                    "operation": "query",
                    "with_frontend": 1,
                    "frontend_type": "unitTson"
                }
            }
            
            print(f"正在生成语音（云服务）: {text[:50]}...")
            
            # 调用API
            resp = requests.post(api_url, json.dumps(request_json), headers=header)
            resp_json = resp.json()
            
            if "data" in resp_json:
                # 解码音频数据
                audio_data = base64.b64decode(resp_json["data"])
                
                # 保存文件
                filename = f"cloud_{uuid.uuid4().hex[:12]}_{int(datetime.now().timestamp())}.wav"
                output_path = os.path.join(settings.AUDIO_OUTPUT_DIR, filename)
                
                with open(output_path, 'wb') as f:
                    f.write(audio_data)
                
                print(f"✅ 云服务语音生成成功: {output_path}")
                return True, output_path, None
            else:
                error_msg = f"云TTS返回数据异常: {resp_json}"
                print(f"❌ {error_msg}")
                return False, None, error_msg
                
        except Exception as e:
            error_msg = f"云TTS生成失败: {str(e)}"
            print(f"❌ {error_msg}")
            return False, None, error_msg


class TTSServiceFactory:
    """TTS服务工厂"""
    
    _local_service = None
    _cloud_service = None
    
    @classmethod
    def get_service(cls, tts_type='local'):
        """
        获取TTS服务实例
        
        Args:
            tts_type: 'local' 或 'cloud'
            
        Returns:
            TTSService实例
        """
        if tts_type == 'local':
            if cls._local_service is None:
                cls._local_service = LocalTTSService()
            return cls._local_service
        elif tts_type == 'cloud':
            if cls._cloud_service is None:
                cls._cloud_service = CloudTTSService()
            return cls._cloud_service
        else:
            raise ValueError(f"不支持的TTS类型: {tts_type}")

