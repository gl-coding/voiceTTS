"""
英文文本转语音基础方法
使用 Coqui TTS 生成英文语音
"""
import os
from TTS.api import TTS


class EnglishTTSGenerator:
    """英文语音生成器"""
    
    def __init__(self, model_name="tts_models/en/ljspeech/tacotron2-DDC"):
        """
        初始化语音生成器
        
        Args:
            model_name: 使用的TTS模型名称
                       默认使用 tacotron2-DDC (轻量级，适合CPU)
        """
        self.model_name = model_name
        self.tts = None
        
    def load_model(self):
        """加载TTS模型"""
        if self.tts is None:
            print(f"正在加载模型: {self.model_name}")
            print("(首次运行会下载模型，请稍候...)")
            try:
                self.tts = TTS(self.model_name, progress_bar=True)
                print("✅ 模型加载成功!")
                return True
            except Exception as e:
                print(f"❌ 模型加载失败: {e}")
                return False
        return True
    
    def generate_speech(self, text, output_file="output.wav"):
        """
        生成英文语音
        
        Args:
            text: 要转换的英文文本
            output_file: 输出文件路径，默认为 output.wav
            
        Returns:
            bool: 生成成功返回 True，失败返回 False
        """
        # 确保模型已加载
        if not self.load_model():
            return False
        
        try:
            # 创建输出目录
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # 生成语音
            print(f"\n生成语音...")
            print(f"文本: {text[:100]}{'...' if len(text) > 100 else ''}")
            
            self.tts.tts_to_file(text=text, file_path=output_file)
            
            print(f"✅ 语音生成成功!")
            print(f"   输出文件: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ 生成失败: {e}")
            return False


def text_to_speech(text, output_file="output.wav", model_name="tts_models/en/ljspeech/tacotron2-DDC"):
    """
    简化的文本转语音函数（一步到位）
    
    Args:
        text: 要转换的英文文本
        output_file: 输出文件路径
        model_name: TTS模型名称
        
    Returns:
        bool: 生成成功返回 True，失败返回 False
    """
    generator = EnglishTTSGenerator(model_name)
    return generator.generate_speech(text, output_file)


# 使用示例
if __name__ == "__main__":
    print("="*60)
    print("英文语音生成测试")
    print("="*60)
    
    # 方法一：使用类（推荐用于批量生成）
    print("\n方法一：使用类生成多个语音")
    generator = EnglishTTSGenerator()
    generator.load_model()  # 只需加载一次
    
    # 生成多个语音文件
    texts = [
        ("Hello, world!", "outputs/hello.wav"),
        ("This is a test of text to speech.", "outputs/test.wav"),
        ("Artificial intelligence is amazing!", "outputs/ai.wav"),
    ]
    
    for text, output in texts:
        generator.generate_speech(text, output)
        print()
    
    # 方法二：快速单次生成
    print("\n" + "="*60)
    print("方法二：快速单次生成")
    print("="*60)
    
    text = "Welcome to the world of speech synthesis!"
    output_file = "outputs/welcome.wav"
    
    success = text_to_speech(text, output_file)
    
    if success:
        print("\n🎉 所有语音生成完成!")
        print("📁 请查看 outputs/ 目录")
    else:
        print("\n❌ 语音生成失败")

