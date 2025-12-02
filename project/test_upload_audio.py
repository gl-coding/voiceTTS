"""
测试音频文件上传API
直接上传本地音频文件到云端，保存文本到数据库
"""
import requests
import json
import os

# 配置
BASE_URL = "http://localhost:8000"  # 修改为你的服务地址
API_ENDPOINT = f"{BASE_URL}/api/upload-audio/"


def test_upload_audio():
    """测试上传音频文件"""
    
    print("="*70)
    print("测试音频文件上传API")
    print("="*70)
    
    # 测试数据
    test_cases = [
        {
            "file_path": "/Users/guolei/work/local/stpython/voice_tts/outputs/stage2/hello.wav",
            "text": "Hello, how are you today?",
            "expire_time": 7200,  # 2小时
            "tts_type": "custom"
        },
        {
            "file_path": "/Users/guolei/work/local/stpython/voice_tts/outputs/stage2/short.wav",
            "text": "This is a short audio sample.",
            "expire_time": 3600,  # 1小时
            "tts_type": "custom"
        }
    ]
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"\n【测试用例 {i}】")
        print(f"文件路径: {test_data['file_path']}")
        print(f"文本内容: {test_data['text']}")
        print(f"有效期: {test_data['expire_time']}秒")
        
        # 检查文件是否存在
        if not os.path.exists(test_data['file_path']):
            print(f"❌ 文件不存在，跳过: {test_data['file_path']}")
            continue
        
        # 发送请求
        try:
            response = requests.post(
                API_ENDPOINT,
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"响应状态码: {response.status_code}")
            
            # 解析响应
            result = response.json()
            
            if result.get('success'):
                print("✅ 上传成功!")
                print(f"   记录ID: {result.get('record_id')}")
                print(f"   预签名URL: {result.get('url')[:80]}...")
                print(f"   过期时间: {result.get('expire_time')}")
                print(f"   剩余时间: {result.get('remaining_time')}")
                print(f"   对象Key: {result.get('object_key')}")
            else:
                print(f"❌ 上传失败: {result.get('error')}")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败！请确保服务已启动（python manage.py runserver）")
            break
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
    
    print("\n" + "="*70)


def test_error_cases():
    """测试错误情况"""
    
    print("\n【测试错误情况】")
    print("="*70)
    
    error_cases = [
        {
            "name": "文件路径为空",
            "data": {
                "file_path": "",
                "text": "Test text",
                "expire_time": 3600
            }
        },
        {
            "name": "文本内容为空",
            "data": {
                "file_path": "/path/to/audio.wav",
                "text": "",
                "expire_time": 3600
            }
        },
        {
            "name": "文件不存在",
            "data": {
                "file_path": "/non/existent/file.wav",
                "text": "Test text",
                "expire_time": 3600
            }
        },
        {
            "name": "不支持的文件格式",
            "data": {
                "file_path": "/path/to/file.txt",
                "text": "Test text",
                "expire_time": 3600
            }
        }
    ]
    
    for case in error_cases:
        print(f"\n测试: {case['name']}")
        
        try:
            response = requests.post(
                API_ENDPOINT,
                json=case['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            result = response.json()
            
            if not result.get('success'):
                print(f"✅ 正确返回错误: {result.get('error')}")
            else:
                print(f"⚠️  应该返回错误，但成功了")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败！请确保服务已启动")
            break
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
    
    print("="*70)


def show_usage():
    """显示使用示例"""
    
    print("\n" + "="*70)
    print("API使用示例")
    print("="*70)
    
    print("\n【curl命令示例】")
    print("""
curl -X POST http://localhost:8000/api/upload-audio/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "file_path": "/path/to/your/audio.wav",
    "text": "Your text content here",
    "expire_time": 3600,
    "tts_type": "custom"
  }'
""")
    
    print("\n【Python requests示例】")
    print("""
import requests

response = requests.post(
    'http://localhost:8000/api/upload-audio/',
    json={
        'file_path': '/path/to/audio.wav',
        'text': 'Hello world',
        'expire_time': 7200,
        'tts_type': 'custom'
    }
)

result = response.json()
if result['success']:
    print(f"URL: {result['url']}")
    print(f"Record ID: {result['record_id']}")
""")
    
    print("\n【参数说明】")
    print("""
- file_path   (必需): 本地音频文件的完整路径
- text        (必需): 音频对应的文本内容（最多1000字符）
- expire_time (可选): URL有效期，单位秒，默认3600（1小时）
- tts_type    (可选): 类型标记，默认'custom'

支持的音频格式: .wav, .mp3, .flac, .ogg, .m4a, .aac
""")
    
    print("="*70)


if __name__ == "__main__":
    # 显示使用说明
    show_usage()
    
    # 运行测试
    test_upload_audio()
    
    # 测试错误情况
    test_error_cases()
    
    print("\n✅ 测试完成！")

