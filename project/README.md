# 英文语音生成系统

基于Django的英文文本转语音Web应用，支持本地TTS和云服务TTS，自动上传到对象存储并生成预签名URL。

## ✨ 功能特点

- 🎤 **双模式TTS生成**
  - 本地TTS：使用Coqui TTS，适合CPU环境
  - 云服务TTS：使用火山引擎TTS，音质更好
  
- ☁️ **对象存储集成**
  - 自动上传到火山引擎TOS对象存储
  - 生成预签名URL（可自定义有效期：1小时~7天）
  - 支持直接浏览器播放和下载
  - 实时显示URL剩余有效时间

- 📊 **完整的记录管理**
  - 记录列表和详情查看
  - 🔍 **搜索功能**：支持按文本内容或ID搜索
  - 📄 **分页显示**：每页10条记录，完整分页导航
  - 音频在线播放
  - URL复制和下载功能
  - 🔄 **一键续期**：快速为已过期或即将过期的URL续期
  - 记录删除（同时删除对象存储文件）

- 🎨 **现代化UI**
  - 响应式设计，支持移动端
  - Bootstrap 5美化
  - 渐变色主题

## 📋 系统要求

- Python 3.8+
- Django 4.2+
- SQLite（或其他数据库）
- 火山引擎TOS账号（用于对象存储）
- 火山引擎TTS账号（可选，用于云服务TTS）

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /Users/guolei/work/local/stpython/voice_tts/project
pip install -r requirements.txt
```

### 2. 配置环境变量

在终端中设置以下环境变量：

```bash
# TOS对象存储配置（必需）
export TOS_ACCESS_KEY='你的TOS_ACCESS_KEY'
export TOS_SECRET_KEY='你的TOS_SECRET_KEY'

# 火山引擎TTS配置（可选，仅云服务生成需要）
export VOLC_APPID='你的火山引擎AppID'
export VOLC_ACCESS_TOKEN='你的火山引擎AccessToken'
export VOLC_CLUSTER='volcano_tts'
```

或者修改 `tts_project/settings.py` 直接配置（不推荐用于生产环境）：

```python
# TOS对象存储配置
TOS_ACCESS_KEY = "你的密钥"
TOS_SECRET_KEY = "你的密钥"
TOS_BUCKET_NAME = "web-audio"  # 修改为你的桶名称
```

### 3. 初始化数据库

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 创建管理员账号（可选）

```bash
python manage.py createsuperuser
```

### 5. 运行开发服务器

```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000/ 开始使用！

## 📁 项目结构

```
project/
├── manage.py                    # Django管理脚本
├── requirements.txt             # Python依赖
├── README.md                    # 项目说明
├── tts_project/                 # 项目配置目录
│   ├── __init__.py
│   ├── settings.py              # 项目设置
│   ├── urls.py                  # 主路由
│   └── wsgi.py                  # WSGI配置
├── tts_app/                     # 应用目录
│   ├── __init__.py
│   ├── models.py                # 数据模型
│   ├── views.py                 # 视图函数
│   ├── forms.py                 # 表单
│   ├── urls.py                  # 应用路由
│   ├── admin.py                 # 后台管理
│   ├── apps.py                  # 应用配置
│   └── services/                # 服务层
│       ├── tts_service.py       # TTS服务
│       └── storage_service.py   # 对象存储服务
├── templates/                   # 模板目录
│   ├── base.html                # 基础模板
│   └── tts_app/                 # 应用模板
│       ├── index.html           # 首页
│       ├── result.html          # 结果页
│       ├── record_list.html     # 记录列表
│       └── record_detail.html   # 记录详情
└── media/                       # 媒体文件目录
    └── audio/                   # 音频文件存储
```

## 🎯 使用说明

### 1. 生成语音

1. 访问首页
2. 输入英文文本（最多1000字符）
3. 选择生成方式：
   - **本地生成**：速度快，适合开发测试
   - **云服务生成**：音质好，适合生产环境
4. 选择URL有效期（预签名URL的过期时间）：
   - 1小时（默认，适合临时分享）
   - 2小时
   - 6小时
   - 12小时
   - 24小时
   - 3天（适合短期项目）
   - 7天（适合长期使用）
5. 点击"生成语音"按钮
6. 等待处理完成（首次使用会下载模型，需要一些时间）

### 2. 播放和下载

- 生成成功后会自动跳转到结果页
- 可以在线播放音频
- 复制预签名URL分享给他人
- 下载音频到本地

### 3. 管理记录

- 点击"记录列表"查看所有生成记录
- 使用搜索框搜索特定文本或ID
- 使用分页导航浏览大量记录
- 点击"查看"按钮查看记录详情
- 点击"下载"按钮下载音频
- 点击"删除"按钮删除记录（会同时删除对象存储文件）

#### 搜索功能使用

