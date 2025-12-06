# 快速开始指南

## 🎯 文件命名格式

**新格式**：`local_{uuid}_{timestamp}.wav`

**示例**：
```
local_4ef8276bc03e_1764637950.wav
```

与项目 `tts_service.py` 保持完全一致！✅

## 🚀 立即开始

### 1. 测试命名格式
```bash
cd /Users/guolei/work/local/stpython/voice_tts/local_tts
python test_naming.py
```

### 2. 快速测试（生成3个音频）
```bash
python quick_test.py
```

### 3. 批量生成
```bash
python batch_generate.py example_input.txt
```

生成的文件：
```
data/
├── local_4ef8276bc03e_1764637950.wav
├── local_79723749c3f7_1764637951.wav
└── local_c7fad659dbe3_1764637952.wav
```

### 4. 生成并上传到云端
```bash
# 1. 启动Django服务
cd ../project
python manage.py runserver &

# 2. 批量生成并上传
cd ../local_tts
python batch_upload.py data/ --text example_input.txt
```

## 📖 详细文档

- [NAMING_UPDATE.md](NAMING_UPDATE.md) - 命名格式更新说明
- [README_BATCH.md](README_BATCH.md) - 批量工具完整说明
- [BATCH_USAGE.md](BATCH_USAGE.md) - 详细使用文档

## ✅ 验证

运行测试验证命名格式：
```bash
$ python test_naming.py

行   1: Hello, world!...
        → local_4ef8276bc03e_1764637950.wav
        验证: ✅ 前缀正确 | ✅ UUID格式正确 | ✅ 时间戳正确 | ✅ 字符合法 | ✅ 长度合理 | ✅ 扩展名正确
```

所有验证通过！🎉

