"""
TTS应用视图
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import AudioRecord, VideoRecord
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


@require_http_methods(["POST"])
@csrf_exempt
def api_upload_audio(request):
    """
    API: 直接上传本地音频文件到云端
    
    功能：
    - 上传指定路径的本地音频文件到对象存储
    - 生成预签名URL
    - 保存记录到数据库
    
    POST参数（JSON格式）:
        file_path: 本地音频文件路径（必需）
        text: 文本内容（必需）
        expire_time: 有效期秒数（可选，默认3600）
        tts_type: 标记类型（可选，默认custom）
        
    返回:
        {
            "success": true,
            "url": "预签名URL",
            "expire_time": "过期时间",
            "record_id": 1,
            "message": "上传成功"
        }
    """
    # 解析JSON参数
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': '无效的JSON格式'
            }, status=400)
    else:
        data = request.POST
    
    file_path = data.get('file_path', '').strip()
    text = data.get('text', '').strip()
    expire_seconds = int(data.get('expire_time', 3600))
    tts_type = data.get('tts_type', 'custom')
    
    # 验证参数
    if not file_path:
        return JsonResponse({
            'success': False,
            'error': '文件路径不能为空'
        }, status=400)
    
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
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return JsonResponse({
            'success': False,
            'error': f'文件不存在: {file_path}'
        }, status=404)
    
    # 检查是否是音频文件
    allowed_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac']
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in allowed_extensions:
        return JsonResponse({
            'success': False,
            'error': f'不支持的音频格式: {file_ext}。支持的格式: {", ".join(allowed_extensions)}'
        }, status=400)
    
    # 创建数据库记录
    record = AudioRecord.objects.create(
        text=text,
        tts_type=tts_type,
        status='pending',
        path=file_path
    )
    
    try:
        # 上传到对象存储并生成预签名URL
        storage_service = StorageService()
        
        # 生成唯一的对象key（使用时间戳+原文件名）
        import time
        timestamp = int(time.time() * 1000)
        original_filename = os.path.basename(file_path)
        filename_without_ext = os.path.splitext(original_filename)[0]
        object_key = f"{filename_without_ext}_{timestamp}{file_ext}"
        
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
        
        # 更新记录状态
        record.preurl = preurl
        record.expire_time = expire_time
        record.status = 'success'
        record.save()
        
        return JsonResponse({
            'success': True,
            'url': preurl,
            'expire_time': expire_time.strftime('%Y-%m-%d %H:%M:%S'),
            'remaining_time': record.get_remaining_time(),
            'record_id': record.id,
            'tts_type': tts_type,
            'object_key': object_key,
            'message': '✅ 音频上传成功'
        })
        
    except Exception as e:
        record.status = 'failed'
        record.error_message = str(e)
        record.save()
        return JsonResponse({
            'success': False,
            'error': f'处理失败: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def api_upload_video(request):
    """
    API: 直接上传本地视频文件到云端
    
    功能：
    - 上传指定路径的本地视频文件到对象存储（web-video桶）
    - 生成预签名URL
    - 保存记录到数据库
    
    POST参数（JSON格式）:
        file_path: 本地视频文件路径（必需）
        expire_time: 有效期秒数（可选，默认3600）
        title: 视频标题（可选，默认使用文件名）
        
    返回:
        {
            "success": true,
            "url": "预签名URL",
            "expire_time": "过期时间",
            "record_id": 1,
            "message": "上传成功"
        }
    """
    # 解析JSON参数
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': '无效的JSON格式'
            }, status=400)
    else:
        data = request.POST
    
    file_path = data.get('file_path', '').strip()
    expire_seconds = int(data.get('expire_time', 3600))
    title = data.get('title', '').strip()
    
    # 验证参数
    if not file_path:
        return JsonResponse({
            'success': False,
            'error': '文件路径不能为空'
        }, status=400)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return JsonResponse({
            'success': False,
            'error': f'文件不存在: {file_path}'
        }, status=404)
    
    # 检查是否是视频文件
    allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in allowed_extensions:
        return JsonResponse({
            'success': False,
            'error': f'不支持的视频格式: {file_ext}。支持的格式: {", ".join(allowed_extensions)}'
        }, status=400)
    
    # 获取文件信息
    original_filename = os.path.basename(file_path)
    filename_without_ext = os.path.splitext(original_filename)[0]
    file_size = os.path.getsize(file_path)
    
    # 如果没有提供标题，使用文件名
    if not title:
        title = filename_without_ext
    
    # 创建数据库记录
    record = VideoRecord.objects.create(
        title=title,
        path=file_path,
        file_size=file_size,
        status='pending'
    )
    
    try:
        # 使用视频专用bucket上传
        from django.conf import settings as django_settings
        video_bucket = getattr(django_settings, 'TOS_VIDEO_BUCKET_NAME', 'web-video')
        storage_service = StorageService(bucket_name=video_bucket)
        
        # 生成唯一的对象key
        import time
        import uuid
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]
        object_key = f"video_{unique_id}_{timestamp}{file_ext}"
        
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
        
        # 更新记录状态
        record.preurl = preurl
        record.object_key = object_key
        record.expire_time = expire_time
        record.status = 'success'
        record.save()
        
        return JsonResponse({
            'success': True,
            'url': preurl,
            'expire_time': expire_time.strftime('%Y-%m-%d %H:%M:%S'),
            'remaining_time': record.get_remaining_time(),
            'record_id': record.id,
            'object_key': object_key,
            'title': title,
            'file_size': file_size,
            'bucket': video_bucket,
            'message': '✅ 视频上传成功'
        })
        
    except Exception as e:
        record.status = 'failed'
        record.error_message = str(e)
        record.save()
        return JsonResponse({
            'success': False,
            'error': f'处理失败: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def api_upload_video_file(request):
    """
    API: 通过表单上传视频文件、字幕和标题
    
    支持 multipart/form-data 格式上传
    
    POST参数（form-data格式）:
        video_file: 视频文件（必需）
        subtitle_file: 字幕文件（可选，支持 .srt, .vtt, .ass, .ssa）
        title: 视频标题（可选，默认使用文件名）
        expire_time: URL有效期秒数（可选，默认3600）
        
    返回:
        {
            "success": true,
            "url": "视频预签名URL",
            "thumbnail_url": "缩略图URL",
            "subtitle_url": "字幕URL",
            "expire_time": "过期时间",
            "record_id": 1,
            "title": "视频标题",
            "file_size": 12345678,
            "message": "上传成功"
        }
        
    示例 (curl):
        curl -X POST http://localhost:8000/api/upload-video-file/ \\
            -F "video_file=@/path/to/video.mp4" \\
            -F "subtitle_file=@/path/to/subtitle.srt" \\
            -F "title=我的视频" \\
            -F "expire_time=7200"
            
    示例 (Python requests):
        import requests
        
        files = {
            'video_file': open('video.mp4', 'rb'),
            'subtitle_file': open('subtitle.srt', 'rb')  # 可选
        }
        data = {
            'title': '我的视频',
            'expire_time': 7200
        }
        response = requests.post(
            'http://localhost:8000/api/upload-video-file/',
            files=files,
            data=data
        )
        print(response.json())
    """
    import time
    import uuid
    import tempfile
    
    # 检查是否有上传的视频文件
    if 'video_file' not in request.FILES:
        return JsonResponse({
            'success': False,
            'error': '请上传视频文件 (video_file)'
        }, status=400)
    
    # 获取参数
    title = request.POST.get('title', '').strip()
    expire_seconds = int(request.POST.get('expire_time', 3600))
    
    # 处理视频文件
    uploaded_file = request.FILES['video_file']
    original_filename = uploaded_file.name
    file_ext = os.path.splitext(original_filename)[1].lower()
    filename_without_ext = os.path.splitext(original_filename)[0]
    
    # 检查视频格式
    allowed_video_ext = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
    if file_ext not in allowed_video_ext:
        return JsonResponse({
            'success': False,
            'error': f'不支持的视频格式: {file_ext}。支持: {", ".join(allowed_video_ext)}'
        }, status=400)
    
    # 如果没有提供标题，使用文件名
    if not title:
        title = filename_without_ext
    
    # 保存视频到临时文件
    temp_dir = tempfile.gettempdir()
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:8]
    temp_video_path = os.path.join(temp_dir, f"api_upload_{unique_id}_{timestamp}{file_ext}")
    
    try:
        # 写入视频临时文件
        with open(temp_video_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        file_size = os.path.getsize(temp_video_path)
        
        # 创建数据库记录
        record = VideoRecord.objects.create(
            title=title,
            path=temp_video_path,
            file_size=file_size,
            status='pending'
        )
        
        # 使用视频专用bucket上传
        from django.conf import settings as django_settings
        video_bucket = getattr(django_settings, 'TOS_VIDEO_BUCKET_NAME', 'web-video')
        storage_service = StorageService(bucket_name=video_bucket)
        
        # 上传视频
        object_key = f"video_{unique_id}_{timestamp}{file_ext}"
        success, preurl, expire_time, error_msg = storage_service.upload_and_get_url(
            temp_video_path,
            object_key=object_key,
            expires=expire_seconds
        )
        
        if not success:
            record.status = 'failed'
            record.error_message = f'视频上传失败: {error_msg}'
            record.save()
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
            return JsonResponse({
                'success': False,
                'error': f'视频上传失败: {error_msg}'
            }, status=500)
        
        # 生成缩略图
        thumbnail_url = None
        thumbnail_key = None
        try:
            from .services.thumbnail_service import ThumbnailService
            thumb_service = ThumbnailService()
            thumb_success, thumb_path, _ = thumb_service.generate_thumbnail(temp_video_path)
            
            if thumb_success and thumb_path:
                thumbnail_key = f"thumb_{unique_id}_{timestamp}.jpg"
                thumb_ok, thumb_preurl, _, _ = storage_service.upload_and_get_url(
                    thumb_path, object_key=thumbnail_key, expires=expire_seconds
                )
                if thumb_ok:
                    thumbnail_url = thumb_preurl
                if os.path.exists(thumb_path):
                    os.remove(thumb_path)
        except Exception as e:
            print(f"缩略图生成失败: {e}")
        
        # 处理字幕文件
        subtitle_url = None
        subtitle_key = None
        subtitle_name = None
        if 'subtitle_file' in request.FILES:
            subtitle_file = request.FILES['subtitle_file']
            subtitle_name = subtitle_file.name
            subtitle_ext = os.path.splitext(subtitle_name)[1].lower()
            
            allowed_subtitle_ext = ['.srt', '.vtt', '.ass', '.ssa']
            if subtitle_ext in allowed_subtitle_ext:
                try:
                    temp_subtitle_path = os.path.join(temp_dir, f"sub_{unique_id}_{timestamp}{subtitle_ext}")
                    with open(temp_subtitle_path, 'wb+') as f:
                        for chunk in subtitle_file.chunks():
                            f.write(chunk)
                    
                    subtitle_key = f"sub_{unique_id}_{timestamp}{subtitle_ext}"
                    sub_ok, sub_preurl, _, _ = storage_service.upload_and_get_url(
                        temp_subtitle_path, object_key=subtitle_key, expires=expire_seconds
                    )
                    if sub_ok:
                        subtitle_url = sub_preurl
                    if os.path.exists(temp_subtitle_path):
                        os.remove(temp_subtitle_path)
                except Exception as e:
                    print(f"字幕上传失败: {e}")
            else:
                # 不支持的字幕格式，但不阻止视频上传
                print(f"不支持的字幕格式: {subtitle_ext}")
        
        # 更新记录
        record.preurl = preurl
        record.object_key = object_key
        record.thumbnail_url = thumbnail_url
        record.thumbnail_key = thumbnail_key
        record.subtitle_url = subtitle_url
        record.subtitle_key = subtitle_key
        record.subtitle_name = subtitle_name
        record.expire_time = expire_time
        record.status = 'success'
        record.save()
        
        # 清理视频临时文件
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        
        return JsonResponse({
            'success': True,
            'url': preurl,
            'thumbnail_url': thumbnail_url,
            'subtitle_url': subtitle_url,
            'expire_time': expire_time.strftime('%Y-%m-%d %H:%M:%S'),
            'remaining_time': record.get_remaining_time(),
            'record_id': record.id,
            'title': title,
            'file_size': file_size,
            'object_key': object_key,
            'subtitle_name': subtitle_name,
            'bucket': video_bucket,
            'message': '✅ 视频上传成功'
        })
        
    except Exception as e:
        if 'record' in locals():
            record.status = 'failed'
            record.error_message = str(e)
            record.save()
        if 'temp_video_path' in locals() and os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        return JsonResponse({
            'success': False,
            'error': f'处理失败: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def api_renew_video_url(request, record_id):
    """
    API: 续期视频预签名URL
    
    POST参数（JSON格式）:
        expire_time: 新的有效期秒数（可选，默认3600）
        
    返回:
        {
            "success": true,
            "url": "新的预签名URL",
            "expire_time": "新的过期时间",
            "message": "续期成功"
        }
    """
    try:
        record = VideoRecord.objects.get(id=record_id)
    except VideoRecord.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '记录不存在'
        }, status=404)
    
    # 只有成功的记录才能续期
    if record.status != 'success':
        return JsonResponse({
            'success': False,
            'error': '只有成功上传的记录才能续期'
        }, status=400)
    
    # 检查object_key
    if not record.object_key:
        return JsonResponse({
            'success': False,
            'error': '缺少对象存储Key，无法续期'
        }, status=400)
    
    # 解析参数
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}
    else:
        data = request.POST
    
    expire_seconds = int(data.get('expire_time', 3600))
    
    try:
        # 使用视频专用bucket
        from django.conf import settings as django_settings
        video_bucket = getattr(django_settings, 'TOS_VIDEO_BUCKET_NAME', 'web-video')
        storage_service = StorageService(bucket_name=video_bucket)
        
        # 生成新的预签名URL
        success, preurl, expire_time, error_msg = storage_service.generate_presigned_url(
            object_key=record.object_key,
            expires=expire_seconds
        )
        
        if success:
            # 更新记录
            record.preurl = preurl
            record.expire_time = expire_time
            record.save()
            
            return JsonResponse({
                'success': True,
                'url': preurl,
                'expire_time': expire_time.strftime('%Y-%m-%d %H:%M:%S'),
                'remaining_time': record.get_remaining_time(),
                'record_id': record.id,
                'message': f'✅ URL续期成功！新的有效期至 {expire_time.strftime("%Y-%m-%d %H:%M:%S")}'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'续期失败: {error_msg}'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'续期失败: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def api_video_subtitle(request, record_id):
    """
    API: 获取视频字幕内容（代理接口，解决CORS问题）
    
    返回字幕文件内容，支持直接在 <track> 标签中使用
    可选参数 format=vtt 将SRT转换为VTT格式
    """
    from django.http import HttpResponse
    import requests
    
    try:
        record = VideoRecord.objects.get(id=record_id)
    except VideoRecord.DoesNotExist:
        return HttpResponse("字幕不存在", status=404, content_type="text/plain")
    
    if not record.subtitle_url:
        return HttpResponse("该视频没有字幕", status=404, content_type="text/plain")
    
    # 检查并续期字幕URL
    if record.subtitle_key and (record.is_expired() or not record.subtitle_url):
        try:
            from django.conf import settings as django_settings
            video_bucket = getattr(django_settings, 'TOS_VIDEO_BUCKET_NAME', 'web-video')
            storage_service = StorageService(bucket_name=video_bucket)
            success, sub_url, _, _ = storage_service.generate_presigned_url(
                record.subtitle_key, expires=3600
            )
            if success:
                record.subtitle_url = sub_url
                record.save(update_fields=['subtitle_url'])
        except Exception as e:
            print(f"字幕URL续期失败: {e}")
    
    try:
        # 从云存储获取字幕内容
        response = requests.get(record.subtitle_url, timeout=10)
        if response.status_code != 200:
            return HttpResponse("字幕获取失败", status=502, content_type="text/plain")
        
        # 确保正确解码UTF-8
        response.encoding = 'utf-8'
        subtitle_content = response.text
        
        # 判断是否需要转换为VTT格式
        output_format = request.GET.get('format', '').lower()
        subtitle_ext = os.path.splitext(record.subtitle_name or '')[1].lower()
        
        if output_format == 'vtt' and subtitle_ext == '.srt':
            # SRT转VTT
            subtitle_content = srt_to_vtt(subtitle_content)
            content_type = 'text/vtt; charset=utf-8'
        elif subtitle_ext == '.vtt':
            content_type = 'text/vtt; charset=utf-8'
        else:
            content_type = 'text/plain; charset=utf-8'
        
        response = HttpResponse(subtitle_content, content_type=content_type)
        response['Access-Control-Allow-Origin'] = '*'  # 允许跨域
        return response
        
    except Exception as e:
        return HttpResponse(f"字幕获取失败: {str(e)}", status=500, content_type="text/plain")


def srt_to_vtt(srt_content):
    """将SRT字幕转换为VTT格式"""
    import re
    
    # VTT文件头
    vtt_content = "WEBVTT\n\n"
    
    # 替换时间格式: 00:00:00,000 -> 00:00:00.000
    srt_content = re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})', r'\1.\2', srt_content)
    
    # 移除序号行（纯数字行）
    lines = srt_content.strip().split('\n')
    result_lines = []
    skip_next = False
    
    for i, line in enumerate(lines):
        # 跳过纯数字行（字幕序号）
        if line.strip().isdigit():
            continue
        result_lines.append(line)
    
    vtt_content += '\n'.join(result_lines)
    return vtt_content


@require_http_methods(["GET"])
def api_video_detail(request, record_id):
    """API: 获取视频记录详情（JSON格式）"""
    try:
        record = VideoRecord.objects.get(id=record_id)
        return JsonResponse({
            'success': True,
            'data': record.to_dict()
        })
    except VideoRecord.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '记录不存在'
        }, status=404)


@require_http_methods(["GET"])
def api_video_list(request):
    """API: 获取视频记录列表（JSON格式，支持搜索）"""
    from django.db.models import Q
    
    # 获取参数
    limit = int(request.GET.get('limit', 20))
    search_query = request.GET.get('q', '').strip()
    
    # 基础查询
    records = VideoRecord.objects.all()
    
    # 搜索过滤
    if search_query:
        records = records.filter(
            Q(title__icontains=search_query) |
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


@require_http_methods(["POST", "GET"])
@csrf_exempt
def api_get_video_url(request):
    """
    智能API: 获取视频URL
    
    如果标题已存在且URL有效，直接返回
    如果标题已存在但URL过期，续期后返回
    如果标题不存在，返回错误（视频需要先上传）
    
    POST/GET参数:
        title: 视频标题（必需）
        expire_time: 有效期秒数（可选，默认3600，用于续期）
        
    返回:
        {
            "success": true,
            "url": "预签名URL",
            "expire_time": "过期时间",
            "is_renewed": false,
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
    
    title = data.get('title', '').strip()
    expire_seconds = int(data.get('expire_time', 3600))
    
    # 验证参数
    if not title:
        return JsonResponse({
            'success': False,
            'error': '视频标题不能为空'
        }, status=400)
    
    try:
        # 查找是否已存在相同标题的成功记录
        existing_record = VideoRecord.objects.filter(
            title=title,
            status='success'
        ).order_by('-uptime').first()
        
        if existing_record:
            # 记录已存在
            was_expired = existing_record.is_expired()
            
            if was_expired:
                # URL过期，续期
                from django.conf import settings as django_settings
                video_bucket = getattr(django_settings, 'TOS_VIDEO_BUCKET_NAME', 'web-video')
                storage_service = StorageService(bucket_name=video_bucket)
                
                success, preurl, expire_time, error_msg = storage_service.generate_presigned_url(
                    object_key=existing_record.object_key,
                    expires=expire_seconds
                )
                
                if success:
                    existing_record.preurl = preurl
                    existing_record.expire_time = expire_time
                    existing_record.save()
                else:
                    return JsonResponse({
                        'success': False,
                        'error': f'续期失败: {error_msg}'
                    }, status=500)
            
            # 返回现有记录
            return JsonResponse({
                'success': True,
                'url': existing_record.preurl,
                'expire_time': existing_record.expire_time.strftime('%Y-%m-%d %H:%M:%S'),
                'remaining_time': existing_record.get_remaining_time(),
                'is_renewed': was_expired,
                'record_id': existing_record.id,
                'title': existing_record.title,
                'file_size': existing_record.file_size,
                'created_at': existing_record.uptime.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        else:
            # 记录不存在
            return JsonResponse({
                'success': False,
                'error': f'视频不存在: {title}。请先使用 /api/upload-video/ 上传视频'
            }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'系统错误: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def api_delete_video(request, record_id):
    """API: 删除视频记录"""
    try:
        record = VideoRecord.objects.get(id=record_id)
    except VideoRecord.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '记录不存在'
        }, status=404)
    
    try:
        # 从对象存储删除文件
        if record.object_key:
            from django.conf import settings as django_settings
            video_bucket = getattr(django_settings, 'TOS_VIDEO_BUCKET_NAME', 'web-video')
            storage_service = StorageService(bucket_name=video_bucket)
            storage_service.delete_file(record.object_key)
        
        # 删除数据库记录
        record.delete()
        
        return JsonResponse({
            'success': True,
            'message': '✅ 视频记录已删除'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'删除失败: {str(e)}'
        }, status=500)


# ============================================
# 视频页面视图（非API）
# ============================================

def video_list(request):
    """视频列表页面"""
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    # 获取搜索关键词
    search_query = request.GET.get('q', '').strip()
    
    # 基础查询
    videos = VideoRecord.objects.all()
    
    # 如果有搜索关键词，进行搜索
    if search_query:
        videos = videos.filter(
            Q(title__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    # 按上传时间倒序排列
    videos = videos.order_by('-uptime')
    
    # 分页，每页12条（4x3网格）
    paginator = Paginator(videos, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_count': paginator.count,
    }
    return render(request, 'tts_app/video_list.html', context)


def video_detail(request, record_id):
    """视频详情页面（自动续期过期URL）"""
    video = get_object_or_404(VideoRecord, id=record_id)
    
    # 自动续期：如果URL已过期或即将过期（剩余不足5分钟），自动续期
    auto_renewed = False
    if video.status == 'success' and video.object_key:
        from django.utils import timezone
        from datetime import timedelta
        
        # 检查是否需要续期（过期或剩余不足5分钟）
        needs_renewal = False
        if video.expire_time is None:
            needs_renewal = True
        elif video.is_expired():
            needs_renewal = True
        elif video.expire_time - timezone.now() < timedelta(minutes=5):
            needs_renewal = True
        
        if needs_renewal:
            try:
                from django.conf import settings as django_settings
                video_bucket = getattr(django_settings, 'TOS_VIDEO_BUCKET_NAME', 'web-video')
                storage_service = StorageService(bucket_name=video_bucket)
                
                # 默认续期2小时
                expire_seconds = 7200
                
                # 续期视频URL
                success, preurl, expire_time, _ = storage_service.generate_presigned_url(
                    video.object_key, expires=expire_seconds
                )
                if success:
                    video.preurl = preurl
                    video.expire_time = expire_time
                    auto_renewed = True
                
                # 续期缩略图URL
                if video.thumbnail_key:
                    _, thumb_url, _, _ = storage_service.generate_presigned_url(
                        video.thumbnail_key, expires=expire_seconds
                    )
                    if thumb_url:
                        video.thumbnail_url = thumb_url
                
                # 续期字幕URL
                if video.subtitle_key:
                    _, sub_url, _, _ = storage_service.generate_presigned_url(
                        video.subtitle_key, expires=expire_seconds
                    )
                    if sub_url:
                        video.subtitle_url = sub_url
                
                if auto_renewed:
                    video.save()
                    messages.info(request, f'🔄 URL已自动续期，有效期至 {expire_time.strftime("%Y-%m-%d %H:%M:%S")}')
                    
            except Exception as e:
                print(f"自动续期失败: {e}")
    
    context = {
        'video': video,
        'auto_renewed': auto_renewed,
    }
    return render(request, 'tts_app/video_detail.html', context)


@require_http_methods(["POST"])
def video_upload_page(request):
    """视频上传（页面表单提交，支持文件上传）"""
    import time
    import uuid
    import tempfile
    
    title = request.POST.get('title', '').strip()
    expire_seconds = int(request.POST.get('expire_time', 3600))
    
    # 检查是否有上传的文件
    if 'video_file' not in request.FILES:
        messages.error(request, '请选择一个视频文件')
        return redirect('video_list')
    
    uploaded_file = request.FILES['video_file']
    original_filename = uploaded_file.name
    file_ext = os.path.splitext(original_filename)[1].lower()
    filename_without_ext = os.path.splitext(original_filename)[0]
    
    # 检查是否是视频文件
    allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
    if file_ext not in allowed_extensions:
        messages.error(request, f'不支持的视频格式: {file_ext}')
        return redirect('video_list')
    
    # 如果没有提供标题，使用文件名
    if not title:
        title = filename_without_ext
    
    # 保存上传的文件到临时目录
    temp_dir = tempfile.gettempdir()
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:8]
    temp_filename = f"upload_{unique_id}_{timestamp}{file_ext}"
    temp_path = os.path.join(temp_dir, temp_filename)
    
    try:
        # 写入临时文件
        with open(temp_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        file_size = os.path.getsize(temp_path)
        
        # 创建数据库记录
        record = VideoRecord.objects.create(
            title=title,
            path=temp_path,
            file_size=file_size,
            status='pending'
        )
        
        # 使用视频专用bucket上传
        from django.conf import settings as django_settings
        video_bucket = getattr(django_settings, 'TOS_VIDEO_BUCKET_NAME', 'web-video')
        storage_service = StorageService(bucket_name=video_bucket)
        
        # 生成唯一的对象key
        object_key = f"video_{unique_id}_{timestamp}{file_ext}"
        
        success, preurl, expire_time, error_msg = storage_service.upload_and_get_url(
            temp_path,
            object_key=object_key,
            expires=expire_seconds
        )
        
        if not success:
            record.status = 'failed'
            record.error_message = f'上传失败: {error_msg}'
            record.save()
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            messages.error(request, f'上传失败: {error_msg}')
            return redirect('video_list')
        
        # 生成并上传缩略图
        thumbnail_url = None
        thumbnail_key = None
        try:
            from .services.thumbnail_service import ThumbnailService
            thumb_service = ThumbnailService()
            thumb_success, thumb_path, thumb_error = thumb_service.generate_thumbnail(temp_path)
            
            if thumb_success and thumb_path:
                # 上传缩略图到云端
                thumbnail_key = f"thumb_{unique_id}_{timestamp}.jpg"
                thumb_upload_success, thumb_preurl, _, thumb_upload_error = storage_service.upload_and_get_url(
                    thumb_path,
                    object_key=thumbnail_key,
                    expires=expire_seconds
                )
                if thumb_upload_success:
                    thumbnail_url = thumb_preurl
                
                # 清理缩略图临时文件
                if os.path.exists(thumb_path):
                    os.remove(thumb_path)
        except Exception as thumb_e:
            # 缩略图生成失败不影响视频上传
            print(f"缩略图生成失败: {thumb_e}")
        
        # 处理字幕文件上传
        subtitle_url = None
        subtitle_key = None
        subtitle_name = None
        if 'subtitle_file' in request.FILES:
            subtitle_file = request.FILES['subtitle_file']
            subtitle_name = subtitle_file.name
            subtitle_ext = os.path.splitext(subtitle_name)[1].lower()
            
            # 验证字幕格式
            allowed_subtitle_ext = ['.srt', '.vtt', '.ass', '.ssa']
            if subtitle_ext in allowed_subtitle_ext:
                try:
                    # 保存字幕到临时文件
                    subtitle_temp_path = os.path.join(temp_dir, f"sub_{unique_id}_{timestamp}{subtitle_ext}")
                    with open(subtitle_temp_path, 'wb+') as f:
                        for chunk in subtitle_file.chunks():
                            f.write(chunk)
                    
                    # 上传字幕到云端
                    subtitle_key = f"sub_{unique_id}_{timestamp}{subtitle_ext}"
                    sub_success, sub_preurl, _, sub_error = storage_service.upload_and_get_url(
                        subtitle_temp_path,
                        object_key=subtitle_key,
                        expires=expire_seconds
                    )
                    if sub_success:
                        subtitle_url = sub_preurl
                    
                    # 清理临时文件
                    if os.path.exists(subtitle_temp_path):
                        os.remove(subtitle_temp_path)
                except Exception as sub_e:
                    print(f"字幕上传失败: {sub_e}")
        
        # 更新记录状态
        record.preurl = preurl
        record.object_key = object_key
        record.thumbnail_url = thumbnail_url
        record.thumbnail_key = thumbnail_key
        record.subtitle_url = subtitle_url
        record.subtitle_key = subtitle_key
        record.subtitle_name = subtitle_name
        record.expire_time = expire_time
        record.status = 'success'
        record.save()
        
        # 上传成功后清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        messages.success(request, f'✅ 视频 "{title}" 上传成功！')
        return redirect('video_detail', record_id=record.id)
        
    except Exception as e:
        if 'record' in locals():
            record.status = 'failed'
            record.error_message = str(e)
            record.save()
        # 清理临时文件
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        messages.error(request, f'上传失败: {str(e)}')
        return redirect('video_list')


@require_http_methods(["POST"])
def video_renew(request, record_id):
    """视频URL续期（页面表单提交）"""
    video = get_object_or_404(VideoRecord, id=record_id)
    
    # 只有成功的记录才能续期
    if video.status != 'success':
        messages.error(request, '只有成功上传的视频才能续期')
        return redirect('video_detail', record_id=record_id)
    
    # 检查object_key
    if not video.object_key:
        messages.error(request, '缺少对象存储Key，无法续期')
        return redirect('video_detail', record_id=record_id)
    
    expire_seconds = int(request.POST.get('expire_time', 3600))
    
    try:
        from django.conf import settings as django_settings
        video_bucket = getattr(django_settings, 'TOS_VIDEO_BUCKET_NAME', 'web-video')
        storage_service = StorageService(bucket_name=video_bucket)
        
        success, preurl, expire_time, error_msg = storage_service.generate_presigned_url(
            object_key=video.object_key,
            expires=expire_seconds
        )
        
        if success:
            video.preurl = preurl
            video.expire_time = expire_time
            video.save()
            
            messages.success(request, f'✅ URL续期成功！新的有效期至 {expire_time.strftime("%Y-%m-%d %H:%M:%S")}')
        else:
            messages.error(request, f'续期失败: {error_msg}')
            
    except Exception as e:
        messages.error(request, f'续期失败: {str(e)}')
    
    return redirect('video_detail', record_id=record_id)


@require_http_methods(["POST"])
def video_delete(request, record_id):
    """删除视频（页面表单提交）"""
    video = get_object_or_404(VideoRecord, id=record_id)
    
    try:
        # 从对象存储删除文件
        if video.object_key:
            from django.conf import settings as django_settings
            video_bucket = getattr(django_settings, 'TOS_VIDEO_BUCKET_NAME', 'web-video')
            storage_service = StorageService(bucket_name=video_bucket)
            storage_service.delete_file(video.object_key)
        
        # 删除数据库记录
        video.delete()
        
        messages.success(request, '✅ 视频已删除')
    except Exception as e:
        messages.error(request, f'删除失败: {str(e)}')
    
    return redirect('video_list')

