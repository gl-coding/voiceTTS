"""
TTS应用URL路由
"""
from django.urls import path
from . import views

urlpatterns = [
    # 页面路由
    path('', views.index, name='index'),
    path('generate/', views.generate_tts, name='generate_tts'),
    path('result/<int:record_id>/', views.result, name='result'),
    path('records/', views.record_list, name='record_list'),
    path('record/<int:record_id>/', views.record_detail, name='record_detail'),
    path('record/<int:record_id>/renew/', views.renew_url, name='renew_url'),
    path('record/<int:record_id>/delete/', views.delete_record, name='delete_record'),
    
    # API路由
    path('api/record/<int:record_id>/', views.api_record_detail, name='api_record_detail'),
    path('api/records/', views.api_record_list, name='api_record_list'),
]

