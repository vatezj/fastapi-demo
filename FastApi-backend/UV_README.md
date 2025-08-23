# UV 项目管理指南

本项目使用 [uv](https://github.com/astral-sh/uv) 作为 Python 包管理器和项目构建工具。

## 安装 UV

如果您还没有安装 uv，请先安装：

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或者使用 pip
pip install uv
```

## 项目设置

### 1. 安装依赖

```bash
# 安装所有依赖（包括开发依赖）
uv sync

# 只安装生产依赖
uv sync --no-dev

# 安装特定依赖
uv add package_name

# 安装开发依赖
uv add --dev package_name
```

### 2. 激活虚拟环境

```bash
# 激活虚拟环境
source .venv/bin/activate

# 或者使用 uv run（推荐）
uv run python your_script.py
```

## 常用命令

### 依赖管理

```bash
# 添加新依赖
uv add package_name

# 添加开发依赖
uv add --dev package_name

# 移除依赖
uv remove package_name

# 更新依赖
uv sync --upgrade

# 查看依赖树
uv tree
```

### 运行项目

```bash
# 运行 Python 脚本
uv run python app.py

# 运行测试
uv run pytest

# 运行代码格式化
uv run black .
uv run isort .
uv run ruff check .

# 运行类型检查
uv run mypy .
```

### 项目构建

```bash
# 构建项目
uv build

# 发布到 PyPI
uv publish
```

## 项目结构

```
FastApi-backend/
├── pyproject.toml          # 项目配置和依赖
├── uv.lock                 # 依赖锁定文件
├── .venv/                  # 虚拟环境（自动生成）
├── .uv/                    # UV 缓存目录
└── ...                     # 项目源代码
```

## 配置文件说明

### pyproject.toml

- `[project]`: 项目基本信息
- `[project.dependencies]`: 生产依赖
- `[project.optional-dependencies]`: 可选依赖（如开发工具）
- `[tool.uv]`: UV 特定配置
- `[tool.ruff]`: 代码检查工具配置
- `[tool.black]`: 代码格式化工具配置
- `[tool.isort]`: 导入排序工具配置
- `[tool.mypy]`: 类型检查工具配置

## 开发工作流

1. **克隆项目后**：
   ```bash
   uv sync
   ```

2. **添加新依赖**：
   ```bash
   uv add package_name
   ```

3. **运行项目**：
   ```bash
   uv run python app.py
   ```

4. **代码质量检查**：
   ```bash
   uv run black .          # 格式化代码
   uv run isort .          # 排序导入
   uv run ruff check .     # 代码检查
   uv run mypy .           # 类型检查
   ```

5. **运行测试**：
   ```bash
   uv run pytest
   ```

## 优势

- **快速**: 比 pip 快 10-100 倍
- **可靠**: 确定性依赖解析
- **现代**: 支持最新的 Python 打包标准
- **集成**: 内置虚拟环境管理
- **兼容**: 与现有 pip 工作流兼容

## 注意事项

- `uv.lock` 文件应该提交到版本控制
- `.venv/` 和 `.uv/` 目录不应该提交到版本控制
- 使用 `uv run` 而不是直接激活虚拟环境，这样可以确保使用正确的 Python 版本 