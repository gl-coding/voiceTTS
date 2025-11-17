"""
Django Admin配置
"""
from django.contrib import admin
from .models import AudioRecord


@admin.register(AudioRecord)
class AudioRecordAdmin(admin.ModelAdmin):
    """音频记录管理"""
    list_display = ['id', 'text_preview', 'tts_type', 'status', 'uptime', 'expire_time']
    list_filter = ['tts_type', 'status', 'uptime']
    search_fields = ['text']
    readonly_fields = ['uptime']
    list_per_page = 20
    
    def text_preview(self, obj):
        """文本预览"""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = '文本内容'

