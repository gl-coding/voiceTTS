"""
TTS应用URL路由
"""
from django.urls import path
from . import views

urlpatterns = [
    # 音频页面路由
    path('', views.index, name='index'),
    path('generate/', views.generate_tts, name='generate_tts'),
    path('result/<int:record_id>/', views.result, name='result'),
    path('records/', views.record_list, name='record_list'),
    path('record/<int:record_id>/', views.record_detail, name='record_detail'),
    path('record/<int:record_id>/renew/', views.renew_url, name='renew_url'),
    path('record/<int:record_id>/delete/', views.delete_record, name='delete_record'),
    
    # 视频页面路由
    path('videos/', views.video_list, name='video_list'),
    path('video/<int:record_id>/', views.video_detail, name='video_detail'),
    path('video/upload/', views.video_upload_page, name='video_upload_page'),
    path('video/<int:record_id>/renew/', views.video_renew, name='video_renew'),
    path('video/<int:record_id>/delete/', views.video_delete, name='video_delete'),
    
    # 音频API路由
    path('api/get-audio-url/', views.api_get_audio_url, name='api_get_audio_url'),
    path('api/upload-audio/', views.api_upload_audio, name='api_upload_audio'),
    path('api/record/<int:record_id>/', views.api_record_detail, name='api_record_detail'),
    path('api/records/', views.api_record_list, name='api_record_list'),
    
    # 视频API路由
    path('api/upload-video/', views.api_upload_video, name='api_upload_video'),
    path('api/upload-video-file/', views.api_upload_video_file, name='api_upload_video_file'),  # 文件上传
    path('api/get-video-url/', views.api_get_video_url, name='api_get_video_url'),
    path('api/video/<int:record_id>/', views.api_video_detail, name='api_video_detail'),
    path('api/video/<int:record_id>/subtitle/', views.api_video_subtitle, name='api_video_subtitle'),  # 字幕代理
    path('api/video/<int:record_id>/renew/', views.api_renew_video_url, name='api_renew_video_url'),
    path('api/video/<int:record_id>/delete/', views.api_delete_video, name='api_delete_video'),
    path('api/videos/', views.api_video_list, name='api_video_list'),
]

