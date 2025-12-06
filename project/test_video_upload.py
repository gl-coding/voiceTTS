"""
测试视频API
包括上传、获取、续期、列表等功能
"""
import requests
import json
import os

# 配置
BASE_URL = "http://localhost:8000"


def test_upload_video(file_path, title=None, expire_time=7200):
    """
    测试上传视频
    
    Args:
        file_path: 视频文件路径
        title: 视频标题（可选）
        expire_time: URL有效期秒数
    """
    print("="*70)
    print("【1】测试视频上传API")
    print("="*70)
    
    print(f"\n文件路径: {file_path}")
    print(f"标题: {title or '(使用文件名)'}")
    print(f"有效期: {expire_time}秒")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return None
    
    # 发送请求
    try:
        payload = {
            'file_path': file_path,
            'expire_time': expire_time,
        }
        if title:
            payload['title'] = title
        
        response = requests.post(
            f"{BASE_URL}/api/upload-video/",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n响应状态码: {response.status_code}")
        
        result = response.json()
        
        if result.get('success'):
            print("\n✅ 上传成功!")
            print(f"   记录ID: {result.get('record_id')}")
            print(f"   预签名URL: {result.get('url')[:80]}...")
            print(f"   过期时间: {result.get('expire_time')}")
            print(f"   剩余时间: {result.get('remaining_time')}")
            print(f"   对象Key: {result.get('object_key')}")
            print(f"   标题: {result.get('title')}")
            print(f"   文件大小: {result.get('file_size')} bytes")
            print(f"   存储桶: {result.get('bucket')}")
            return result
        else:
            print(f"\n❌ 上传失败: {result.get('error')}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败！请确保服务已启动：")
        print("   cd project && python manage.py runserver")
        return None
    except Exception as e:
        print(f"\n❌ 请求失败: {str(e)}")
        return None


def test_get_video_url(title):
    """测试获取视频URL"""
    print("\n" + "="*70)
    print("【2】测试获取视频URL")
    print("="*70)
    
    print(f"\n标题: {title}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/get-video-url/",
            json={'title': title}
        )
        
        result = response.json()
        
        if result.get('success'):
            print("\n✅ 获取成功!")
            print(f"   记录ID: {result.get('record_id')}")
            print(f"   URL: {result.get('url')[:80]}...")
            print(f"   过期时间: {result.get('expire_time')}")
            print(f"   剩余时间: {result.get('remaining_time')}")
            print(f"   是否续期: {result.get('is_renewed')}")
            return result
        else:
            print(f"\n❌ 获取失败: {result.get('error')}")
            return None
            
    except Exception as e:
        print(f"\n❌ 请求失败: {str(e)}")
        return None


def test_renew_video_url(record_id, expire_time=7200):
    """测试续期视频URL"""
    print("\n" + "="*70)
    print("【3】测试续期视频URL")
    print("="*70)
    
    print(f"\n记录ID: {record_id}")
    print(f"新有效期: {expire_time}秒")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/video/{record_id}/renew/",
            json={'expire_time': expire_time}
        )
        
        result = response.json()
        
        if result.get('success'):
            print("\n✅ 续期成功!")
            print(f"   新URL: {result.get('url')[:80]}...")
            print(f"   新过期时间: {result.get('expire_time')}")
            print(f"   剩余时间: {result.get('remaining_time')}")
            return result
        else:
            print(f"\n❌ 续期失败: {result.get('error')}")
            return None
            
    except Exception as e:
        print(f"\n❌ 请求失败: {str(e)}")
        return None


