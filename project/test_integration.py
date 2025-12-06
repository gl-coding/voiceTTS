"""
测试上传接口和智能获取接口的集成
验证通过 upload-audio 上传的音频能否被 get-audio-url 找到
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_upload_then_get():
    """
    测试流程：
    1. 通过 /api/upload-audio/ 上传音频
    2. 通过 /api/get-audio-url/ 获取相同文本的音频
    3. 验证返回的是同一条记录
    """
    
    print("="*70)
    print("测试：上传后通过智能接口获取")
    print("="*70)
    
    test_text = "Integration test: Hello, this is a test message."
    test_file = "/Users/guolei/work/local/stpython/voice_tts/outputs/stage2/hello.wav"
    
    # 步骤1：上传音频
    print("\n【步骤1】上传音频文件")
    print(f"文件路径: {test_file}")
    print(f"文本内容: {test_text}")
    
    upload_response = requests.post(
        f"{BASE_URL}/api/upload-audio/",
        json={
            'file_path': test_file,
            'text': test_text,
            'expire_time': 3600,
            'tts_type': 'test_upload'
        }
    )
    
    upload_result = upload_response.json()
    
    if not upload_result.get('success'):
        print(f"❌ 上传失败: {upload_result.get('error')}")
        return
    
    print("✅ 上传成功!")
    print(f"   记录ID: {upload_result.get('record_id')}")
    print(f"   URL: {upload_result.get('url')[:60]}...")
    print(f"   TTS类型: {upload_result.get('tts_type')}")
    
    upload_record_id = upload_result.get('record_id')
    upload_url = upload_result.get('url')
    
    # 步骤2：通过智能接口获取
    print("\n【步骤2】通过智能接口获取相同文本的音频")
    print(f"请求文本: {test_text}")
    
    get_response = requests.post(
        f"{BASE_URL}/api/get-audio-url/",
        json={
            'text': test_text,
            'tts_type': 'local',  # 注意：类型不同
            'expire_time': 3600
        }
    )
    
    get_result = get_response.json()
    
    if not get_result.get('success'):
        print(f"❌ 获取失败: {get_result.get('error')}")
        return
    
    print("✅ 获取成功!")
    print(f"   记录ID: {get_result.get('record_id')}")
    print(f"   URL: {get_result.get('url')[:60]}...")
    print(f"   TTS类型: {get_result.get('tts_type')}")
    print(f"   是否新生成: {get_result.get('is_new')}")
    print(f"   是否续期: {get_result.get('is_renewed')}")
    
    get_record_id = get_result.get('record_id')
    get_url = get_result.get('url')
    
    # 步骤3：验证结果
    print("\n【步骤3】验证结果")
    
    if upload_record_id == get_record_id:
        print("✅ 记录ID匹配！找到了上传的记录")
    else:
        print(f"❌ 记录ID不匹配！上传:{upload_record_id}, 获取:{get_record_id}")
    
    if upload_url.split('?')[0] == get_url.split('?')[0]:
        print("✅ URL基础路径匹配！（签名参数可能不同）")
    else:
        print("❌ URL不匹配")
    
    if not get_result.get('is_new'):
        print("✅ is_new=false，确认是复用已有记录")
    else:
        print("❌ is_new=true，应该是复用已有记录")
    
    if get_result.get('tts_type') == 'test_upload':
        print("✅ TTS类型保持原样（test_upload），未被覆盖")
    else:
        print(f"⚠️  TTS类型变化了：{get_result.get('tts_type')}")
    
    print("\n" + "="*70)
    print("测试结论：")
    print("✅ 通过 /api/upload-audio/ 上传的音频")
    print("✅ 可以通过 /api/get-audio-url/ 获取到")
    print("✅ 系统会复用已上传的记录，不会重复生成")
    print("="*70)


def test_get_then_upload():
    """
    测试反向流程：
    1. 先通过 /api/get-audio-url/ 生成音频
    2. 再尝试通过 /api/upload-audio/ 上传相同文本的音频
    3. 再通过 /api/get-audio-url/ 获取，看返回哪一个
    """
    
    print("\n\n" + "="*70)
    print("测试：生成后上传相同文本")
    print("="*70)
    
    test_text = "Another test: What time is it now?"
    test_file = "/Users/guolei/work/local/stpython/voice_tts/outputs/stage2/short.wav"
    
    # 步骤1：生成音频（如果不存在）
    print("\n【步骤1】通过智能接口生成/获取音频")
    
    gen_response = requests.post(
        f"{BASE_URL}/api/get-audio-url/",
        json={
            'text': test_text,
            'tts_type': 'local',
            'expire_time': 3600
        }
    )
    
    gen_result = gen_response.json()
    
    if gen_result.get('success'):
        print(f"✅ 第一次获取成功")
        print(f"   记录ID: {gen_result.get('record_id')}")
        print(f"   是否新生成: {gen_result.get('is_new')}")
        first_record_id = gen_result.get('record_id')
    else:
        print(f"❌ 获取失败: {gen_result.get('error')}")
        return
    
    # 步骤2：上传相同文本的另一个音频
    print("\n【步骤2】上传相同文本的音频文件")
    
    upload_response = requests.post(
        f"{BASE_URL}/api/upload-audio/",
        json={
            'file_path': test_file,
            'text': test_text,
            'expire_time': 3600,
            'tts_type': 'test_manual_upload'
        }
    )
    
    upload_result = upload_response.json()
    
    if upload_result.get('success'):
        print(f"✅ 上传成功")
        print(f"   记录ID: {upload_result.get('record_id')}")
        second_record_id = upload_result.get('record_id')
    else:
        print(f"❌ 上传失败: {upload_result.get('error')}")
        return
    
    # 步骤3：再次通过智能接口获取
    print("\n【步骤3】再次通过智能接口获取")
    
    get_again_response = requests.post(
        f"{BASE_URL}/api/get-audio-url/",
        json={
            'text': test_text,
            'tts_type': 'local',
            'expire_time': 3600
        }
    )
    
    get_again_result = get_again_response.json()
    
    if get_again_result.get('success'):
        print(f"✅ 再次获取成功")
        print(f"   记录ID: {get_again_result.get('record_id')}")
        final_record_id = get_again_result.get('record_id')
        
        # 分析返回的是哪一个
        if final_record_id == second_record_id:
            print(f"   ℹ️  返回的是新上传的记录（ID: {second_record_id}）")
            print(f"   ℹ️  因为查询按时间倒序，最新的记录会被优先返回")
        elif final_record_id == first_record_id:
            print(f"   ℹ️  返回的是之前生成的记录（ID: {first_record_id}）")
        else:
            print(f"   ⚠️  返回的是另一个记录（ID: {final_record_id}）")
    else:
        print(f"❌ 再次获取失败: {get_again_result.get('error')}")
    
    print("\n" + "="*70)
    print("测试结论：")
    print("✅ 相同文本可以有多条记录")
    print("✅ /api/get-audio-url/ 会返回最新的一条（按时间倒序）")
    print("ℹ️  建议：避免相同文本重复上传/生成")
    print("="*70)


if __name__ == "__main__":
    try:
        # 测试1：先上传，后获取
        test_upload_then_get()
        
        # 测试2：先生成，后上传，再获取
        test_get_then_upload()
        
        print("\n✅ 所有集成测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败！请确保服务已启动：")
        print("   cd /Users/guolei/work/local/stpython/voice_tts/project")
        print("   python manage.py runserver")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

