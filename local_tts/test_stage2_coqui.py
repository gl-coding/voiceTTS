"""
第二阶段：Coqui TTS 测试（轻量模型）
中等质量，CPU可用，GPU更佳
"""
import os
import time
import soundfile as sf

def test_coqui_tts():
    print("="*60)
    print("第二阶段：Coqui TTS 测试")
    print("模型特点：质量较好、速度适中、CPU/GPU均可")
    print("="*60)
    
    # 检查安装
    try:
        from TTS.api import TTS
        import torch
        print("✅ Coqui TTS 已安装")
        print(f"✅ PyTorch 已安装")
        print(f"   GPU 可用: {'是' if torch.cuda.is_available() else '否'}")
    except ImportError as e:
        print("❌ 缺少依赖，请先安装:")
        print("   pip install TTS torch")
        return
    
    # 创建输出目录
    os.makedirs("outputs/stage2", exist_ok=True)
    
    # 英文测试文本
    test_texts = [
        ("hello", "Hello, world!"),
        ("short", "This is a test of Coqui text to speech system."),
        ("medium", "Artificial intelligence is revolutionizing speech synthesis. "
                   "Modern systems can produce highly natural and expressive voices."),
        ("long", "In the field of speech synthesis, deep learning has enabled "
                 "remarkable progress. Neural text-to-speech models can now generate "
                 "speech that is nearly indistinguishable from human recordings, "
                 "with proper intonation, rhythm, and emotional expression."),
        ("question", "How are you doing today? Would you like to hear more examples?"),
        ("numbers", "The temperature is 72 degrees Fahrenheit. "
                   "Please call me at 555-987-6543 by 4:45 PM."),
    ]
    
    # 使用轻量级英文模型（适合CPU）
    model_name = "tts_models/en/ljspeech/tacotron2-DDC"
    
    print(f"\n正在加载模型: {model_name}")
    print("(首次运行会下载模型，请稍候...)")
    
    try:
        start_load = time.time()
        tts = TTS(model_name, progress_bar=True)
        load_time = time.time() - start_load
        
        print(f"✅ 模型加载成功! 耗时: {load_time:.2f}秒")
        
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return
    
    print("\n" + "="*60)
    print("开始生成语音样本...")
    print("="*60)
    
    results = []
    
    for name, text in test_texts:
        print(f"\n[{len(results)+1}/{len(test_texts)}] 生成: {name}")
        print(f"文本: {text[:60]}{'...' if len(text) > 60 else ''}")
        
        output_file = f"outputs/stage2/{name}.wav"
        
        try:
            start_time = time.time()
            tts.tts_to_file(text=text, file_path=output_file)
            gen_time = time.time() - start_time
            
            # 计算音频时长
            audio_data, sample_rate = sf.read(output_file)
            duration = len(audio_data) / sample_rate
            rtf = gen_time / duration if duration > 0 else 0
            
            result = {
                "name": name,
                "text_length": len(text),
                "gen_time": round(gen_time, 2),
                "duration": round(duration, 2),
                "rtf": round(rtf, 3),
                "output": output_file
            }
            results.append(result)
            
            print(f"✅ 生成成功!")
            print(f"   生成时间: {gen_time:.2f}秒")
            print(f"   音频时长: {duration:.2f}秒")
            print(f"   实时率(RTF): {rtf:.3f}x")
            
        except Exception as e:
            print(f"❌ 生成失败: {e}")
            results.append({"name": name, "error": str(e)})
    
    # 生成汇总报告
    print("\n" + "="*60)
    print("第二阶段测试完成!")
    print("="*60)
    
    successful = [r for r in results if "error" not in r]
    
    if successful:
        avg_rtf = sum(r["rtf"] for r in successful) / len(successful)
        total_time = sum(r["gen_time"] for r in successful)
        
        print(f"\n✅ 成功生成: {len(successful)}/{len(test_texts)} 个样本")
        print(f"📊 平均实时率: {avg_rtf:.3f}x")
        print(f"⏱️  总耗时: {total_time:.2f}秒")
        print(f"📁 输出目录: outputs/stage2/")
        
        print("\n" + "="*60)
        print("🎧 请试听并与第一阶段对比:")
        print("="*60)
        
        for r in successful:
            print(f"\n{r['name']}.wav - {r['duration']:.2f}秒")
        
        print("\n" + "="*60)
        print("📊 与第一阶段对比:")
        print("="*60)
        print("请对比 outputs/stage1/ 和 outputs/stage2/ 中的同名文件")
        print("评估哪个模型的质量更好")
        
        print("\n" + "="*60)
        print("✨ Coqui TTS (Tacotron2) 特点:")
        print("="*60)
        print("  ✓ 质量比 Piper 更自然")
        print("  ✓ 韵律更好")
        print("  ✓ CPU 可运行，但比 Piper 慢")
        print(f"  ✓ 平均速度: {avg_rtf:.3f}x 实时率")
        
        print("\n" + "="*60)
        print("🚀 下一步:")
        print("="*60)
        
        if avg_rtf < 5:
            print("您的电脑运行第二阶段很流畅！")
            print("可以继续测试第三阶段（更高质量）:")
            print("  python test_stage3_bark.py")
        else:
            print(f"⚠️  第二阶段运行较慢 (RTF={avg_rtf:.2f}x)")
            print("建议:")
            print("  - 如果质量满意，可以停在这个阶段")
            print("  - 如果想要更好质量，谨慎继续第三阶段")
    
    else:
        print("\n❌ 测试失败")
        print("建议使用第一阶段的 Piper（更轻量）")

if __name__ == "__main__":
    test_coqui_tts()

