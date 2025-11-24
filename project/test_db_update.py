#!/usr/bin/env python3
"""
验证自动续期是否真的更新了数据库
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


def test_database_update():
    """测试续期是否更新数据库"""
    
    print("=" * 70)
    print("验证自动续期是否真的更新数据库")
    print("=" * 70)
    
    # 1. 找一条记录
    record = AudioRecord.objects.filter(status='success').first()
    
    if not record:
        print("\n❌ 没有可用的测试记录")
        return
    
    print(f"\n📝 测试记录 ID: {record.id}")
    print(f"   文本: {record.text}")
    
    # 2. 记录原始数据
    print("\n" + "=" * 70)
    print("📸 数据库快照 - 续期前")
    print("=" * 70)
    original_url = record.preurl
    original_expire = record.expire_time
    print(f"原始URL: {original_url[:80]}...")
    print(f"原始过期时间: {original_expire}")
    print(f"原始是否过期: {record.is_expired()}")
    
    # 3. 手动设置为过期
    record.expire_time = timezone.now() - timedelta(hours=1)
    record.save()
    print(f"\n⏰ 手动设置为过期: {record.expire_time}")
    
    # 4. 调用API续期
    print("\n" + "=" * 70)
    print("🔄 调用API进行续期...")
    print("=" * 70)
    
    response = requests.post(
        "http://127.0.0.1:8001/api/get-audio-url/",
        json={
            'text': record.text,
            'tts_type': record.tts_type,
            'expire_time': 7200  # 2小时
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ API调用成功")
        print(f"   是否续期: {result.get('is_renewed')}")
        print(f"   返回的URL: {result.get('url')[:80]}...")
        print(f"   返回的过期时间: {result.get('expire_time')}")
    
    # 5. 从数据库重新读取，验证是否真的更新了
    print("\n" + "=" * 70)
    print("📸 数据库快照 - 续期后（从数据库重新查询）")
    print("=" * 70)
    
    # 重新从数据库查询
    record_after = AudioRecord.objects.get(id=record.id)
    
    new_url = record_after.preurl
    new_expire = record_after.expire_time
    
    print(f"新URL: {new_url[:80]}...")
    print(f"新过期时间: {new_expire}")
    print(f"新是否过期: {record_after.is_expired()}")
    print(f"剩余时间: {record_after.get_remaining_time()}")
    
    # 6. 对比验证
    print("\n" + "=" * 70)
    print("🔍 对比验证")
    print("=" * 70)
    
    url_changed = (original_url != new_url)
    expire_changed = (original_expire != new_expire)
    
    print(f"\nURL是否变化: {'✅ 是' if url_changed else '❌ 否'}")
    if url_changed:
        print(f"  旧: {original_url[:50]}...")
        print(f"  新: {new_url[:50]}...")
    
    print(f"\n过期时间是否变化: {'✅ 是' if expire_changed else '❌ 否'}")
    if expire_changed:
        print(f"  旧: {original_expire}")
        print(f"  新: {new_expire}")
        
        time_diff = new_expire - timezone.now()
        hours = time_diff.total_seconds() / 3600
        print(f"  新的有效期: 约 {hours:.1f} 小时")
    
    # 7. 总结
    print("\n" + "=" * 70)
    print("📊 测试结论")
    print("=" * 70)
    
    if url_changed and expire_changed and not record_after.is_expired():
        print("✅ 数据库已成功更新！")
        print("   ✓ 预签名URL已更新")
        print("   ✓ 过期时间已更新")
        print("   ✓ 续期后URL有效")
        print("\n💡 结论：自动续期的URL会永久保存到数据库中")
    else:
        print("⚠️  数据库更新可能有问题")


if __name__ == '__main__':
    test_database_update()

