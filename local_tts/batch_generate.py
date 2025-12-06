"""
批量文本转语音工具
从文本文件中读取内容，为每一行生成语音文件
"""
import os
import sys
import time
from pathlib import Path

# 导入本地的TTS生成器
from test import EnglishTTSGenerator


class BatchTTSGenerator:
    """批量语音生成器"""
    
    def __init__(self, output_dir="data", model_name="tts_models/en/ljspeech/tacotron2-DDC"):
        """
        初始化批量生成器
        
        Args:
            output_dir: 输出目录，默认为 data
            model_name: TTS模型名称
        """
        self.output_dir = output_dir
        self.model_name = model_name
        self.generator = EnglishTTSGenerator(model_name)
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"📁 输出目录: {os.path.abspath(self.output_dir)}")
    
    def read_text_file(self, input_file):
        """
        读取文本文件，返回非空行列表
        
        Args:
            input_file: 输入文件路径
            
        Returns:
            list: 文本行列表
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 过滤空行和只包含空白字符的行
            texts = [line.strip() for line in lines if line.strip()]
            
            print(f"✅ 成功读取文件: {input_file}")
            print(f"   共 {len(texts)} 行文本")
            return texts
            
        except FileNotFoundError:
            print(f"❌ 文件不存在: {input_file}")
            return []
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return []
    
    def generate_filename(self, index, text, max_length=30):
        """
        生成输出文件名（符合云端上传规范）
        
        格式: local_{uuid}_{timestamp}.wav
        与项目中 tts_service.py 保持一致的命名格式
        
        Args:
            index: 行号（从1开始）
            text: 文本内容
            max_length: 未使用（保留参数兼容性）
            
        Returns:
            str: 文件名
        """
        import uuid
        from datetime import datetime
        
        # 生成12位uuid（与项目保持一致）
        unique_id = uuid.uuid4().hex[:12]
        
        # 生成时间戳（秒级）
        timestamp = int(datetime.now().timestamp())
        
        # 格式: local_{uuid}_{timestamp}.wav
        filename = f"local_{unique_id}_{timestamp}.wav"
        
        return filename
    
    def generate_all(self, input_file, start_index=1, end_index=None, 
                     use_custom_names=True, name_prefix="audio"):
        """
        批量生成语音
        
        Args:
            input_file: 输入文本文件路径
            start_index: 开始行号（从1开始）
            end_index: 结束行号（包含），None表示到最后
            use_custom_names: 是否使用基于文本内容的自定义文件名
            name_prefix: 如果不使用自定义名称，使用的前缀
            
        Returns:
            dict: 生成结果统计
        """
        # 读取文本
        texts = self.read_text_file(input_file)
        if not texts:
            return {"success": 0, "failed": 0, "total": 0}
        
        # 确定处理范围
        start_idx = max(1, start_index) - 1  # 转为0-based索引
        end_idx = min(len(texts), end_index if end_index else len(texts))
        
        texts_to_process = texts[start_idx:end_idx]
        
        print("\n" + "="*70)
        print("开始批量生成")
        print("="*70)
        print(f"输入文件: {input_file}")
        print(f"处理范围: 第 {start_idx+1} 行 到 第 {end_idx} 行")
        print(f"共需处理: {len(texts_to_process)} 条")
        print(f"输出目录: {self.output_dir}")
        print("="*70)
        
        # 加载模型（只加载一次）
        print("\n正在加载TTS模型...")
        if not self.generator.load_model():
            print("❌ 模型加载失败，无法继续")
            return {"success": 0, "failed": len(texts_to_process), "total": len(texts_to_process)}
        
        # 批量生成
        results = []
        success_count = 0
        failed_count = 0
        total_time = 0
        
        print("\n开始生成语音...\n")
        
        for i, text in enumerate(texts_to_process, start=1):
            actual_line_num = start_idx + i
            
            print(f"[{i}/{len(texts_to_process)}] 第 {actual_line_num} 行")
            print(f"文本: {text[:60]}{'...' if len(text) > 60 else ''}")
            
            # 生成文件名
            if use_custom_names:
                filename = self.generate_filename(actual_line_num, text)
            else:
                # 简单命名也使用 uuid + timestamp 格式
                import uuid
                from datetime import datetime
                unique_id = uuid.uuid4().hex[:12]
                timestamp = int(datetime.now().timestamp())
                filename = f"{name_prefix}_{unique_id}_{timestamp}.wav"
            
            output_file = os.path.join(self.output_dir, filename)
            
            # 生成语音
            start_time = time.time()
            success = self.generator.generate_speech(text, output_file)
            gen_time = time.time() - start_time
            
            if success:
                success_count += 1
                total_time += gen_time
                print(f"✅ 成功! 耗时: {gen_time:.2f}秒")
                print(f"   文件: {filename}\n")
                
                results.append({
                    "line": actual_line_num,
                    "text": text,
                    "file": filename,
                    "time": round(gen_time, 2),
                    "success": True
                })
            else:
                failed_count += 1
                print(f"❌ 失败!\n")
                
                results.append({
                    "line": actual_line_num,
                    "text": text,
                    "success": False
                })
        
        # 生成结果报告
        print("\n" + "="*70)
        print("批量生成完成!")
        print("="*70)
        
        print(f"\n📊 生成统计:")
        print(f"   总数: {len(texts_to_process)} 条")
        print(f"   成功: {success_count} 条")
        print(f"   失败: {failed_count} 条")
        
        if success_count > 0:
            avg_time = total_time / success_count
            print(f"   总耗时: {total_time:.2f} 秒")
            print(f"   平均耗时: {avg_time:.2f} 秒/条")
        
        print(f"\n📁 输出目录: {os.path.abspath(self.output_dir)}")
        
        # 显示成功的文件列表
        if success_count > 0:
            print(f"\n✅ 成功生成的文件:")
            for r in results:
                if r.get("success"):
                    print(f"   {r['file']} - {r['text'][:40]}...")
        
        # 显示失败的项目
        if failed_count > 0:
            print(f"\n❌ 失败的项目:")
            for r in results:
                if not r.get("success"):
                    print(f"   第 {r['line']} 行: {r['text'][:40]}...")
        
        print("\n" + "="*70)
        
        return {
            "success": success_count,
            "failed": failed_count,
            "total": len(texts_to_process),
            "total_time": round(total_time, 2),
            "results": results
        }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='批量文本转语音工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 处理整个文件
  python batch_generate.py input.txt
  
  # 处理指定行范围
  python batch_generate.py input.txt --start 1 --end 10
  
  # 指定输出目录
  python batch_generate.py input.txt --output my_audio
  
  # 使用简单文件名（不基于文本内容）
  python batch_generate.py input.txt --simple-names --prefix audio
        """
    )
    
    parser.add_argument('input_file', help='输入文本文件路径')
    parser.add_argument('--output', '-o', default='data', 
                       help='输出目录（默认: data）')
    parser.add_argument('--start', '-s', type=int, default=1,
                       help='开始行号（默认: 1）')
    parser.add_argument('--end', '-e', type=int, default=None,
                       help='结束行号（默认: 处理到最后）')
    parser.add_argument('--model', '-m', 
                       default='tts_models/en/ljspeech/tacotron2-DDC',
                       help='TTS模型名称')
    parser.add_argument('--simple-names', action='store_true',
                       help='使用简单的序号文件名，而不是基于文本内容')
    parser.add_argument('--prefix', '-p', default='audio',
                       help='简单文件名的前缀（配合 --simple-names 使用）')
    
    args = parser.parse_args()
    
    # 检查输入文件
    if not os.path.exists(args.input_file):
        print(f"❌ 输入文件不存在: {args.input_file}")
        print("\n💡 提示: 创建一个文本文件，每行一段需要转语音的文本")
        print("例如:")
        print("  echo 'Hello, world!' > input.txt")
        print("  echo 'This is a test.' >> input.txt")
        print("  python batch_generate.py input.txt")
        sys.exit(1)
    
    # 创建生成器
    generator = BatchTTSGenerator(
        output_dir=args.output,
        model_name=args.model
    )
    
    # 批量生成
    result = generator.generate_all(
        input_file=args.input_file,
        start_index=args.start,
        end_index=args.end,
        use_custom_names=not args.simple_names,
        name_prefix=args.prefix
    )
    
    # 返回状态码
    if result["success"] > 0:
        print("\n🎉 批量生成完成!")
        sys.exit(0)
    else:
        print("\n❌ 批量生成失败!")
        sys.exit(1)


if __name__ == "__main__":
    # 如果直接运行且没有参数，显示帮助
    if len(sys.argv) == 1:
        print("="*70)
        print("批量文本转语音工具")
        print("="*70)
        print("\n使用方法:")
        print("  python batch_generate.py <输入文件> [选项]")
        print("\n查看完整帮助:")
        print("  python batch_generate.py --help")
        print("\n快速开始:")
        print("  1. 创建输入文件 input.txt，每行一段文本")
        print("  2. 运行: python batch_generate.py input.txt")
        print("  3. 查看生成的音频文件在 data/ 目录")
        print("="*70)
        sys.exit(0)
    
    main()

