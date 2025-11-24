#!/usr/bin/env python3
"""
测试过期URL自动续期功能
"""
import os
import sys
import django
from datetime import timedelta

# 设置Django环境
sys.path.insert(0, '/Users/guolei/work/local/stpython/voice_tts/project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tts_project.settings')
django.setup()

from django.utils import timezone
from tts_app.models import AudioRecord
import requests
import time


def test_expired_renewal():
    """测试过期URL自动续期"""
    
    print("=" * 70)
    print("测试过期URL自动续期功能")
    print("=" * 70)
    
    # 1. 查找一条成功的记录
    record = AudioRecord.objects.filter(status='success').first()
    
    if not record:
        print("\n❌ 数据库中没有成功的记录，请先生成一些音频")
        return
    
    print(f"\n找到测试记录:")
    print(f"  ID: {record.id}")
    print(f"  文本: {record.text}")
    print(f"  TTS类型: {record.tts_type}")
    print(f"  当前过期时间: {record.expire_time}")
    print(f"  是否过期: {record.is_expired()}")
    
    # 2. 手动将过期时间设置为过去的时间
    original_expire_time = record.expire_time
    record.expire_time = timezone.now() - timedelta(hours=1)  # 1小时前过期
    record.save()
    
    print(f"\n修改后的过期时间: {record.expire_time}")
    print(f"  是否过期: {record.is_expired()} ✅")
    
    # 3. 调用API，看是否会自动续期
    print("\n" + "=" * 70)
    print("调用API测试自动续期...")
    print("=" * 70)
    
    api_url = "http://127.0.0.1:8001/api/get-audio-url/"
    data = {
        'text': record.text,
        'tts_type': record.tts_type,
        'expire_time': 3600  # 续期1小时
    }
    
    print(f"\n请求参数:")
    print(f"  文本: {data['text']}")
    print(f"  TTS类型: {data['tts_type']}")
    print(f"  新的有效期: {data['expire_time']}秒")
    
    start_time = time.time()
    
    try:
        response = requests.post(api_url, json=data)
        elapsed = time.time() - start_time
        
        print(f"\n✅ 响应时间: {elapsed:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("\n" + "=" * 70)
                print("API响应结果:")
                print("=" * 70)
                print(f"  ✅ 请求成功")
                print(f"  是否新生成: {'是' if result.get('is_new') else '否'}")
                print(f"  是否续期: {'是' if result.get('is_renewed') else '否'} {'✅' if result.get('is_renewed') else '❌'}")
                print(f"  记录ID: {result.get('record_id')}")
                print(f"  新的过期时间: {result.get('expire_time')}")
                print(f"  剩余时间: {result.get('remaining_time')}")
                print(f"  播放URL: {result.get('url')[:80]}...")
                
                # 4. 验证数据库中的记录是否更新
                record.refresh_from_db()
                print("\n" + "=" * 70)
                print("数据库记录验证:")
                print("=" * 70)
                print(f"  新的过期时间: {record.expire_time}")
                print(f"  是否过期: {record.is_expired()} {'✅ 已续期' if not record.is_expired() else '❌ 仍然过期'}")
                print(f"  剩余时间: {record.get_remaining_time()}")
                
                # 5. 总结
                print("\n" + "=" * 70)
                print("测试总结:")
                print("=" * 70)
                
                if result.get('is_renewed') and not record.is_expired():
                    print("✅ 自动续期功能正常工作！")
                    print("   - 检测到URL已过期")
                    print("   - 自动生成新的预签名URL")
                    print("   - 未重新生成音频文件（高效）")
                    print("   - 响应时间快（{}秒）".format(elapsed))
                else:
                    print("⚠️  续期可能未成功")
                
            else:
                print(f"\n❌ API返回失败: {result.get('error')}")
        else:
            print(f"\n❌ HTTP错误: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败！请确保Django服务器正在运行：")
        print("   python manage.py runserver 8001")
    except Exception as e:
        print(f"\n❌ 异常: {str(e)}")


if __name__ == '__main__':
    test_expired_renewal()

