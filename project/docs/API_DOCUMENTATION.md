# API 文档

## 智能获取音频URL接口

### 接口说明

智能获取英文语音播放URL。自动判断文本是否已生成，如果存在则直接返回（或续期后返回），如果不存在则生成后返回。

**特点**：
- 🧠 智能判断：自动检测文本是否已存在
- ⚡ 快速响应：已存在的文本无需重新生成
- 🔄 自动续期：过期URL自动续期
- 🎯 灵活配置：可自定义有效期和生成方式

### 接口地址

```
POST /api/get-audio-url/
GET  /api/get-audio-url/  (也支持GET，但推荐POST)
```

### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| text | string | 是 | - | 英文文本，最多1000字符 |
| tts_type | string | 否 | local | 生成方式：local(本地) 或 cloud(云服务) |
| expire_time | integer | 否 | 3600 | URL有效期（秒）：1小时=3600, 24小时=86400, 7天=604800 |

### 请求示例

#### 方式1：POST + JSON

```bash
curl -X POST http://127.0.0.1:8000/api/get-audio-url/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test.",
    "tts_type": "local",
    "expire_time": 3600
  }'
```

#### 方式2：POST + Form Data

```bash
curl -X POST http://127.0.0.1:8000/api/get-audio-url/ \
  -d "text=Hello, this is a test." \
  -d "tts_type=local" \
  -d "expire_time=3600"
```

#### 方式3：GET + Query Parameters

```bash
curl "http://127.0.0.1:8000/api/get-audio-url/?text=Hello&tts_type=local&expire_time=3600"
```

#### Python 示例

```python
import requests

# 方式1：使用requests发送JSON
response = requests.post(
    'http://127.0.0.1:8000/api/get-audio-url/',
    json={
        'text': 'Hello, this is a test.',
        'tts_type': 'local',
        'expire_time': 3600
    }
)

data = response.json()
if data['success']:
    audio_url = data['url']
    print(f"音频URL: {audio_url}")
    print(f"是否新生成: {data['is_new']}")
    print(f"剩余时间: {data['remaining_time']}")
```

```python
# 方式2：使用requests发送表单数据
response = requests.post(
    'http://127.0.0.1:8000/api/get-audio-url/',
    data={
        'text': 'Hello, world!',
        'tts_type': 'cloud',
        'expire_time': 86400  # 24小时
    }
)
```

### 响应格式

#### 成功响应（已存在，直接返回）

```json
{
    "success": true,
    "url": "https://web-audio.tos-cn-beijing.volces.com/audio.wav?X-Amz-...",
    "expire_time": "2024-01-01 14:00:00",
    "remaining_time": "45分钟",
    "is_new": false,
    "is_renewed": false,
    "record_id": 5,
    "tts_type": "local",
    "created_at": "2024-01-01 12:00:00"
}
```

#### 成功响应（已存在但过期，续期后返回）

```json
{
    "success": true,
    "url": "https://web-audio.tos-cn-beijing.volces.com/audio.wav?X-Amz-...",
    "expire_time": "2024-01-01 15:00:00",
    "remaining_time": "1小时0分钟",
    "is_new": false,
    "is_renewed": true,
    "record_id": 5,
    "tts_type": "local",
    "created_at": "2024-01-01 12:00:00"
}
```

#### 成功响应（不存在，新生成）

```json
{
    "success": true,
    "url": "https://web-audio.tos-cn-beijing.volces.com/audio.wav?X-Amz-...",
    "expire_time": "2024-01-01 14:00:00",
    "remaining_time": "1小时0分钟",
    "is_new": true,
    "record_id": 10,
    "tts_type": "local",
    "created_at": "2024-01-01 13:00:00"
}
```

### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| url | string | 音频播放URL（预签名URL） |
| expire_time | string | URL过期时间 |
| remaining_time | string | 剩余有效时间（人类可读） |
| is_new | boolean | 是否新生成（true=新生成，false=使用已有记录） |
| is_renewed | boolean | 是否续期（true=URL已过期并续期，false=URL仍有效） |
| record_id | integer | 记录ID |
| tts_type | string | 生成方式 |
| created_at | string | 记录创建时间 |

### 错误响应

#### 参数错误

```json
{
    "success": false,
    "error": "文本内容不能为空"
}
```

#### 生成失败

```json
{
    "success": false,
    "error": "语音生成失败: 模型加载失败"
}
```

#### 系统错误

```json
{
    "success": false,
    "error": "系统错误: ..."
}
```

## 工作流程

### 流程图

