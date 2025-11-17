#!/usr/bin/env python3
"""
API接口测试脚本 - 仅测试云服务生成
"""
import requests
import time

BASE_URL = "http://127.0.0.1:8001"
API_ENDPOINT = f"{BASE_URL}/api/get-audio-url/"


def test_api_call(text, tts_type='cloud', expire_time=3600, test_name=""):
    """
    测试API调用
    
    Args:
        text: 要转换的英文文本
        tts_type: 生成方式 (cloud)
        expire_time: URL有效期（秒）
        test_name: 测试名称
    """
    print("\n" + "=" * 70)
    print(f"测试文本: {text}")
    print(f"生成方式: {tts_type}")
    print(f"有效期: {expire_time}秒")
    print("=" * 70)
    
    # 构建请求参数
    data = {
        'text': text,
        'tts_type': tts_type,
        'expire_time': expire_time
    }
    
    # 发送请求
    print("\n发送请求...")
    start_time = time.time()
    
    try:
        response = requests.post(API_ENDPOINT, json=data)
        elapsed = time.time() - start_time
        
        print(f"✅ 响应时间: {elapsed:.2f}秒")
        
        # 检查HTTP状态码
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("\n✅ 请求成功！")
                print(f"   是否新生成: {'是' if result.get('is_new') else '否'}")
                print(f"   是否续期: {'是' if result.get('is_renewed') else '否'}")
                print(f"   记录ID: {result.get('record_id')}")
                print(f"   生成方式: {result.get('tts_type')}")
                print(f"   创建时间: {result.get('created_at')}")
                print(f"   过期时间: {result.get('expire_time')}")
                print(f"   剩余时间: {result.get('remaining_time')}")
                print(f"   播放URL: {result.get('url')[:80]}...")
                
                return True, result
            else:
                print(f"\n❌ 请求失败: {result.get('error')}")
                return False, result
        else:
            print(f"\n❌ HTTP错误: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   {error_detail}")
            except:
                print(f"   {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败！请确保Django服务器正在运行：")
        print("   cd /Users/guolei/work/local/stpython/voice_tts/project")
        print("   python manage.py runserver")
        return False, None
    except Exception as e:
        print(f"\n❌ 异常: {str(e)}")
        return False, None


def main():
    """主测试流程"""
    print("=" * 70)
    print("API接口测试 - 云服务生成")
    print("=" * 70)
    
    # 测试1: 首次请求 - 应该生成新音频
    print("\n【测试1】首次请求 - 应该生成新音频")
    success1, result1 = test_api_call(
        text="Hello, this is a cloud TTS test.",
        tts_type='cloud',
        expire_time=3600,
        test_name="首次请求"
    )
    
    if not success1:
        print("\n⚠️  测试1失败，停止后续测试")
        return
    
    time.sleep(1)
    
    # 测试2: 重复请求 - 应该直接返回（不重新生成）
    print("\n【测试2】重复请求 - 应该直接返回（不生成）")
    success2, result2 = test_api_call(
        text="Hello, this is a cloud TTS test.",
        tts_type='cloud',
        expire_time=3600,
        test_name="重复请求"
    )
    
    if success2:
        if result2.get('is_new'):
            print("\n⚠️  预期：应该返回已存在的记录，但实际生成了新记录")
        else:
            print("\n✅ 正确：返回了已存在的记录")
    
    time.sleep(1)
    
    # 测试3: 不同文本 - 应该生成新音频
    print("\n【测试3】不同文本 - 应该生成新音频")
    success3, result3 = test_api_call(
        text="This is a different cloud text.",
        tts_type='cloud',
        expire_time=7200,
        test_name="不同文本"
    )
    
    if success3:
        if not result3.get('is_new'):
            print("\n⚠️  预期：应该生成新记录，但实际返回了已存在的记录")
        else:
            print("\n✅ 正确：生成了新记录")
    
    time.sleep(1)
    
    # 测试4: 再次请求第一个文本 - 应该直接返回
    print("\n【测试4】再次请求第一个文本 - 应该直接返回")
    success4, result4 = test_api_call(
        text="Hello, this is a cloud TTS test.",
        tts_type='cloud',
        expire_time=3600,
        test_name="再次请求"
    )
    
    if success4:
        if result4.get('is_new'):
            print("\n⚠️  预期：应该返回已存在的记录，但实际生成了新记录")
        else:
            print("\n✅ 正确：返回了已存在的记录")
            if result4.get('record_id') == result1.get('record_id'):
                print("✅ 记录ID一致，确认是同一条记录")
    
    time.sleep(1)
    
    # 测试5: 长文本测试
    print("\n【测试5】长文本测试")
    success5, result5 = test_api_call(
        text="The quick brown fox jumps over the lazy dog. This is a longer text to test the cloud TTS system's ability to handle multiple sentences and generate natural speech.",
        tts_type='cloud',
        expire_time=86400,
        test_name="长文本"
    )
    
    if success5:
        if not result5.get('is_new'):
            print("\n⚠️  预期：应该生成新记录，但实际返回了已存在的记录")
        else:
            print("\n✅ 正确：生成了新记录")
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)
    
    # 统计
    total_tests = 5
    successful_tests = sum([success1, success2, success3, success4, success5])
    
    print(f"\n总测试数: {total_tests}")
    print(f"成功: {successful_tests}")
    print(f"失败: {total_tests - successful_tests}")
    
    if successful_tests == total_tests:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {total_tests - successful_tests} 个测试失败")


if __name__ == '__main__':
    main()

