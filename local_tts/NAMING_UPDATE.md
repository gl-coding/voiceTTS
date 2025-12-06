# 文件命名规范更新说明

## 🎯 更新内容

已将批量生成工具的文件命名格式更新为与项目统一的格式。

### 新的命名格式

```
local_{uuid}_{timestamp}.wav
```

### 格式对比

#### ❌ 旧格式（已弃用）
```
batch_001_Hello_world_1733123456789.wav
batch_002_Good_morning_how_1733123457890.wav
```

**问题**：
- 包含文本内容，可能有特殊字符
- 依赖行号，不够通用
- 与项目其他服务不一致

#### ✅ 新格式（当前）
```
local_4ef8276bc03e_1764637950.wav
local_79723749c3f7_1764637951.wav
```

**优势**：
- ✅ 与 `tts_service.py` 完全一致
- ✅ UUID + 时间戳双重保证唯一性
- ✅ 固定格式，简洁清晰
- ✅ 只包含安全字符（字母、数字、下划线）
- ✅ 无需担心特殊字符或中文

## 📋 格式详解

### 结构
```
local_{uuid}_{timestamp}.wav
 │     │       │         │
 │     │       │         └─ 扩展名
 │     │       └─ Unix时间戳（秒级，10位）
 │     └─ UUID（12位十六进制）
 └─ 前缀（表示本地生成）
```

### 示例分析
```
local_4ef8276bc03e_1764637950.wav
```

- **local**: 固定前缀
  - 表示本地TTS生成
  - 与云端生成的 `cloud_xxx` 区分
  
- **4ef8276bc03e**: UUID
  - 长度：12位
  - 格式：十六进制（0-9, a-f）
  - 作用：确保全局唯一性
  
- **1764637950**: 时间戳
  - 长度：10位
  - 格式：Unix时间戳（秒）
  - 作用：时间排序和二次唯一性保证

## 🔄 与项目其他服务的对比

### TTS Service (`tts_service.py`)

**本地生成**：
```python
filename = f"local_{uuid.uuid4().hex[:12]}_{int(datetime.now().timestamp())}.wav"
# 输出: local_d42cee267ac1_1764167774.wav
```

**云端生成**：
```python
filename = f"cloud_{uuid.uuid4().hex[:12]}_{int(datetime.now().timestamp())}.wav"
# 输出: cloud_5c55886e5354_1764086426.wav
```

### 批量生成工具 (`batch_generate.py`)

**现在的命名**：
```python
filename = f"local_{uuid.uuid4().hex[:12]}_{int(datetime.now().timestamp())}.wav"
# 输出: local_4ef8276bc03e_1764637950.wav
```

**完全一致！✅**

## 🎉 兼容性说明

### 向后兼容
- 旧版本生成的文件不受影响
- 可以继续使用已生成的旧格式文件
- 新生成的文件使用新格式

### 上传兼容
- 新格式完全符合云端规范
- 可直接通过 `/api/upload-audio/` 上传
- 可被 `/api/get-audio-url/` 正确识别

## 🚀 使用方法

### 生成音频（自动使用新格式）
```bash
python batch_generate.py example_input.txt
```

生成文件：
```
data/
├── local_4ef8276bc03e_1764637950.wav
├── local_79723749c3f7_1764637951.wav
└── local_c7fad659dbe3_1764637952.wav
```

### 验证命名格式
```bash
python test_naming.py
```

输出示例：
```
行   1: Hello, world!...
        → local_4ef8276bc03e_1764637950.wav
        验证: ✅ 前缀正确 | ✅ UUID格式正确 | ✅ 时间戳正确 | ✅ 字符合法 | ✅ 长度合理 | ✅ 扩展名正确
```

## 📝 更新的文件

- ✅ `batch_generate.py` - 主程序（更新命名逻辑）
- ✅ `batch_upload.py`（原名 `batch_generate_and_upload.py`） - 上传工具
- ✅ `test_naming.py` - 测试工具（更新验证逻辑）
- ✅ `README_BATCH.md` - 文档（更新说明）
- ✅ `BATCH_USAGE.md` - 使用文档（更新示例）
- ✅ `NAMING_UPDATE.md` - 本更新说明

## ✅ 测试结果

所有测试通过：
```bash
$ python test_naming.py
======================================================================
✅ 文件命名规范测试完成!

新的命名格式: local_{uuid}_{timestamp}.wav

特点:
  ✓ 与项目中 tts_service.py 保持一致
  ✓ 只包含字母、数字、下划线
  ✓ UUID + 时间戳双重保证唯一性
  ✓ 符合云端对象存储命名规范
  ✓ 文件名简洁固定长度
======================================================================
```

## 📊 对比总结

| 特性 | 旧格式 | 新格式 |
|------|--------|--------|
| 格式 | `batch_{序号}_{文本}_{时间戳}.wav` | `local_{uuid}_{timestamp}.wav` |
| 与项目统一 | ❌ 不一致 | ✅ 完全一致 |
| 唯一性 | ⚠️ 序号+时间戳 | ✅ UUID+时间戳 |
| 文件名长度 | ❌ 可变（30-80字符） | ✅ 固定（约35字符） |
| 特殊字符 | ⚠️ 需要过滤 | ✅ 无需担心 |
| 云端兼容 | ✅ 兼容 | ✅ 兼容 |
| 可读性 | ⚠️ 包含文本 | ⚠️ 不含文本 |

## 💡 建议

1. **新项目**：直接使用新格式
2. **旧项目**：
   - 保留旧文件不影响使用
   - 新生成使用新格式
   - 可选：批量重命名旧文件

3. **文本记录**：
   - 文件名不再包含文本内容
   - 建议维护一个文本-文件映射表
   - 或使用数据库记录对应关系

## 🔗 相关文档

- [README_BATCH.md](README_BATCH.md) - 批量工具完整说明
- [BATCH_USAGE.md](BATCH_USAGE.md) - 详细使用文档
- [test_naming.py](test_naming.py) - 命名格式测试工具

---

**更新时间**: 2025-12-02  
**版本**: v2.0  
**状态**: ✅ 已完成

