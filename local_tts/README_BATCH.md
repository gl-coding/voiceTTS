# 批量语音生成工具 - 云端规范版

## 🎯 更新说明

### ✨ 新特性

1. **符合云端命名规范** - 所有生成的文件名都可直接上传到对象存储
2. **时间戳唯一性** - 每个文件名包含毫秒级时间戳，确保不重复
3. **一键上传云端** - 新增集成工具，生成后自动上传

### 📝 文件命名规范

#### 新的命名格式

```
local_{uuid}_{timestamp}.wav
```

**与项目中 `tts_service.py` 保持一致的命名格式**

示例：
```
local_4ef8276bc03e_1764637950.wav
local_79723749c3f7_1764637951.wav
local_c7fad659dbe3_1764637952.wav
```

#### 格式说明

- `local`: 固定前缀，表示本地生成
- `4ef8276bc03e`: 12位十六进制UUID，确保唯一性
- `1764637950`: 10位Unix时间戳（秒级）
- `.wav`: 音频文件扩展名

#### 规范要点

- ✅ 只包含字母、数字、下划线
- ✅ UUID + 时间戳双重保证唯一性
- ✅ 固定长度（约35字符），简洁清晰
- ✅ 符合对象存储命名要求
- ✅ 与项目其他TTS服务命名统一

## 🚀 快速开始

### 1. 基础批量生成

```bash
# 生成音频（保存到 data/ 目录）
python batch_generate.py example_input.txt
```

生成文件示例：
```
data/
├── local_4ef8276bc03e_1764637950.wav
├── local_79723749c3f7_1764637951.wav
└── local_c7fad659dbe3_1764637952.wav
```

### 2. 生成并上传到云端

```bash
# 需要先启动Django服务
cd ../project
python manage.py runserver

# 在另一个终端
cd ../local_tts
python batch_upload.py data/ --text example_input.txt
```

### 3. 指定选项

```bash
# 处理指定行范围
python batch_generate.py input.txt --start 1 --end 10

# 使用简单命名
python batch_generate.py input.txt --simple-names --prefix audio

# 指定输出目录
python batch_generate.py input.txt --output my_audio

# 生成并上传，设置2小时有效期
python batch_generate_and_upload.py input.txt --expire 7200
```

## 📦 工具说明

### batch_generate.py

**功能**：批量生成语音文件
- ✅ 从文本文件读取内容
- ✅ 批量生成本地音频
- ✅ 符合云端命名规范
- ✅ 支持范围控制和自定义输出

**使用**：
```bash
python batch_generate.py input.txt [选项]

选项：
  --output, -o        输出目录（默认: data）
  --start, -s         开始行号（默认: 1）
  --end, -e           结束行号（默认: 全部）
  --simple-names      使用简单命名
  --prefix, -p        文件名前缀（默认: audio）
  --help              显示帮助
```

### batch_upload.py

**功能**：上传音频到云端
- ✅ 本地批量生成音频
- ✅ 自动上传到对象存储
- ✅ 生成预签名URL
- ✅ 保存记录到数据库

**使用**：
```bash
python batch_upload.py data/ [选项]

选项：
  --api               API地址（默认: http://localhost:8000）
  --output, -o        本地输出目录（默认: data）
  --start, -s         开始行号（默认: 1）
  --end, -e           结束行号（默认: 全部）
  --expire            URL有效期秒数（默认: 7200）
  --no-upload         只生成不上传
  --help              显示帮助
```

### quick_test.py

**功能**：快速测试（生成3个测试音频）
```bash
python quick_test.py
```

## 💡 使用示例

### 示例1：处理10行文本

```bash
# 创建输入文件
cat > test.txt << EOF
Hello, how are you?
Good morning everyone.
Welcome to our service.
Thank you for visiting.
Have a great day!
See you later.
Artificial intelligence is amazing.
Machine learning is the future.
Natural language processing works well.
Text to speech is very useful.
EOF

# 生成音频
python batch_generate.py test.txt
```

### 示例2：生成并上传前5条

```bash
# 启动Django服务
cd ../project
python manage.py runserver &

# 生成并上传
cd ../local_tts
python batch_generate_and_upload.py test.txt --start 1 --end 5
```

输出：
```
【步骤1】本地生成音频...
[1/5] 第 1 行
文本: Hello, how are you?
✅ 成功! 耗时: 2.15秒

【步骤2】上传到云端...
[1/5] 上传第 1 行
✅ 上传成功!
   记录ID: 101
   URL: https://web-audio.tos-cn-beijing.volces.com/...
```

### 示例3：只生成不上传

```bash
# 只在本地生成，不上传
python batch_generate_and_upload.py test.txt --no-upload
```

