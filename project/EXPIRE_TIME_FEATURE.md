# URL有效期自定义功能

## 📝 功能说明

系统支持用户自定义预签名URL的有效期，从1小时到7天不等，满足不同场景的需求。

## ⏰ 可选时长

| 选项 | 时长 | 秒数 | 推荐场景 |
|------|------|------|---------|
| 1小时 | 1 hour | 3600 | ⚡ 临时测试、快速分享 |
| 2小时 | 2 hours | 7200 | 📊 短时间演示、会议使用 |
| 6小时 | 6 hours | 21600 | 🌅 半天有效、上午/下午使用 |
| 12小时 | 12 hours | 43200 | 💼 工作时间内有效 |
| 24小时 | 24 hours | 86400 | 📅 一整天使用 |
| 3天 | 3 days | 259200 | 📦 短期项目、周末使用 |
| 7天 | 7 days | 604800 | 🗓️ 长期使用、一周有效 |

## 🎯 使用方法

### 在网页中设置

1. **访问首页**
   ```
   http://127.0.0.1:8000/
   ```

2. **填写表单**
   - 输入英文文本
   - 选择生成方式（本地/云服务）
   - **选择URL有效期**（下拉菜单）

3. **生成并查看**
   - 点击"生成语音"
   - 在结果页查看过期时间
   - 实时显示剩余有效时间

### 在代码中使用

如果需要通过API或程序化方式设置有效期：

```python
from tts_app.services.storage_service import StorageService

storage = StorageService()

# 上传并生成24小时有效的URL
success, url, expire_time, error = storage.upload_and_get_url(
    local_file_path='audio.wav',
    object_key='audio.wav',
    expires=86400  # 24小时
)
```

## 📊 剩余时间显示

系统会智能显示URL的剩余有效时间：

### 格式化规则

- **大于1天**：显示"X天X小时"
  - 示例：`5天12小时`
  
- **大于1小时**：显示"X小时X分钟"
  - 示例：`3小时45分钟`
  
- **小于1小时**：显示"X分钟"
  - 示例：`25分钟`

### 显示位置

1. **结果页面**
   - 在预签名URL下方显示过期时间
   - 绿色徽章显示剩余时间
   - 已过期显示红色"已过期"徽章

2. **记录详情页**
   - 表格中显示完整过期时间
   - 状态徽章（有效/已过期）
   - 蓝色徽章显示剩余时间

3. **记录列表**
   - （可选）可在列表中添加剩余时间列

## ⚠️ 注意事项

### 1. 过期后的处理

- ✅ URL过期后无法访问
- ✅ 文件仍在对象存储中
- ✅ 可以重新生成新的预签名URL（需要重新生成语音）

### 2. 选择建议

**临时分享（1-2小时）**
- 适合即时测试
- 适合会议演示
- 适合一次性使用

**短期使用（6-24小时）**
- 适合当天使用
- 适合开发调试
- 适合内部分享

**长期使用（3-7天）**
- 适合项目周期使用
- 适合外部分享
- 适合存档备份

### 3. 安全考虑

- 有效期越长，安全风险越高
- 敏感内容建议使用较短有效期
- 公开分享建议使用中等有效期（6-24小时）

## 🔧 自定义有效期选项

### 添加新选项

编辑 `tts_app/forms.py`：

```python
EXPIRE_TIME_CHOICES = [
    (3600, '1小时'),
    (7200, '2小时'),
    (21600, '6小时'),
    (43200, '12小时'),
    (86400, '24小时'),
    (259200, '3天'),
    (604800, '7天'),
    # 添加新选项
    (1800, '30分钟'),      # 30分钟
    (1209600, '14天'),     # 2周
    (2592000, '30天'),     # 1个月
]
```

### 修改默认值

在 `forms.py` 中修改 `initial` 参数：

```python
expire_time = forms.ChoiceField(
    label='URL有效期',
    choices=EXPIRE_TIME_CHOICES,
    initial=7200,  # 改为2小时
    widget=forms.Select(attrs={
        'class': 'form-select',
    }),
    help_text='预签名URL的有效时长'
)
```

## 💡 高级功能

### 1. 过期提醒

可以添加定时任务，在URL即将过期时发送提醒：

```python
from datetime import timedelta
from django.utils import timezone

# 查找1小时后过期的记录
expiring_soon = AudioRecord.objects.filter(
    expire_time__lte=timezone.now() + timedelta(hours=1),
    expire_time__gt=timezone.now()
)
```

### 2. 自动清理

定期清理已过期的记录和文件：

```python
# 清理过期记录
expired_records = AudioRecord.objects.filter(
    expire_time__lt=timezone.now()
)

for record in expired_records:
    # 删除对象存储文件
    storage_service.delete_file(record.path)
    # 删除数据库记录
    record.delete()
```

### 3. 统计分析

分析不同有效期的使用情况：

```python
from django.db.models import Count, Avg
from datetime import timedelta

# 统计各时长使用频率
stats = AudioRecord.objects.values('expire_time').annotate(
    count=Count('id')
)
```

## 📈 使用建议

### 场景推荐

| 使用场景 | 推荐有效期 | 原因 |
|---------|-----------|------|
| 开发测试 | 1-2小时 | 快速迭代，及时清理 |
| 演示展示 | 6-12小时 | 覆盖演示时段 |
| 团队协作 | 24小时-3天 | 团队成员有足够时间访问 |
| 客户交付 | 3-7天 | 给客户充足时间下载 |
| 临时分享 | 1-6小时 | 保持链接新鲜度 |
| 存档备份 | 7天 | 留出充足时间转存 |

### 最佳实践

1. **根据实际需求选择**
   - 不要一味选择最长时间
   - 考虑内容的时效性

2. **定期清理**
   - 设置合理的有效期
   - 定期清理过期记录

3. **备份重要文件**
   - 重要音频及时下载到本地
   - 不要完全依赖预签名URL

4. **安全第一**
   - 敏感内容使用短有效期
   - 公开分享注意内容审核

## 🔗 相关文档

- [README.md](README.md) - 项目整体说明
- [SEARCH_FEATURE.md](SEARCH_FEATURE.md) - 搜索功能说明
- Django文档: [Timedelta对象](https://docs.djangoproject.com/en/4.2/ref/utils/#django.utils.timezone)

