#!/usr/bin/env python
"""
测试视频文件上传API

API接口: POST /api/upload-video-file/
支持: multipart/form-data 格式

参数:
    video_file: 视频文件（必需）
    subtitle_file: 字幕文件（可选）
    title: 视频标题（可选）
    expire_time: URL有效期秒数（可选，默认3600）
"""
import requests
import os
import sys


API_URL = "http://localhost:8001/api/upload-video-file/"


def upload_video(video_path, subtitle_path=None, title=None, expire_time=3600):
    """
    上传视频和字幕
    
    Args:
        video_path: 视频文件路径
        subtitle_path: 字幕文件路径（可选）
        title: 视频标题（可选）
        expire_time: URL有效期秒数
    """
    # 检查视频文件
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        return None
    
    # 准备文件
    files = {
        'video_file': ('video' + os.path.splitext(video_path)[1], 
                       open(video_path, 'rb'), 
                       'video/mp4')
    }
    
    # 如果有字幕文件
    if subtitle_path and os.path.exists(subtitle_path):
        files['subtitle_file'] = (os.path.basename(subtitle_path),
                                  open(subtitle_path, 'rb'),
                                  'text/plain')
    
    # 准备表单数据
    data = {
        'expire_time': expire_time
    }
    if title:
        data['title'] = title
    
    print(f"📤 正在上传视频: {video_path}")
    if subtitle_path:
        print(f"📝 字幕文件: {subtitle_path}")
    
    try:
        response = requests.post(API_URL, files=files, data=data)
        result = response.json()
        
        # 关闭文件
        for f in files.values():
            if hasattr(f[1], 'close'):
                f[1].close()
        
        if result.get('success'):
            print("\n✅ 上传成功!")
            print(f"   记录ID: {result.get('record_id')}")
            print(f"   标题: {result.get('title')}")
            print(f"   文件大小: {result.get('file_size', 0) / 1024 / 1024:.2f} MB")
            print(f"   视频URL: {result.get('url')[:80]}...")
            if result.get('thumbnail_url'):
                print(f"   缩略图: {result.get('thumbnail_url')[:80]}...")
            if result.get('subtitle_url'):
                print(f"   字幕URL: {result.get('subtitle_url')[:80]}...")
            print(f"   过期时间: {result.get('expire_time')}")
            return result
        else:
            print(f"\n❌ 上传失败: {result.get('error')}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务正在运行")
        return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None


def main():
    """主函数"""
    print("=" * 60)
    print("视频上传API测试")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\n用法:")
        print("  python test_upload_video_api.py <视频路径> [字幕路径] [标题]")
        print("\n示例:")
        print("  python test_upload_video_api.py video.mp4")
        print("  python test_upload_video_api.py video.mp4 subtitle.srt")
        print("  python test_upload_video_api.py video.mp4 subtitle.srt '我的视频'")
        print("\n" + "=" * 60)
        
        # 使用curl示例
        print("\n使用 curl 上传:")
        print("""
curl -X POST http://localhost:8001/api/upload-video-file/ \\
    -F "video_file=@/path/to/video.mp4" \\
    -F "subtitle_file=@/path/to/subtitle.srt" \\
    -F "title=我的视频" \\
    -F "expire_time=7200"
""")
        return
    
    video_path = sys.argv[1]
    subtitle_path = sys.argv[2] if len(sys.argv) > 2 else None
    title = sys.argv[3] if len(sys.argv) > 3 else None
    
    upload_video(video_path, subtitle_path, title)


if __name__ == "__main__":
    main()