### 示例4：使用哈利波特文本

```bash
# 处理前20句
python batch_generate.py 6Harry_Potter_and_The_Half_Blood_Prince_sentences.txt \
  --start 1 --end 20 \
  --output harry_potter_audio
```

## 📊 文件命名对比

### 旧版命名（不符合云端规范）
```
❌ 001_Hello_world.wav                    # 缺少唯一标识
❌ 002_Good morning, how are you?.wav     # 包含空格和问号
❌ 003_你好世界.wav                        # 包含中文
```

### 新版命名（符合云端规范）
```
✅ local_4ef8276bc03e_1764637950.wav      # UUID + 时间戳
✅ local_79723749c3f7_1764637951.wav      # 与项目保持一致
✅ local_c7fad659dbe3_1764637952.wav      # 简洁固定格式
```

### 与项目其他服务对比

**项目TTS服务生成的文件名**（`tts_service.py`）：
```
local_d42cee267ac1_1764167774.wav
cloud_5c55886e5354_1764086426.wav
```

**批量生成工具生成的文件名**（`batch_generate.py`）：
```
local_4ef8276bc03e_1764637950.wav  ✅ 格式完全一致
local_79723749c3f7_1764637951.wav  ✅ 格式完全一致
```

## 🔗 与云端集成

### 工作流程

```
┌─────────────────────┐
│  1. 准备文本文件    │
│     input.txt       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  2. 批量生成音频    │
│  batch_generate.py  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  3. 上传到云端      │
│  /api/upload-audio/ │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  4. 获取URL         │
│  /api/get-audio-url/│
└─────────────────────┘
```

### 手动上传已生成的文件

```python
import requests
import os

# 上传单个文件
file_path = "data/batch_001_Hello_world_1733123456789.wav"
text = "Hello, world!"

response = requests.post(
    'http://localhost:8000/api/upload-audio/',
    json={
        'file_path': os.path.abspath(file_path),
        'text': text,
        'expire_time': 7200
    }
)

result = response.json()
if result['success']:
    print(f"URL: {result['url']}")
    print(f"记录ID: {result['record_id']}")
```

## 📚 相关文件

- `batch_generate.py` - 批量生成工具
- `batch_generate_and_upload.py` - 生成并上传工具
- `quick_test.py` - 快速测试脚本
- `example_input.txt` - 示例输入文件
- `BATCH_USAGE.md` - 详细使用文档
- `test.py` - 基础TTS生成器

## ⚙️ 系统要求

### 本地生成
- Python 3.8+
- TTS库（Coqui TTS）
- PyTorch

### 上传到云端
- Django服务运行中
- 网络连接
- 对象存储配置完成

## 🎉 新版优势

| 特性 | 旧版 | 新版 |
|------|------|------|
| 文件命名 | ❌ 不规范 | ✅ 符合云端标准 |
| 唯一性 | ❌ 可能重复 | ✅ 时间戳保证 |
| 云端上传 | ❌ 手动操作 | ✅ 一键完成 |
| 特殊字符 | ❌ 可能包含 | ✅ 自动过滤 |
| 批量处理 | ✅ 支持 | ✅ 支持 |

## 🔧 故障排除

### 问题1：上传失败 - 连接错误

```bash
# 检查Django服务是否运行
curl http://localhost:8000/

# 启动服务
cd ../project
python manage.py runserver
```

### 问题2：文件名太长

```bash
# 文件名会自动截断到合理长度
# 简短标识最多30字符，总长度不超过100字符
```

### 问题3：时间戳冲突

```bash
# 极少发生，因为使用毫秒级时间戳
# 即使同时生成，时间戳也会不同
```

## 📈 性能建议

1. **批量生成**：一次生成所有音频，然后统一上传（更快）
2. **分批处理**：大文件（>100行）建议分批处理
3. **网络优化**：本地网络环境下上传速度更快
4. **并发控制**：避免同时上传过多文件

## ✅ 快速检查清单

- [ ] 创建输入文本文件
- [ ] 安装必要依赖（TTS、PyTorch）
- [ ] 测试本地生成：`python quick_test.py`
- [ ] 启动Django服务（如需上传）
- [ ] 运行批量生成
- [ ] 检查生成的文件
- [ ] （可选）上传到云端
- [ ] 验证文件命名符合规范

## 🎯 总结

新版批量生成工具：
- ✅ **规范命名** - 符合云端对象存储要求
- ✅ **唯一性** - 时间戳保证不重复
- ✅ **易集成** - 一键生成并上传
- ✅ **向后兼容** - 保留所有原有功能

开始使用：
```bash
python quick_test.py
```

