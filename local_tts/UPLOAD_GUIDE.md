# 批量上传工具使用指南

## 🎯 功能说明

`batch_upload.py` - 专门用于批量上传已生成的音频文件到云端。

**职责分离**：
- `batch_generate.py` - 负责生成音频
- `batch_upload.py` - 负责上传音频

## 🚀 快速开始

### 完整工作流程

```bash
# 步骤1: 生成音频
python batch_generate.py example_input.txt

# 步骤2: 上传到云端（需要Django服务运行）
python batch_upload.py data/
```

## 📝 详细使用

### 1. 基础上传

上传整个目录的音频文件：

```bash
python batch_generate_and_upload.py data/
```

### 2. 指定文本文件

如果有对应的文本文件（每行对应一个音频）：

```bash
python batch_generate_and_upload.py data/ --text example_input.txt
```

文本文件示例（`example_input.txt`）：
```
Hello, world!
Good morning, how are you?
This is a test.
```

### 3. 指定文件匹配模式

只上传特定模式的文件：

```bash
# 只上传 local_ 开头的文件
python batch_generate_and_upload.py data/ --pattern "local_*.wav"

# 只上传特定时间的文件
python batch_generate_and_upload.py data/ --pattern "*_1764637950.wav"
```

### 4. 设置URL有效期

```bash
# 设置24小时有效期
python batch_generate_and_upload.py data/ --expire 86400

# 设置7天有效期
python batch_generate_and_upload.py data/ --expire 604800
```

### 5. 指定API地址

```bash
python batch_generate_and_upload.py data/ --api http://192.168.1.100:8000
```

## 🎮 命令行参数

| 参数 | 简写 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `audio_dir` | - | 是 | - | 音频文件目录 |
| `--text` | `-t` | 否 | None | 文本文件（每行对应一个音频） |
| `--api` | - | 否 | http://localhost:8000 | Django服务地址 |
| `--pattern` | `-p` | 否 | *.wav | 文件匹配模式 |
| `--expire` | - | 否 | 7200 | URL有效期（秒） |

## 💡 使用场景

### 场景1：完整工作流

```bash
# 1. 生成音频
python batch_generate.py input.txt

# 2. 检查生成的文件
ls -lh data/

# 3. 上传到云端
python batch_generate_and_upload.py data/ --text input.txt
```

### 场景2：只上传部分文件

```bash
# 只上传今天生成的文件
python batch_generate_and_upload.py data/ --pattern "local_*_17646*.wav"

# 只上传前10个文件
# （需要先排序筛选，或使用其他方法）
```

### 场景3：重新上传

```bash
# 如果上传失败，可以重新运行
python batch_generate_and_upload.py data/ --text input.txt
```

> 注意：如果文本内容相同，系统会识别为已存在的记录

### 场景4：不同有效期

```bash
# 重要内容：7天有效期
python batch_generate_and_upload.py important/ --expire 604800

# 临时内容：1小时有效期  
python batch_generate_and_upload.py temp/ --expire 3600
```

## 📊 输出示例

```bash
$ python batch_generate_and_upload.py data/ --text example_input.txt

======================================================================
批量上传音频文件到云端
======================================================================

找到 3 个音频文件
目录: data
文本文件: example_input.txt (3 行)

======================================================================
开始上传...
======================================================================

[1/3] local_4ef8276bc03e_1764637950.wav
文本: Hello, world!...
✅ 上传成功!
   记录ID: 101
   URL: https://web-audio.tos-cn-beijing.volces.com/...

[2/3] local_79723749c3f7_1764637951.wav
文本: Good morning, how are you?...
✅ 上传成功!
   记录ID: 102
   URL: https://web-audio.tos-cn-beijing.volces.com/...

[3/3] local_c7fad659dbe3_1764637952.wav
文本: This is a test....
✅ 上传成功!
   记录ID: 103
   URL: https://web-audio.tos-cn-beijing.volces.com/...

======================================================================
上传完成!
======================================================================

📊 上传统计:
   总文件数: 3 个
   上传成功: 3 个
   上传失败: 0 个

✅ 成功上传的文件:
   local_4ef8276bc03e_1764637950.wav - 记录ID: 101
   local_79723749c3f7_1764637951.wav - 记录ID: 102
   local_c7fad659dbe3_1764637952.wav - 记录ID: 103

======================================================================

🎉 上传完成!
```

## 🔄 与其他工具配合

### 与 batch_generate.py 配合

```bash
# 完整流程
python batch_generate.py input.txt
python batch_generate_and_upload.py data/ --text input.txt
```

### 获取云端URL

上传后，可以通过智能接口获取：

```bash
curl -X POST http://localhost:8000/api/get-audio-url/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!"}'
```

## ⚙️ 配置要求

### Django服务必须运行

```bash
# 在 project 目录启动服务
cd ../project
python manage.py runserver

# 或后台运行
nohup python manage.py runserver > /dev/null 2>&1 &
```

### 环境变量

确保 Django 配置了对象存储：

```bash
export TOS_ACCESS_KEY='your_access_key'
export TOS_SECRET_KEY='your_secret_key'
```

## 🔧 故障排除

### 问题1：连接失败

```
❌ 警告: 无法连接到 http://localhost:8000
```

**解决方案**：
```bash
# 检查Django服务是否运行
curl http://localhost:8000/

# 启动服务
cd ../project
python manage.py runserver
```

### 问题2：找不到音频文件

```
❌ 在 data/ 中没有找到音频文件（模式: *.wav）
```

**解决方案**：
```bash
# 检查目录
ls -lh data/

# 检查匹配模式
python batch_generate_and_upload.py data/ --pattern "local_*.wav"
```

### 问题3：文本行数不匹配

```
⚠️  警告: 文本行数(3)少于音频文件数(5)
```

**说明**：
- 前N个文件使用文本文件中的内容
- 剩余文件使用文件名作为文本

**解决方案**：
```bash
# 补全文本文件，或不指定文本文件
python batch_generate_and_upload.py data/
```

### 问题4：上传重复

如果文本内容相同，系统会识别为已存在：

```json
{
  "success": true,
  "is_new": false,
  "message": "文本已存在，返回已有记录"
}
```

## 📚 相关文档

- [batch_generate.py](batch_generate.py) - 批量生成工具
- [BATCH_USAGE.md](BATCH_USAGE.md) - 生成工具使用指南
- [README_BATCH.md](README_BATCH.md) - 完整文档
- [QUICK_START.md](QUICK_START.md) - 快速开始

## 💡 最佳实践

1. **先生成后上传**
   ```bash
   python batch_generate.py input.txt
   python batch_generate_and_upload.py data/ --text input.txt
   ```

2. **保留文本文件**
   - 文本文件是上传的重要依据
   - 建议与音频文件对应保存

3. **合理设置有效期**
   - 测试：1小时（3600）
   - 日常：2小时（7200，默认）
   - 长期：7天（604800）

4. **分批上传**
   - 大量文件建议分批上传
   - 避免单次上传过多

## ✅ 检查清单

上传前检查：
- [ ] Django服务已启动
- [ ] 音频文件已生成
- [ ] （可选）文本文件已准备
- [ ] 网络连接正常
- [ ] 对象存储配置正确

---

**更新时间**: 2025-12-02  
**版本**: v2.0  
**状态**: ✅ 功能独立

