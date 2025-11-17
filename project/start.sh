#!/bin/bash

echo "================================"
echo "英文语音生成系统 - 启动脚本"
echo "================================"

# 检查Python版本
echo "检查Python版本..."
python --version

# 检查是否安装了依赖
echo ""
echo "检查依赖..."
if ! python -c "import django" 2>/dev/null; then
    echo "Django未安装，正在安装依赖..."
    pip install -r requirements.txt
else
    echo "依赖已安装 ✓"
fi

# 检查环境变量
echo ""
echo "检查环境变量..."
if [ -z "$TOS_ACCESS_KEY" ] || [ -z "$TOS_SECRET_KEY" ]; then
    echo "⚠️  警告: TOS环境变量未设置"
    echo "请设置以下环境变量："
    echo "  export TOS_ACCESS_KEY='你的密钥'"
    echo "  export TOS_SECRET_KEY='你的密钥'"
    echo ""
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "环境变量已设置 ✓"
fi

# 初始化数据库
echo ""
echo "初始化数据库..."
python manage.py makemigrations
python manage.py migrate

# 创建媒体目录
echo ""
echo "创建媒体目录..."
mkdir -p media/audio

# 启动服务器
echo ""
echo "================================"
echo "启动开发服务器..."
echo "访问: http://127.0.0.1:8000"
echo "按 Ctrl+C 停止服务器"
echo "================================"
echo ""

python manage.py runserver

