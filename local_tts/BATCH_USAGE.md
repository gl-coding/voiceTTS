# 批量文本转语音使用指南

## 📖 功能说明

`batch_generate.py` 是一个批量文本转语音工具，可以从文本文件中读取内容，为每一行生成语音文件。

## 🚀 快速开始

### 1. 准备输入文件

创建一个文本文件（如 `input.txt`），每行一段需要转语音的文本：

```text
Hello, world!
Good morning, how are you today?
This is a test.
```

或者使用提供的示例文件：
```bash
cp example_input.txt my_input.txt
```

### 2. 运行批量生成

```bash
python batch_generate.py input.txt
```

生成的音频文件将保存在 `data/` 目录下。

## 📝 使用方法

### 基础用法

```bash
# 处理整个文件
python batch_generate.py input.txt

# 处理指定行范围（第1行到第10行）
python batch_generate.py input.txt --start 1 --end 10

# 指定输出目录
python batch_generate.py input.txt --output my_audio

# 查看帮助
python batch_generate.py --help
```

### 高级选项

```bash
# 使用简单的序号文件名（而不是基于文本内容）
python batch_generate.py input.txt --simple-names --prefix audio

# 指定不同的TTS模型
python batch_generate.py input.txt --model "tts_models/en/ljspeech/tacotron2-DDC"

# 组合使用多个选项
python batch_generate.py input.txt \
  --output output_audio \
  --start 5 \
  --end 15 \
  --simple-names \
  --prefix speech
```

## 🎯 参数说明

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `input_file` | - | 输入文本文件路径（必需） | - |
| `--output` | `-o` | 输出目录 | `data` |
| `--start` | `-s` | 开始行号（从1开始） | `1` |
| `--end` | `-e` | 结束行号（包含） | 文件末尾 |
| `--model` | `-m` | TTS模型名称 | `tts_models/en/ljspeech/tacotron2-DDC` |
| `--simple-names` | - | 使用简单的序号文件名 | 否（使用基于文本的文件名） |
| `--prefix` | `-p` | 简单文件名的前缀 | `audio` |

## 📁 输出文件命名

### 文件命名规范（与项目统一）

格式：`local_{uuid}_{timestamp}.wav`

**与项目中 `tts_service.py` 保持完全一致的命名格式**

示例：
```
local_4ef8276bc03e_1764637950.wav
local_79723749c3f7_1764637951.wav
local_c7fad659dbe3_1764637952.wav
```

### 格式说明

- `local`: 固定前缀，表示本地生成
- `4ef8276bc03e`: 12位十六进制UUID，确保唯一性  
- `1764637950`: 10位Unix时间戳（秒级）
- `.wav`: 音频文件扩展名

### 命名规范特点

1. **项目统一** - 与 tts_service.py 生成的文件命名格式完全一致
2. **云端兼容** - 可直接上传到对象存储，无需重命名
3. **唯一性保证** - UUID + 时间戳双重保证不重复
4. **简洁固定** - 固定长度约35字符，便于管理
5. **字符安全** - 只包含字母、数字、下划线

### 简单命名（使用 --simple-names）

格式：`{prefix}_{uuid}_{timestamp}.wav`

```
audio_4ef8276bc03e_1764637950.wav
audio_79723749c3f7_1764637951.wav
audio_c7fad659dbe3_1764637952.wav
```

> 注意：即使使用简单命名，也会使用 UUID + 时间戳 确保唯一性

## 💡 使用示例

### 示例1：处理整个文件

```bash
# 创建输入文件
cat > my_texts.txt << EOF
Hello, how are you?
Welcome to our service.
Thank you for visiting.
EOF

# 批量生成
python batch_generate.py my_texts.txt

# 查看生成的文件
ls -lh data/
```

### 示例2：分批处理大文件

```bash
# 假设有一个包含100行的大文件
# 分成5批处理，每批20行

python batch_generate.py large_file.txt --start 1 --end 20 --output batch1
python batch_generate.py large_file.txt --start 21 --end 40 --output batch2
python batch_generate.py large_file.txt --start 41 --end 60 --output batch3
python batch_generate.py large_file.txt --start 61 --end 80 --output batch4
python batch_generate.py large_file.txt --start 81 --end 100 --output batch5
```

