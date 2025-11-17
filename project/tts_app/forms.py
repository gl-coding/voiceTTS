"""
TTS应用表单
"""
from django import forms
from .models import AudioRecord


class TTSForm(forms.Form):
    """文本转语音表单"""
    
    # 过期时间选项（秒）
    EXPIRE_TIME_CHOICES = [
        (3600, '1小时'),
        (7200, '2小时'),
        (21600, '6小时'),
        (43200, '12小时'),
        (86400, '24小时'),
        (259200, '3天'),
        (604800, '7天'),
    ]
    
    text = forms.CharField(
        label='英文文本',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': '请输入要转换的英文文本...',
            'required': True,
        }),
        max_length=1000,
        help_text='最多1000个字符'
    )
    
    tts_type = forms.ChoiceField(
        label='生成方式',
        choices=AudioRecord.TTS_TYPE_CHOICES,
        initial='local',
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        }),
    )
    
    expire_time = forms.ChoiceField(
        label='URL有效期',
        choices=EXPIRE_TIME_CHOICES,
        initial=3600,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        help_text='预签名URL的有效时长'
    )
    
    def clean_text(self):
        """验证文本"""
        text = self.cleaned_data.get('text', '').strip()
        if not text:
            raise forms.ValidationError('文本内容不能为空')
        if len(text) < 2:
            raise forms.ValidationError('文本内容至少需要2个字符')
        return text

