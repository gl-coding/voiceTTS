# 完整工作流程

## 🎯 工具职责划分

### batch_generate.py
**职责**：批量生成音频文件
- ✅ 读取文本文件
- ✅ 调用本地TTS生成语音
- ✅ 保存到本地目录
- ✅ 使用统一命名格式：`local_{uuid}_{timestamp}.wav`

### batch_upload.py
**职责**：批量上传音频文件
- ✅ 扫描音频文件目录
- ✅ 读取对应文本内容
- ✅ 上传到云端对象存储
- ✅ 生成预签名URL
- ✅ 保存记录到数据库

## 🔄 标准工作流程

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
│                     │
│  ✓ 本地TTS生成      │
│  ✓ 保存到 data/     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  3. 批量上传音频    │
│  batch_upload.py    │
│                     │
│  ✓ 上传到TOS        │
│  ✓ 生成URL          │
│  ✓ 保存到数据库      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  4. 获取/使用URL    │
│  /api/get-audio-url/│
└─────────────────────┘
```

## 📋 详细步骤

### 步骤1：准备文本文件

创建 `input.txt`，每行一段文本：

```bash
cat > input.txt << EOF
Hello, world!
Good morning, how are you?
Welcome to our service.
Thank you for visiting.
EOF
```

### 步骤2：批量生成音频

```bash
# 生成音频
python batch_generate.py input.txt

# 检查生成的文件
ls -lh data/
```

输出文件：
```
data/
├── local_4ef8276bc03e_1764637950.wav
├── local_79723749c3f7_1764637951.wav
├── local_c7fad659dbe3_1764637952.wav
└── local_110d565a917e_1764637953.wav
```

### 步骤3：批量上传到云端

```bash
# 确保Django服务运行
cd ../project
python manage.py runserver &

# 返回local_tts目录
cd ../local_tts

# 批量上传
python batch_upload.py data/ --text input.txt
```

### 步骤4：获取和使用URL

```bash
# 通过API获取URL
curl -X POST http://localhost:8000/api/get-audio-url/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!"}'
```

响应：
```json
{
  "success": true,
  "url": "https://web-audio.tos-cn-beijing.volces.com/...",
  "expire_time": "2025-12-02 12:00:00",
  "is_new": false,
  "record_id": 101
}
```

## 🚀 快速命令

### 一次性完整流程

```bash
# 1. 生成音频
python batch_generate.py example_input.txt

# 2. 上传音频
python batch_generate_and_upload.py data/ --text example_input.txt
```

### 分批处理

```bash
# 生成前10条
python batch_generate.py input.txt --start 1 --end 10

# 上传这批文件（需要对应的文本）
python batch_generate_and_upload.py data/ --text input.txt --pattern "local_*_176463*.wav"
```

## 💡 使用场景

### 场景1：小批量处理（< 20条）

```bash
# 直接一次性处理
python batch_generate.py input.txt
python batch_generate_and_upload.py data/ --text input.txt
```

### 场景2：大批量处理（> 100条）

```bash
# 分批生成
python batch_generate.py input.txt --start 1 --end 50
python batch_generate.py input.txt --start 51 --end 100

# 分批上传
python batch_generate_and_upload.py data/ --text input.txt
```

### 场景3：重新上传失败的文件

```bash
# 查看失败记录
# 筛选出失败的文件

# 只上传特定文件
python batch_generate_and_upload.py data/ --pattern "local_xxx*.wav"
```

### 场景4：不同有效期的内容

```bash
# 生成所有音频
python batch_generate.py all_texts.txt

# 重要内容：7天有效期
python batch_generate_and_upload.py data/ \
  --text important.txt \
  --pattern "local_*_17646370*.wav" \
  --expire 604800

# 临时内容：1小时有效期
python batch_generate_and_upload.py data/ \
  --text temp.txt \
  --pattern "local_*_17646380*.wav" \
  --expire 3600
```

## 📊 文件对应关系

### 文本文件（input.txt）
```
第1行: Hello, world!
第2行: Good morning, how are you?
第3行: Welcome to our service.
```

### 生成的音频文件（data/）
```
第1行 → local_4ef8276bc03e_1764637950.wav
第2行 → local_79723749c3f7_1764637951.wav
第3行 → local_c7fad659dbe3_1764637952.wav
```

### 上传时的对应
```bash
python batch_generate_and_upload.py data/ --text input.txt
```

- 第1个文件 → 第1行文本 → 记录ID: 101
- 第2个文件 → 第2行文本 → 记录ID: 102
- 第3个文件 → 第3行文本 → 记录ID: 103

## 🎯 关键点

### 1. 文件命名统一
- 格式：`local_{uuid}_{timestamp}.wav`
- 与项目其他服务保持一致
- 可直接上传，无需重命名

### 2. 职责分离
- 生成和上传分开
- 更灵活，更易调试
- 可以重复上传

### 3. 文本对应
- 上传时需要文本内容
- 可通过文本文件提供
- 也可使用文件名

### 4. 智能识别
- 相同文本会被识别
- 避免重复上传
- 自动复用URL

## 🔧 调试和测试

### 测试生成

```bash
# 快速测试
python quick_test.py

# 测试命名格式
python test_naming.py
```

### 测试上传

```bash
# 生成测试文件
python quick_test.py

# 上传测试
python batch_generate_and_upload.py data/ --text test_input.txt
```

### 检查结果

```bash
# 查看生成的文件
ls -lh data/

# 查看数据库记录
curl http://localhost:8000/api/records/

# 获取特定文本的URL
curl -X POST http://localhost:8000/api/get-audio-url/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!"}'
```

## 📚 相关文档

- [batch_generate.py](batch_generate.py) - 生成工具
- [batch_upload.py](batch_upload.py) - 上传工具
- [BATCH_USAGE.md](BATCH_USAGE.md) - 生成工具详细文档
- [UPLOAD_GUIDE.md](UPLOAD_GUIDE.md) - 上传工具详细文档
- [QUICK_START.md](QUICK_START.md) - 快速开始指南

## ✅ 检查清单

使用前确认：
- [ ] Python 3.8+已安装
- [ ] TTS库已安装（生成用）
- [ ] Django服务已启动（上传用）
- [ ] 对象存储已配置（上传用）
- [ ] 网络连接正常（上传用）

---

**更新时间**: 2025-12-02  
**版本**: v2.0  
**状态**: ✅ 职责分离完成