### 示例3：生成统一命名的音频库

```bash
# 生成编号统一的音频文件
python batch_generate.py phrases.txt \
  --simple-names \
  --prefix phrase \
  --output audio_library
```

### 示例4：Python脚本中使用

```python
from batch_generate import BatchTTSGenerator

# 创建生成器
generator = BatchTTSGenerator(output_dir="my_output")

# 批量生成
result = generator.generate_all(
    input_file="input.txt",
    start_index=1,
    end_index=10,
    use_custom_names=True
)

print(f"成功: {result['success']} 条")
print(f"失败: {result['failed']} 条")
```

## 📊 输出报告

程序运行后会显示详细的生成报告：

```
======================================================================
批量生成完成!
======================================================================

📊 生成统计:
   总数: 10 条
   成功: 10 条
   失败: 0 条
   总耗时: 45.23 秒
   平均耗时: 4.52 秒/条

📁 输出目录: /path/to/local_tts/data

✅ 成功生成的文件:
   001_Hello_world.wav - Hello, world!
   002_Good_morning_how_are_you.wav - Good morning, how are you today?
   ...
```

## ⚙️ 配置建议

### 模型选择

根据需求选择合适的模型：

| 模型 | 特点 | 适用场景 |
|------|------|---------|
| `tts_models/en/ljspeech/tacotron2-DDC` | 中等质量，速度适中 | 推荐，平衡质量和速度 |
| `tts_models/en/ljspeech/tacotron2-DCA` | 质量更好，速度较慢 | 需要高质量输出 |
| `tts_models/en/vctk/vits` | 多说话人，质量高 | 需要不同声音 |

### 性能优化

- 首次运行会下载模型，请耐心等待
- 模型只加载一次，批量生成速度更快
- GPU环境下速度更快
- 建议分批处理超大文件（>100条）

## 🔧 故障排除

### 问题1：模型下载失败

```bash
# 手动下载模型
export HF_ENDPOINT=https://hf-mirror.com  # 使用镜像
python -c "from TTS.api import TTS; TTS('tts_models/en/ljspeech/tacotron2-DDC')"
```

### 问题2：内存不足

```bash
# 分批处理
python batch_generate.py large.txt --start 1 --end 50
python batch_generate.py large.txt --start 51 --end 100
```

### 问题3：输出目录权限问题

```bash
# 检查目录权限
ls -ld data/

# 创建目录
mkdir -p data
chmod 755 data
```

## 📚 相关文件

- `batch_generate.py` - 批量生成工具（本程序）
- `test.py` - 基础TTS生成器
- `example_input.txt` - 示例输入文件
- `data/` - 默认输出目录
- `BATCH_USAGE.md` - 本文档

## 🌐 上传到云端

### 使用集成工具

`batch_generate_and_upload.py` 可以一键完成生成和上传：

```bash
# 生成并上传（需要Django服务运行）
python batch_upload.py data/ --text input.txt

# 指定API地址和有效期
python batch_upload.py data/ --text input.txt \
  --api http://localhost:8000 \
  --expire 86400  # 24小时

# 只生成不上传
python batch_upload.py data/ --text input.txt --no-upload
```

### 手动上传已生成的音频

如果已经生成了音频，可以手动上传：

```python
import requests
import os
import glob

# 获取所有音频文件
audio_files = glob.glob('data/*.wav')

# 上传到云端
api_url = 'http://localhost:8000/api/upload-audio/'

for audio_file in audio_files:
    # 从文件名推测文本内容（或从原始文本文件读取）
    text = "对应的文本内容"
    
    response = requests.post(
        api_url,
        json={
            'file_path': os.path.abspath(audio_file),
            'text': text,
            'expire_time': 7200,
            'tts_type': 'batch_local'
        }
    )
    
    if response.json().get('success'):
        print(f"✅ {audio_file} 上传成功")
```

### 工作流程

```
1. 本地批量生成音频
   └─> batch_generate.py input.txt
   
2. 上传到云端存储
   └─> batch_generate_and_upload.py input.txt
   
3. 获取云端URL
   └─> 通过 /api/get-audio-url/ 获取
```

## 💬 联系与反馈

如有问题或建议，请查看项目主README或提交issue。

