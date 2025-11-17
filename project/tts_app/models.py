"""
TTS应用数据库模型
"""
from django.db import models
from django.utils import timezone


class AudioRecord(models.Model):
    """音频记录模型"""
    
    TTS_TYPE_CHOICES = [
        ('local', '本地生成'),
        ('cloud', '云服务生成'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '处理中'),
        ('success', '成功'),
        ('failed', '失败'),
    ]
    
    text = models.TextField(verbose_name='文本内容', help_text='要转换的英文文本')
    tts_type = models.CharField(
        max_length=10, 
        choices=TTS_TYPE_CHOICES, 
        default='local',
        verbose_name='生成方式'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态'
    )
    preurl = models.URLField(
        max_length=500, 
        null=True, 
        blank=True,
        verbose_name='预签名URL'
    )
    path = models.CharField(
        max_length=300, 
        null=True, 
        blank=True,
        verbose_name='文件路径'
    )
    uptime = models.DateTimeField(
        default=timezone.now,
        verbose_name='创建时间'
    )
    expire_time = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='过期时间'
    )
    error_message = models.TextField(
        null=True, 
        blank=True,
        verbose_name='错误信息'
    )
    
    class Meta:
        db_table = 'audio_records'
        verbose_name = '音频记录'
        verbose_name_plural = '音频记录'
        ordering = ['-uptime']
    
    def __str__(self):
        return f"[{self.get_tts_type_display()}] {self.text[:30]}..."
    
    def is_expired(self):
        """判断是否过期"""
        if self.expire_time:
            return timezone.now() > self.expire_time
        return False
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'text': self.text,
            'tts_type': self.tts_type,
            'tts_type_display': self.get_tts_type_display(),
            'status': self.status,
            'status_display': self.get_status_display(),
            'preurl': self.preurl,
            'path': self.path,
            'uptime': self.uptime.strftime('%Y-%m-%d %H:%M:%S'),
            'expire_time': self.expire_time.strftime('%Y-%m-%d %H:%M:%S') if self.expire_time else None,
            'is_expired': self.is_expired(),
            'error_message': self.error_message,
        }