```
接收请求（text, tts_type, expire_time）
           ↓
    数据库中是否存在该文本？
           ↓
    ┌─────┴─────┐
   是            否
    ↓             ↓
URL是否过期？    生成音频
    ↓             ↓
 ┌─┴─┐         上传TOS
是   否          ↓
 ↓   ↓        生成URL
续期 直接        ↓
 ↓   返回    保存记录
 └───┴──────┬───┘
           ↓
       返回URL
```

### 场景说明

#### 场景1：首次请求

```
请求: "Hello, world!" (第一次)
流程: 生成音频 → 上传 → 生成URL
耗时: ~30秒
响应: is_new=true
```

#### 场景2：重复请求（URL有效）

```
请求: "Hello, world!" (第二次，URL未过期)
流程: 直接返回已有URL
耗时: < 1秒
响应: is_new=false, is_renewed=false
```

#### 场景3：重复请求（URL过期）

```
请求: "Hello, world!" (第二次，URL已过期)
流程: 续期URL
耗时: < 1秒
响应: is_new=false, is_renewed=true
```

## 使用建议

### 1. expire_time 选择

| 场景 | 推荐值 | 秒数 |
|------|--------|------|
| 临时测试 | 1小时 | 3600 |
| 当天使用 | 12小时 | 43200 |
| 长期访问 | 7天 | 604800 |

### 2. tts_type 选择

| 类型 | 特点 | 适用场景 |
|------|------|---------|
| local | 速度快，免费 | 开发测试、大量生成 |
| cloud | 音质好，需配置 | 生产环境、高质量要求 |

### 3. 性能优化

**缓存策略**：
```python
# 客户端缓存示例
cache = {}

def get_audio_url(text):
    # 检查本地缓存
    if text in cache:
        cached_data = cache[text]
        # 检查是否过期（留10分钟缓冲）
        if not is_expired(cached_data['expire_time'], buffer=600):
            return cached_data['url']
    
    # 调用API
    response = requests.post(API_URL, json={'text': text})
    data = response.json()
    
    # 更新缓存
    if data['success']:
        cache[text] = data
    
    return data['url']
```

### 4. 错误处理

```python
def safe_get_audio_url(text, max_retries=3):
    for i in range(max_retries):
        try:
            response = requests.post(
                API_URL,
                json={'text': text},
                timeout=60  # 设置超时
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    return data
                else:
                    print(f"错误: {data['error']}")
                    
        except requests.Timeout:
            print(f"超时，重试 {i+1}/{max_retries}")
        except Exception as e:
            print(f"异常: {e}")
    
    return None
```

## 直接上传音频文件接口

### 接口说明

直接上传本地音频文件到云端，无需通过TTS生成。适用于已有录音文件的场景。

**特点**：
- 📁 直接上传：上传本地音频文件到对象存储
- 💾 保存记录：文本和音频信息保存到数据库
- 🔗 生成URL：自动生成预签名URL
- 🎵 多格式支持：支持 .wav, .mp3, .flac, .ogg, .m4a, .aac

### 接口地址

```
POST /api/upload-audio/
```

### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| file_path | string | 是 | - | 本地音频文件的完整路径 |
| text | string | 是 | - | 音频对应的文本内容，最多1000字符 |
| expire_time | integer | 否 | 3600 | URL有效期（秒） |
| tts_type | string | 否 | custom | 类型标记，用于区分来源 |

### 请求示例

#### curl 示例

```bash
curl -X POST http://127.0.0.1:8000/api/upload-audio/ \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/Users/guolei/work/local/stpython/voice_tts/outputs/stage2/hello.wav",
    "text": "Hello, how are you today?",
    "expire_time": 7200,
    "tts_type": "custom"
  }'
```

#### Python 示例

```python
import requests

response = requests.post(
    'http://127.0.0.1:8000/api/upload-audio/',
    json={
        'file_path': '/path/to/your/audio.wav',
        'text': 'Hello world',
        'expire_time': 7200,  # 2小时
        'tts_type': 'custom'
    }
)

data = response.json()
if data['success']:
    print(f"上传成功!")
    print(f"音频URL: {data['url']}")
    print(f"记录ID: {data['record_id']}")
    print(f"过期时间: {data['expire_time']}")
    print(f"对象Key: {data['object_key']}")
```

### 响应格式

#### 成功响应

```json
{
    "success": true,
    "url": "https://web-audio.tos-cn-beijing.volces.com/hello_1701234567890.wav?X-Amz-...",
    "expire_time": "2024-01-01 15:00:00",
    "remaining_time": "2小时0分钟",
    "record_id": 15,
    "tts_type": "custom",
    "object_key": "hello_1701234567890.wav",
    "message": "✅ 音频上传成功"
}
```

#### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 上传是否成功 |
| url | string | 音频播放URL（预签名URL） |
| expire_time | string | URL过期时间 |
| remaining_time | string | 剩余有效时间 |
| record_id | integer | 数据库记录ID |
| tts_type | string | 类型标记 |
| object_key | string | 对象存储中的文件名 |
| message | string | 成功消息 |

### 错误响应

#### 文件路径为空

```json
{
    "success": false,
    "error": "文件路径不能为空"
}
```

#### 文件不存在

```json
{
    "success": false,
    "error": "文件不存在: /path/to/file.wav"
}
```

#### 不支持的音频格式

```json
{
    "success": false,
    "error": "不支持的音频格式: .txt。支持的格式: .wav, .mp3, .flac, .ogg, .m4a, .aac"
}
```

#### 上传失败

```json
{
    "success": false,
    "error": "上传失败: 网络错误"
}
```

### 使用场景

#### 场景1：上传本地录音

```python
# 有一个录音文件，想上传到云端
response = requests.post(
    'http://127.0.0.1:8000/api/upload-audio/',
    json={
        'file_path': '/recordings/my_voice.wav',
        'text': '这是我录制的音频内容',
        'expire_time': 86400  # 24小时
    }
)
```

#### 场景2：批量上传音频文件

```python
import os

audio_dir = '/path/to/audio/files'
audio_files = [
    ('hello.wav', 'Hello, how are you?'),
    ('goodbye.wav', 'Goodbye, see you later!'),
    ('thanks.wav', 'Thank you very much!')
]

for filename, text in audio_files:
    file_path = os.path.join(audio_dir, filename)
    
    response = requests.post(
        'http://127.0.0.1:8000/api/upload-audio/',
        json={
            'file_path': file_path,
            'text': text,
            'expire_time': 604800  # 7天
        }
    )
    
    if response.json()['success']:
        print(f"✅ {filename} 上传成功")
    else:
        print(f"❌ {filename} 上传失败")
```

#### 场景3：配合 outputs 目录使用

```python
# 项目中 outputs/stage2/ 目录下有很多生成的音频
import glob

audio_files = glob.glob('/Users/guolei/work/local/stpython/voice_tts/outputs/stage2/*.wav')

for audio_path in audio_files:
    # 假设文本内容可以从文件名或其他元数据获取
    text = "从文件名或元数据中获取的文本"
    
    response = requests.post(
        'http://127.0.0.1:8000/api/upload-audio/',
        json={
            'file_path': audio_path,
            'text': text,
            'tts_type': 'local_generated'
        }
    )
```

### 注意事项

1. **文件路径**：必须是服务器可访问的本地路径（绝对路径）
2. **文件格式**：仅支持音频格式，其他格式会被拒绝
3. **文件大小**：建议不超过100MB（取决于对象存储配置）
4. **对象Key命名**：系统会自动添加时间戳，避免文件名冲突
5. **原文件保留**：上传后原文件不会被删除

## 其他API接口

### 1. 获取记录列表

```bash
GET /api/records/
GET /api/records/?q=搜索关键词
GET /api/records/?limit=20
```

### 2. 获取记录详情

```bash
GET /api/record/1/
```

详细说明请参考 [README.md](README.md)

## 安全说明

1. **CSRF保护**：此API已禁用CSRF保护，便于外部调用
2. **频率限制**：建议在生产环境添加频率限制
3. **认证授权**：建议添加API Key或Token认证

## 常见问题

### Q1: 相同文本多次请求会重复生成吗？

**A**: 不会。系统会自动检测，只在首次请求时生成，后续请求直接返回已有URL。

### Q2: URL过期后怎么办？

**A**: 系统会自动续期，无需重新生成音频。

### Q3: 如何强制重新生成？

**A**: 当前版本不支持。如需重新生成，请先删除旧记录或修改文本内容。

### Q4: 支持批量请求吗？

**A**: 当前不支持。建议客户端并发调用多次单个请求。

### Q5: 响应时间多长？

**A**: 
- 已存在记录：< 1秒
- 新生成音频：20-60秒（取决于文本长度和生成方式）

## 更新日志

### v1.0.0 (2024-01-01)
- ✅ 初始版本
- ✅ 智能判断文本是否存在
- ✅ 自动续期过期URL
- ✅ 支持自定义有效期
- ✅ 支持本地和云服务两种生成方式

