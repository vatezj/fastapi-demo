#!/bin/bash

# 使用 UV 运行 FastAPI 项目的脚本

echo "🚀 使用 UV 启动 FastAPI 项目..."

# 检查是否安装了 uv
if ! command -v uv &> /dev/null; then
    echo "❌ 错误: 未找到 uv 命令"
    echo "请先安装 uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 检查项目配置
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 错误: 未找到 pyproject.toml 文件"
    exit 1
fi

# 同步依赖（如果需要）
echo "📦 检查依赖..."
uv sync

# 运行项目
echo "🌟 启动 FastAPI 应用..."
uv run python app.py --env=dev

echo "✅ 项目已启动！" 