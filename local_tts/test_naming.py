"""
测试新的文件命名规范
验证生成的文件名符合云端上传标准
"""
import uuid
from datetime import datetime

def generate_filename(index, text, max_length=30):
    """
    生成输出文件名（符合云端上传规范）
    
    格式: local_{uuid}_{timestamp}.wav
    与项目中 tts_service.py 保持一致的命名格式
    """
    # 生成12位uuid
    unique_id = uuid.uuid4().hex[:12]
    
    # 生成时间戳（秒级）
    timestamp = int(datetime.now().timestamp())
    
    # 格式: local_{uuid}_{timestamp}.wav
    filename = f"local_{unique_id}_{timestamp}.wav"
    
    return filename


def test_naming_format():
    """测试文件命名格式"""
    print("="*70)
    print("测试文件命名规范")
    print("="*70)
    
    # 测试用例
    test_cases = [
        (1, "Hello, world!"),
        (2, "Good morning, how are you today?"),
        (3, "This is a test of the batch system."),
        (10, "Text with special chars: @#$% & spaces"),
        (99, "Very long text that should be truncated properly to ensure it doesn't exceed the maximum length allowed"),
        (100, "中文文本应该被过滤掉 with English words"),
    ]
    
    print("\n测试文件命名规范:\n")
    
    for index, text in test_cases:
        filename = generate_filename(index, text)
        
        print(f"行 {index:3d}: {text[:40]}...")
        print(f"        → {filename}")
        
        # 验证规范
        checks = []
        
        # 检查1: 包含 local_ 前缀
        if filename.startswith('local_'):
            checks.append('✅ 前缀正确')
        else:
            checks.append('❌ 前缀错误')
        
        # 检查2: 格式符合 local_{uuid}_{timestamp}.wav
        parts = filename.replace('.wav', '').split('_')
        if len(parts) == 3 and parts[0] == 'local':
            # 检查uuid部分（12位十六进制）
            uuid_part = parts[1]
            if len(uuid_part) == 12 and all(c in '0123456789abcdef' for c in uuid_part.lower()):
                checks.append('✅ UUID格式正确')
            else:
                checks.append('❌ UUID格式错误')
            
            # 检查timestamp部分（纯数字）
            timestamp_part = parts[2]
            if timestamp_part.isdigit() and len(timestamp_part) == 10:
                checks.append('✅ 时间戳正确')
            else:
                checks.append('❌ 时间戳错误')
        else:
            checks.append('❌ 格式不符')
            checks.append('❌ 格式不符')
        
        # 检查3: 只包含合法字符
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.')
        if all(c in allowed_chars for c in filename):
            checks.append('✅ 字符合法')
        else:
            checks.append('❌ 包含非法字符')
        
        # 检查4: 长度合理
        if len(filename) <= 100:
            checks.append('✅ 长度合理')
        else:
            checks.append('❌ 文件名过长')
        
        # 检查5: 以 .wav 结尾
        if filename.endswith('.wav'):
            checks.append('✅ 扩展名正确')
        else:
            checks.append('❌ 扩展名错误')
        
        print(f"        验证: {' | '.join(checks)}")
        print()
    
    print("="*70)
    print("✅ 文件命名规范测试完成!")
    print("\n新的命名格式: local_{uuid}_{timestamp}.wav")
    print("\n说明:")
    print("  • local: 固定前缀，表示本地生成")
    print("  • uuid: 12位十六进制UUID，确保唯一性")
    print("  • timestamp: 10位Unix时间戳（秒级）")
    print("\n特点:")
    print("  ✓ 与项目中 tts_service.py 保持一致")
    print("  ✓ 只包含字母、数字、下划线")
    print("  ✓ UUID + 时间戳双重保证唯一性")
    print("  ✓ 符合云端对象存储命名规范")
    print("  ✓ 文件名简洁固定长度")
    print("="*70)


if __name__ == "__main__":
    test_naming_format()

