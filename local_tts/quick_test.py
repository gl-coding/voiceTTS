"""
快速测试批量生成工具
生成3个简短的测试音频
"""
import os
from batch_generate import BatchTTSGenerator

def quick_test():
    """快速测试"""
    print("="*70)
    print("批量生成工具 - 快速测试")
    print("="*70)
    
    # 创建测试输入文件
    test_input = "test_input.txt"
    test_texts = [
        "Hello, world!",
        "This is a quick test.",
        "Batch generation is working!"
    ]
    
    print(f"\n📝 创建测试文件: {test_input}")
    with open(test_input, 'w', encoding='utf-8') as f:
        f.write('\n'.join(test_texts))
    print(f"   写入 {len(test_texts)} 行文本")
    
    # 创建生成器
    print(f"\n🎵 初始化TTS生成器...")
    generator = BatchTTSGenerator(output_dir="data")
    
    # 批量生成
    print(f"\n🚀 开始生成...")
    result = generator.generate_all(
        input_file=test_input,
        use_custom_names=True
    )
    
    # 显示结果
    print("\n" + "="*70)
    if result["success"] > 0:
        print("✅ 快速测试完成!")
        print(f"\n生成的文件在 data/ 目录:")
        for r in result["results"]:
            if r.get("success"):
                print(f"  - {r['file']}")
        
        print(f"\n💡 提示:")
        print(f"  - 查看文件: ls -lh data/")
        print(f"  - 播放音频: play data/{result['results'][0]['file']}")
        print(f"  - 完整用法: python batch_generate.py --help")
    else:
        print("❌ 测试失败")
    
    # 清理测试文件
    if os.path.exists(test_input):
        os.remove(test_input)
        print(f"\n🧹 清理测试文件: {test_input}")
    
    print("="*70)

if __name__ == "__main__":
    quick_test()

