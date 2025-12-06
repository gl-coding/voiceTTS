"""
批量上传音频文件到云端
将已生成的本地音频文件上传到对象存储
"""
import os
import sys
import requests
import time
import glob


class BatchAudioUploader:
    """批量音频上传器"""
    
    def __init__(self, api_url="http://localhost:8000"):
        """
        初始化
        
        Args:
            api_url: Django服务API地址
        """
        self.api_url = api_url
        self.upload_api = f"{api_url}/api/upload-audio/"
    
    def read_text_file(self, text_file):
        """
        读取文本文件
        
        Args:
            text_file: 文本文件路径
            
        Returns:
            list: 文本行列表
        """
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            texts = [line.strip() for line in lines if line.strip()]
            return texts
        except Exception as e:
            print(f"❌ 读取文本文件失败: {e}")
            return []
    
    def upload_from_directory(self, audio_dir, text_file=None, expire_time=7200, pattern="*.wav"):
        """
        从目录上传音频文件
        
        Args:
            audio_dir: 音频文件目录
            text_file: 文本文件路径（可选，每行对应一个音频的文本）
            expire_time: URL有效期（秒）
            pattern: 文件匹配模式
            
        Returns:
            dict: 上传结果
        """
        print("="*70)
        print("批量上传音频文件到云端")
        print("="*70)
        
        # 获取音频文件列表
        audio_pattern = os.path.join(audio_dir, pattern)
        audio_files = sorted(glob.glob(audio_pattern))
        
        if not audio_files:
            print(f"\n❌ 在 {audio_dir} 中没有找到音频文件（模式: {pattern}）")
            return {'success': 0, 'failed': 0, 'total': 0, 'results': []}
        
        print(f"\n找到 {len(audio_files)} 个音频文件")
        print(f"目录: {audio_dir}")
        
        # 读取文本内容（如果提供了文本文件）
        texts = []
        if text_file:
            texts = self.read_text_file(text_file)
            print(f"文本文件: {text_file} ({len(texts)} 行)")
            if len(texts) < len(audio_files):
                print(f"⚠️  警告: 文本行数({len(texts)})少于音频文件数({len(audio_files)})")
        else:
            print("未提供文本文件，将使用文件名作为文本内容")
        
        print("\n" + "="*70)
        print("开始上传...")
        print("="*70)
        
        upload_results = []
        success_count = 0
        failed_count = 0
        
        for i, audio_file in enumerate(audio_files, 1):
            filename = os.path.basename(audio_file)
            
            # 获取对应的文本内容
            if texts and i <= len(texts):
                text = texts[i-1]
            else:
                # 使用文件名作为文本（去除扩展名）
                text = os.path.splitext(filename)[0]
            
            print(f"\n[{i}/{len(audio_files)}] {filename}")
            print(f"文本: {text[:60]}...")
            
            # 上传到云端
            try:
                response = requests.post(
                    self.upload_api,
                    json={
                        'file_path': os.path.abspath(audio_file),
                        'text': text,
                        'expire_time': expire_time,
                        'tts_type': 'batch_upload'
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        success_count += 1
                        print(f"✅ 上传成功!")
                        print(f"   记录ID: {data.get('record_id')}")
                        print(f"   URL: {data.get('url')[:60]}...")
                        
                        upload_results.append({
                            'file': filename,
                            'path': audio_file,
                            'text': text,
                            'success': True,
                            'record_id': data.get('record_id'),
                            'url': data.get('url'),
                            'expire_time': data.get('expire_time')
                        })
                    else:
                        failed_count += 1
                        error = data.get('error', '未知错误')
                        print(f"❌ 上传失败: {error}")
                        upload_results.append({
                            'file': filename,
                            'path': audio_file,
                            'text': text,
                            'success': False,
                            'error': error
                        })
                else:
                    failed_count += 1
                    print(f"❌ 上传失败: HTTP {response.status_code}")
                    upload_results.append({
                        'file': filename,
                        'path': audio_file,
                        'text': text,
                        'success': False,
                        'error': f"HTTP {response.status_code}"
                    })
                    
            except requests.exceptions.ConnectionError:
                failed_count += 1
                print(f"❌ 连接失败！请确保Django服务已启动")
                upload_results.append({
                    'file': filename,
                    'path': audio_file,
                    'text': text,
                    'success': False,
                    'error': '连接失败'
                })
                break
            except Exception as e:
                failed_count += 1
                print(f"❌ 上传异常: {str(e)}")
                upload_results.append({
                    'file': filename,
                    'path': audio_file,
                    'text': text,
                    'success': False,
                    'error': str(e)
                })
            
            # 稍微延迟，避免请求过快
            time.sleep(0.5)
        
        # 生成上传报告
        print("\n" + "="*70)
        print("上传完成!")
        print("="*70)
        
        print(f"\n📊 上传统计:")
        print(f"   总文件数: {len(audio_files)} 个")
        print(f"   上传成功: {success_count} 个")
        print(f"   上传失败: {failed_count} 个")
        
        if success_count > 0:
            print(f"\n✅ 成功上传的文件:")
            for ur in upload_results:
                if ur.get('success'):
                    print(f"   {ur['file']} - 记录ID: {ur['record_id']}")
        
        if failed_count > 0:
            print(f"\n❌ 上传失败的文件:")
            for ur in upload_results:
                if not ur.get('success'):
                    print(f"   {ur['file']}: {ur.get('error')}")
        
        print("\n" + "="*70)
        
        return {
            'success': success_count,
            'failed': failed_count,
            'total': len(audio_files),
            'results': upload_results
        }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='批量上传音频文件到云端',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 上传整个目录的音频
  python batch_generate_and_upload.py data/
  
  # 上传并指定对应的文本文件
  python batch_generate_and_upload.py data/ --text input.txt
  
  # 指定文件匹配模式和有效期
  python batch_generate_and_upload.py data/ --pattern "local_*.wav" --expire 86400
  
  # 指定API地址
  python batch_generate_and_upload.py data/ --api http://192.168.1.100:8000
        """
    )
    
    parser.add_argument('audio_dir', help='音频文件目录')
    parser.add_argument('--text', '-t', default=None,
                       help='文本文件路径（可选，每行对应一个音频的文本）')
    parser.add_argument('--api', default='http://localhost:8000',
                       help='Django服务API地址（默认: http://localhost:8000）')
    parser.add_argument('--pattern', '-p', default='*.wav',
                       help='文件匹配模式（默认: *.wav）')
    parser.add_argument('--expire', type=int, default=7200,
                       help='URL有效期（秒），默认7200（2小时）')
    
    args = parser.parse_args()
    
    # 检查音频目录
    if not os.path.exists(args.audio_dir):
        print(f"❌ 音频目录不存在: {args.audio_dir}")
        sys.exit(1)
    
    if not os.path.isdir(args.audio_dir):
        print(f"❌ 不是有效的目录: {args.audio_dir}")
        sys.exit(1)
    
    # 检查文本文件（如果提供）
    if args.text and not os.path.exists(args.text):
        print(f"❌ 文本文件不存在: {args.text}")
        sys.exit(1)
    
    # 检查服务是否可用
    print("检查Django服务...")
    try:
        response = requests.get(f"{args.api}/", timeout=5)
        print(f"✅ 服务可用: {args.api}\n")
    except:
        print(f"⚠️  警告: 无法连接到 {args.api}")
        print("   请确保Django服务已启动: python manage.py runserver")
        sys.exit(1)
    
    # 创建上传器
    uploader = BatchAudioUploader(api_url=args.api)
    
    # 批量上传
    result = uploader.upload_from_directory(
        audio_dir=args.audio_dir,
        text_file=args.text,
        expire_time=args.expire,
        pattern=args.pattern
    )
    
    # 返回状态码
    if result['success'] > 0:
        print("\n🎉 上传完成!")
        sys.exit(0)
    else:
        print("\n❌ 上传失败!")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("="*70)
        print("批量上传音频文件到云端")
        print("="*70)
        print("\n使用方法:")
        print("  python batch_generate_and_upload.py <音频目录> [选项]")
        print("\n查看完整帮助:")
        print("  python batch_generate_and_upload.py --help")
        print("\n快速开始:")
        print("  1. 确保Django服务已启动")
        print("  2. 运行: python batch_generate_and_upload.py data/")
        print("\n工作流程:")
        print("  1. 使用 batch_generate.py 生成音频")
        print("  2. 使用 batch_generate_and_upload.py 上传音频")
        print("="*70)
        sys.exit(0)
    
    main()