1. 在搜索框中输入关键词（支持英文文本或记录ID）
2. 点击"搜索"按钮或按回车键
3. 查看匹配的搜索结果
4. 点击"清除搜索"返回所有记录

详细说明请查看 [SEARCH_FEATURE.md](SEARCH_FEATURE.md)

#### 续期功能使用

如果预签名URL已过期或即将过期，可以使用续期功能：

1. 在结果页面或记录详情页，点击 **"续期URL"** 按钮
2. 在弹出的对话框中选择新的有效期
3. 点击 **"确认续期"**
4. 系统会生成新的预签名URL（旧URL立即失效）

**优点**：
- ⚡ 无需重新生成音频
- 🚀 快速完成，几秒钟即可
- 💾 节省服务器资源
- 🔄 可多次续期

### 4. API接口

#### 核心接口：智能获取音频URL

🔥 **重点推荐**：这是最常用的API，可以自动判断是否需要生成音频。

```bash
POST /api/get-audio-url/
```

**功能**：
- 传入英文文本
- 如果文本已存在且URL有效 → 直接返回URL（< 1秒）
- 如果文本已存在但URL过期 → 自动续期后返回（< 1秒）
- 如果文本不存在 → 生成音频后返回（20-60秒）

**示例**：
```bash
# 基本用法
curl -X POST http://127.0.0.1:8000/api/get-audio-url/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!"}'

# 指定有效期为24小时
curl -X POST http://127.0.0.1:8000/api/get-audio-url/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, world!",
    "tts_type": "local",
    "expire_time": 86400
  }'
```

**响应示例**：
```json
{
    "success": true,
    "url": "https://web-audio.tos-cn-beijing.volces.com/audio.wav?...",
    "expire_time": "2024-01-01 14:00:00",
    "remaining_time": "1小时0分钟",
    "is_new": false,
    "is_renewed": false,
    "record_id": 5
}
```

详细文档：[API_DOCUMENTATION.md](API_DOCUMENTATION.md)

#### 其他接口

- `GET /api/records/` - 获取记录列表（JSON）
- `GET /api/records/?q=关键词` - 搜索记录
- `GET /api/records/?limit=数量` - 限制返回数量
- `GET /api/record/<id>/` - 获取记录详情（JSON）

示例：
```bash
# 获取所有记录
curl http://127.0.0.1:8000/api/records/

# 搜索包含"hello"的记录
curl http://127.0.0.1:8000/api/records/?q=hello

# 获取最近50条记录
curl http://127.0.0.1:8000/api/records/?limit=50

# 获取单条记录详情
curl http://127.0.0.1:8000/api/record/1/
```

## 🔧 配置说明

### TTS模型配置

修改 `settings.py` 中的 `LOCAL_TTS_MODEL` 可以更换本地TTS模型：

```python
# 轻量级模型（默认，适合CPU）
LOCAL_TTS_MODEL = "tts_models/en/ljspeech/tacotron2-DDC"

# 高质量模型（需要GPU）
LOCAL_TTS_MODEL = "tts_models/en/ljspeech/glow-tts"
```

### 对象存储配置

修改 `settings.py` 中的TOS配置：

```python
TOS_ENDPOINT = "tos-cn-beijing.volces.com"  # 区域端点
TOS_REGION = "cn-beijing"                   # 区域
TOS_BUCKET_NAME = "web-audio"               # 桶名称
```

### URL有效期配置

用户可以在生成语音时选择URL有效期，系统提供以下选项：

| 选项 | 时长（秒） | 适用场景 |
|------|-----------|---------|
| 1小时 | 3600 | 临时测试、快速分享 |
| 2小时 | 7200 | 短时间演示 |
| 6小时 | 21600 | 半天有效 |
| 12小时 | 43200 | 一天工作时间 |
| 24小时 | 86400 | 一整天 |
| 3天 | 259200 | 短期项目 |
| 7天 | 604800 | 长期使用 |

如需添加更多选项，可在 `tts_app/forms.py` 中修改 `EXPIRE_TIME_CHOICES`。

## 🐛 常见问题

### 1. 首次运行速度慢

首次使用本地TTS会自动下载模型文件（约200MB），请耐心等待。

### 2. TOS上传失败

检查以下几点：
- 确认环境变量或配置文件中的AK/SK正确
- 确认桶名称和区域配置正确
- 确认网络连接正常

### 3. 云服务TTS失败

确认火山引擎TTS的AppID和密钥配置正确。

### 4. 音频无法播放

检查预签名URL是否过期，过期后需要重新生成。

## 📝 开发说明

### 添加新的TTS引擎

在 `tts_app/services/tts_service.py` 中添加新的服务类：

```python
class CustomTTSService:
    def generate_speech(self, text):
        # 实现生成逻辑
        return success, file_path, error_message
```

然后在 `TTSServiceFactory` 中注册。

### 自定义模板

所有模板文件在 `templates/tts_app/` 目录下，可以根据需要修改。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📧 联系方式

如有问题，请联系开发者。