def test_video_detail(record_id):
    """测试获取视频详情"""
    print("\n" + "="*70)
    print("【4】测试获取视频详情")
    print("="*70)
    
    print(f"\n记录ID: {record_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/video/{record_id}/")
        
        result = response.json()
        
        if result.get('success'):
            data = result.get('data', {})
            print("\n✅ 获取成功!")
            print(f"   ID: {data.get('id')}")
            print(f"   标题: {data.get('title')}")
            print(f"   状态: {data.get('status_display')}")
            print(f"   文件大小: {data.get('file_size')} bytes")
            print(f"   上传时间: {data.get('uptime')}")
            print(f"   过期时间: {data.get('expire_time')}")
            print(f"   是否过期: {data.get('is_expired')}")
            print(f"   剩余时间: {data.get('remaining_time')}")
            return result
        else:
            print(f"\n❌ 获取失败: {result.get('error')}")
            return None
            
    except Exception as e:
        print(f"\n❌ 请求失败: {str(e)}")
        return None


def test_video_list(limit=10, search=''):
    """测试获取视频列表"""
    print("\n" + "="*70)
    print("【5】测试获取视频列表")
    print("="*70)
    
    print(f"\n限制: {limit}")
    if search:
        print(f"搜索: {search}")
    
    try:
        params = {'limit': limit}
        if search:
            params['q'] = search
        
        response = requests.get(f"{BASE_URL}/api/videos/", params=params)
        
        result = response.json()
        
        if result.get('success'):
            print(f"\n✅ 获取成功! 共 {result.get('count')} 条记录")
            for item in result.get('data', []):
                print(f"   [{item.get('id')}] {item.get('title')} - {item.get('status_display')}")
            return result
        else:
            print(f"\n❌ 获取失败: {result.get('error')}")
            return None
            
    except Exception as e:
        print(f"\n❌ 请求失败: {str(e)}")
        return None


def show_usage():
    """显示使用示例"""
    print("\n" + "="*70)
    print("视频API使用示例")
    print("="*70)
    
    print("\n【API列表】")
    print("""
1. 上传视频:    POST /api/upload-video/
2. 获取URL:     POST /api/get-video-url/
3. 续期URL:     POST /api/video/<id>/renew/
4. 视频详情:    GET  /api/video/<id>/
5. 视频列表:    GET  /api/videos/
6. 删除视频:    POST /api/video/<id>/delete/
""")
    
    print("\n【上传视频】")
    print("""
curl -X POST http://localhost:8000/api/upload-video/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "file_path": "/path/to/video.mp4",
    "expire_time": 7200,
    "title": "我的视频"
  }'
""")
    
    print("\n【获取视频URL（智能接口）】")
    print("""
curl -X POST http://localhost:8000/api/get-video-url/ \\
  -H "Content-Type: application/json" \\
  -d '{"title": "我的视频"}'
  
说明: 如果URL过期，会自动续期
""")
    
    print("\n【续期URL】")
    print("""
curl -X POST http://localhost:8000/api/video/1/renew/ \\
  -H "Content-Type: application/json" \\
  -d '{"expire_time": 86400}'
""")
    
    print("\n【获取视频列表】")
    print("""
curl "http://localhost:8000/api/videos/?limit=20&q=搜索词"
""")
    
    print("\n【支持的视频格式】")
    print(".mp4, .avi, .mov, .mkv, .wmv, .flv, .webm, .m4v")
    
    print("="*70)


if __name__ == "__main__":
    import sys
    
    # 显示使用说明
    show_usage()
    
    # 如果提供了文件路径参数，进行测试
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        title = sys.argv[2] if len(sys.argv) > 2 else None
        
        # 1. 上传视频
        result = test_upload_video(video_path, title)
        
        if result:
            record_id = result.get('record_id')
            video_title = result.get('title')
            
            # 2. 获取视频URL
            test_get_video_url(video_title)
            
            # 3. 获取视频详情
            test_video_detail(record_id)
            
            # 4. 续期URL
            test_renew_video_url(record_id, 86400)
            
            # 5. 获取视频列表
            test_video_list()
    else:
        print("\n💡 提示：运行以下命令测试上传:")
        print(f"   python {sys.argv[0]} /path/to/video.mp4")
        print(f"   python {sys.argv[0]} /path/to/video.mp4 '视频标题'")
        
        # 测试获取列表
        print("\n尝试获取视频列表...")
        test_video_list()
    
    print("\n" + "="*70)

