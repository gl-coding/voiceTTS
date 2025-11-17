"""
TTS应用视图
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import AudioRecord
from .forms import TTSForm
from .services.tts_service import TTSServiceFactory
from .services.storage_service import StorageService
import os
import json


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
    expire_seconds = int(form.cleaned_data['expire_time'])
    
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
            expires=expire_seconds  # 使用用户选择的有效期
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
    """记录列表（支持搜索和分页）"""
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    # 获取搜索关键词
    search_query = request.GET.get('q', '').strip()
    
    # 基础查询
    records = AudioRecord.objects.all()
    
    # 如果有搜索关键词，进行搜索
    if search_query:
        records = records.filter(
            Q(text__icontains=search_query) |  # 文本内容包含关键词
            Q(id__icontains=search_query)       # ID包含关键词
        )
    
    # 按创建时间倒序排列
    records = records.order_by('-uptime')
    
    # 分页，每页10条
    paginator = Paginator(records, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_count': paginator.count,
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
def renew_url(request, record_id):
    """续期预签名URL"""
    record = get_object_or_404(AudioRecord, id=record_id)
    
    # 只有成功的记录才能续期
    if record.status != 'success':
        messages.error(request, '只有成功生成的记录才能续期')
        return redirect('record_detail', record_id=record_id)
    
    # 获取续期时长（秒），默认3600秒（1小时）
    expire_seconds = int(request.POST.get('expire_time', 3600))
    
    try:
        storage_service = StorageService()
        
        # 检查文件是否存在
        if not record.path or not os.path.exists(record.path):
            messages.error(request, '音频文件不存在，无法续期')
            return redirect('record_detail', record_id=record_id)
        
        # 使用现有文件重新生成预签名URL
        object_key = os.path.basename(record.path)
        
        success, preurl, expire_time, error_msg = storage_service.generate_presigned_url(
            object_key=object_key,
            expires=expire_seconds
        )
        
        if success:
            # 更新记录
            record.preurl = preurl
            record.expire_time = expire_time
            record.save()
            
            messages.success(request, f'✅ URL续期成功！新的有效期至 {expire_time.strftime("%Y-%m-%d %H:%M:%S")}')
        else:
            messages.error(request, f'续期失败: {error_msg}')
            
    except Exception as e:
        messages.error(request, f'续期失败: {str(e)}')
    
    return redirect('record_detail', record_id=record_id)


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
@require_http_methods(["POST", "GET"])
def api_get_audio_url(request):
    """
    智能API: 获取音频URL
    
    如果文本已存在且URL有效，直接返回
    如果文本已存在但URL过期，续期后返回
    如果文本不存在，生成后返回
    
    POST参数:
        text: 英文文本（必需）
        tts_type: 生成方式 local/cloud（可选，默认local）
        expire_time: 有效期秒数（可选，默认3600）
        
    返回:
        {
            "success": true,
            "url": "预签名URL",
            "expire_time": "过期时间",
            "is_new": false,  # 是否新生成
            "record_id": 1
        }
    """
    # 获取参数
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except:
                data = {}
        else:
            data = request.POST
    else:
        data = request.GET
    
    text = data.get('text', '').strip()
    tts_type = data.get('tts_type', 'local')
    expire_seconds = int(data.get('expire_time', 3600))
    
    # 验证参数
    if not text:
        return JsonResponse({
            'success': False,
            'error': '文本内容不能为空'
        }, status=400)
    
    if len(text) > 1000:
        return JsonResponse({
            'success': False,
            'error': '文本内容不能超过1000字符'
        }, status=400)
    
    if tts_type not in ['local', 'cloud']:
        return JsonResponse({
            'success': False,
            'error': 'tts_type必须是local或cloud'
        }, status=400)
    
    try:
        # 1. 查找是否已存在相同文本的成功记录
        from django.utils import timezone
        existing_record = AudioRecord.objects.filter(
            text=text,
            status='success'
        ).order_by('-uptime').first()
        
        is_new = False
        
        if existing_record:
            # 记录已存在
            print(f"找到已存在记录 ID: {existing_record.id}")
            
            # 检查URL是否过期
            was_expired = existing_record.is_expired()
            
            if was_expired:
                print("URL已过期，正在续期...")
                # URL过期，续期
                storage_service = StorageService()
                object_key = os.path.basename(existing_record.path)
                
                success, preurl, expire_time, error_msg = storage_service.generate_presigned_url(
                    object_key=object_key,
                    expires=expire_seconds
                )
                
                if success:
                    existing_record.preurl = preurl
                    existing_record.expire_time = expire_time
                    existing_record.save()
                    print("续期成功")
                else:
                    return JsonResponse({
                        'success': False,
                        'error': f'续期失败: {error_msg}'
                    }, status=500)
            else:
                print("URL仍然有效，直接返回")
            
            # 返回现有记录
            return JsonResponse({
                'success': True,
                'url': existing_record.preurl,
                'expire_time': existing_record.expire_time.strftime('%Y-%m-%d %H:%M:%S'),
                'remaining_time': existing_record.get_remaining_time(),
                'is_new': False,
                'is_renewed': was_expired,
                'record_id': existing_record.id,
                'tts_type': existing_record.tts_type,
                'created_at': existing_record.uptime.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        else:
            # 记录不存在，需要生成
            print(f"未找到记录，开始生成新音频...")
            is_new = True
            
            # 创建记录
            record = AudioRecord.objects.create(
                text=text,
                tts_type=tts_type,
                status='pending'
            )
            
            try:
                # 生成语音
                tts_service = TTSServiceFactory.get_service(tts_type)
                success, file_path, error_msg = tts_service.generate_speech(text)
                
                if not success:
                    record.status = 'failed'
                    record.error_message = error_msg
                    record.save()
                    return JsonResponse({
                        'success': False,
                        'error': f'语音生成失败: {error_msg}'
                    }, status=500)
                
                record.path = file_path
                
                # 上传到对象存储并生成URL
                storage_service = StorageService()
                object_key = os.path.basename(file_path)
                
                success, preurl, expire_time, error_msg = storage_service.upload_and_get_url(
                    file_path,
                    object_key=object_key,
                    expires=expire_seconds
                )
                
                if not success:
                    record.status = 'failed'
                    record.error_message = f'上传失败: {error_msg}'
                    record.save()
                    return JsonResponse({
                        'success': False,
                        'error': f'上传失败: {error_msg}'
                    }, status=500)
                
                # 更新记录
                record.preurl = preurl
                record.expire_time = expire_time
                record.status = 'success'
                record.save()
                
                print(f"新音频生成成功 ID: {record.id}")
                
                # 返回新生成的记录
                return JsonResponse({
                    'success': True,
                    'url': record.preurl,
                    'expire_time': record.expire_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'remaining_time': record.get_remaining_time(),
                    'is_new': True,
                    'record_id': record.id,
                    'tts_type': record.tts_type,
                    'created_at': record.uptime.strftime('%Y-%m-%d %H:%M:%S')
                })
                
            except Exception as e:
                record.status = 'failed'
                record.error_message = str(e)
                record.save()
                return JsonResponse({
                    'success': False,
                    'error': f'处理失败: {str(e)}'
                }, status=500)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'系统错误: {str(e)}'
        }, status=500)


# 装饰器版本（免CSRF）
api_get_audio_url = csrf_exempt(api_get_audio_url)


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
    """API: 获取记录列表（JSON格式，支持搜索）"""
    from django.db.models import Q
    
    # 获取参数
    limit = int(request.GET.get('limit', 20))
    search_query = request.GET.get('q', '').strip()
    
    # 基础查询
    records = AudioRecord.objects.all()
    
    # 搜索过滤
    if search_query:
        records = records.filter(
            Q(text__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    # 排序和限制
    records = records.order_by('-uptime')[:limit]
    
    return JsonResponse({
        'success': True,
        'count': len(records),
        'search_query': search_query,
        'data': [record.to_dict() for record in records]
    })

