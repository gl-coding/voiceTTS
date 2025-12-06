"""
视频缩略图生成服务

使用 FFmpeg 从视频中提取帧作为缩略图
"""
import os
import subprocess
import tempfile


class ThumbnailService:
    """视频缩略图生成服务"""
    
    def __init__(self):
        self.default_time = "00:00:01"  # 默认从1秒处截取
        self.default_width = 480        # 默认缩略图宽度，高度按比例自动计算
    
    def generate_thumbnail(self, video_path, output_path=None, time_position=None, width=None):
        """
        从视频生成缩略图（保持原始宽高比）
        
        Args:
            video_path: 视频文件路径
            output_path: 缩略图输出路径（可选，不提供则自动生成）
            time_position: 截取时间点，格式 "HH:MM:SS" 或秒数（可选）
            width: 缩略图宽度（可选），高度自动按比例计算
            
        Returns:
            tuple: (success, thumbnail_path, error_msg)
        """
        # 检查视频文件
        if not os.path.exists(video_path):
            return False, None, f"视频文件不存在: {video_path}"
        
        # 设置参数
        time_pos = time_position or self.default_time
        thumb_width = width or self.default_width
        
        # 生成输出路径
        if output_path is None:
            temp_dir = tempfile.gettempdir()
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(temp_dir, f"{base_name}_thumb.jpg")
        
        try:
            # 使用 FFmpeg 生成缩略图
            # -ss: 跳转到指定时间
            # -i: 输入文件
            # -vframes 1: 只提取1帧
            # -vf scale=width:-1: 按宽度缩放，高度自动保持比例（-1表示自动）
            # -y: 覆盖输出文件
            cmd = [
                'ffmpeg',
                '-ss', str(time_pos),
                '-i', video_path,
                '-vframes', '1',
                '-vf', f'scale={thumb_width}:-1',
                '-q:v', '2',  # 高质量JPEG
                '-y',
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # 30秒超时
            )
            
            if result.returncode != 0:
                # FFmpeg 错误
                error_msg = result.stderr[:500] if result.stderr else "未知错误"
                return False, None, f"FFmpeg 错误: {error_msg}"
            
            # 检查输出文件
            if not os.path.exists(output_path):
                return False, None, "缩略图生成失败：输出文件不存在"
            
            return True, output_path, None
            
        except subprocess.TimeoutExpired:
            return False, None, "缩略图生成超时"
        except FileNotFoundError:
            return False, None, "未找到 FFmpeg，请确保已安装 FFmpeg"
        except Exception as e:
            return False, None, f"生成缩略图失败: {str(e)}"
    
    def check_ffmpeg_installed(self):
        """检查 FFmpeg 是否已安装"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

