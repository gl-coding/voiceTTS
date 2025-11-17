"""
TTS应用视图
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import AudioRecord
from .forms import TTSForm
from .services.tts_service import TTSServiceFactory
from .services.storage_service import StorageService
import os


def index(request):
    """首页 - TTS表单"""
    form = TTSForm()
    recent_records = AudioRecord.objects.filter(status='success')[:10]
    
    context = {
        'form': form,
        'recent_records': recent_records,
    }
    return render(request, 'tts_app/index.html', context)


@require_http_methods(["POST"])
def generate_tts(request):
    """
    生成语音
    处理流程：
    1. 验证表单
    2. 调用TTS服务生成语音
    3. 上传到对象存储
    4. 生成预签名URL
    5. 保存记录到数据库
    """
    form = TTSForm(request.POST)
    
    if not form.is_valid():
        messages.error(request, '表单验证失败，请检查输入')
        return redirect('index')
    
    text = form.cleaned_data['text']
    tts_type = form.cleaned_data['tts_type']
    
    # 创建记录（初始状态为pending）
    record = AudioRecord.objects.create(
        text=text,
        tts_type=tts_type,
        status='pending'
    )
    
    try:
        # 1. 生成语音
        tts_service = TTSServiceFactory.get_service(tts_type)
        success, file_path, error_msg = tts_service.generate_speech(text)
        
        if not success:
            record.status = 'failed'
            record.error_message = error_msg
            record.save()
            messages.error(request, f'语音生成失败: {error_msg}')
            return redirect('index')
        
        # 保存本地路径
        record.path = file_path
        
        # 2. 上传到对象存储并生成预签名URL
        storage_service = StorageService()
        
        # 使用唯一的对象key
        object_key = os.path.basename(file_path)
        
        success, preurl, expire_time, error_msg = storage_service.upload_and_get_url(
            file_path,
            object_key=object_key,
            expires=3600  # 1小时有效期
        )
        
        if not success:
            record.status = 'failed'
            record.error_message = f'上传失败: {error_msg}'
            record.save()
            messages.error(request, f'文件上传失败: {error_msg}')
            return redirect('index')
        
        # 3. 更新记录状态
        record.preurl = preurl
        record.expire_time = expire_time
        record.status = 'success'
        record.save()
        
        messages.success(request, '✅ 语音生成成功！')
        return redirect('result', record_id=record.id)
        
    except Exception as e:
        record.status = 'failed'
        record.error_message = str(e)
        record.save()
        messages.error(request, f'处理失败: {str(e)}')
        return redirect('index')


def result(request, record_id):
    """显示生成结果"""
    record = get_object_or_404(AudioRecord, id=record_id)
    
    context = {
        'record': record,
    }
    return render(request, 'tts_app/result.html', context)


def record_list(request):
    """记录列表"""
    records = AudioRecord.objects.all()[:50]
    
    context = {
        'records': records,
    }
    return render(request, 'tts_app/record_list.html', context)


def record_detail(request, record_id):
    """记录详情"""
    record = get_object_or_404(AudioRecord, id=record_id)
    
    context = {
        'record': record,
    }
    return render(request, 'tts_app/record_detail.html', context)


@require_http_methods(["POST"])
def delete_record(request, record_id):
    """删除记录"""
    record = get_object_or_404(AudioRecord, id=record_id)
    
    try:
        # 从对象存储删除文件
        if record.path:
            storage_service = StorageService()
            object_key = os.path.basename(record.path)
            storage_service.delete_file(object_key)
        
        # 删除本地文件
        if record.path and os.path.exists(record.path):
            os.remove(record.path)
        
        # 删除数据库记录
        record.delete()
        
        messages.success(request, '记录已删除')
    except Exception as e:
        messages.error(request, f'删除失败: {str(e)}')
    
    return redirect('record_list')


# API接口
@require_http_methods(["GET"])
def api_record_detail(request, record_id):
    """API: 获取记录详情（JSON格式）"""
    try:
        record = AudioRecord.objects.get(id=record_id)
        return JsonResponse({
            'success': True,
            'data': record.to_dict()
        })
    except AudioRecord.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '记录不存在'
        }, status=404)


@require_http_methods(["GET"])
def api_record_list(request):
    """API: 获取记录列表（JSON格式）"""
    limit = int(request.GET.get('limit', 20))
    records = AudioRecord.objects.all()[:limit]
    
    return JsonResponse({
        'success': True,
        'count': len(records),
        'data': [record.to_dict() for record in records]
    })

