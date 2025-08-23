#!/usr/bin/env python3
"""
项目环境检查脚本
验证 UV 环境和依赖是否正确安装
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """检查 Python 版本"""
    print("🐍 检查 Python 版本...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - 版本符合要求")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - 需要 Python 3.9+")
        return False

def check_uv_installation():
    """检查 UV 是否安装"""
    print("\n📦 检查 UV 安装...")
    try:
        result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ UV 已安装: {result.stdout.strip()}")
            return True
        else:
            print("❌ UV 未正确安装")
            return False
    except FileNotFoundError:
        print("❌ UV 未安装，请运行: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False

def check_project_files():
    """检查项目文件"""
    print("\n📁 检查项目文件...")
    required_files = [
        'pyproject.toml',
        'uv.lock',
        'app.py',
        '.venv'
    ]
    
    all_exist = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"✅ {file} - 存在")
        else:
            print(f"❌ {file} - 不存在")
            all_exist = False
    
    return all_exist

def check_dependencies():
    """检查关键依赖"""
    print("\n🔍 检查关键依赖...")
    
    dependencies = [
        'fastapi',
        'sqlalchemy', 
        'redis',
        'loguru',
        'pydantic'
    ]
    
    all_imported = True
    for dep in dependencies:
        try:
            importlib.import_module(dep)
            print(f"✅ {dep} - 已安装")
        except ImportError:
            print(f"❌ {dep} - 未安装")
            all_imported = False
    
    return all_imported

def check_virtual_env():
    """检查虚拟环境"""
    print("\n🔧 检查虚拟环境...")
    
    # 检查是否在虚拟环境中
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 运行在虚拟环境中")
        print(f"📍 Python 路径: {sys.executable}")
        return True
    else:
        print("⚠️  未在虚拟环境中运行")
        print("💡 建议使用: uv run python check_setup.py")
        return False

def main():
    """主检查函数"""
    print("🚀 FastAPI 项目环境检查\n")
    
    checks = [
        ("Python 版本", check_python_version()),
        ("UV 安装", check_uv_installation()),
        ("项目文件", check_project_files()),
        ("依赖安装", check_dependencies()),
        ("虚拟环境", check_virtual_env())
    ]
    
    print("\n" + "="*50)
    print("📊 检查结果汇总:")
    print("="*50)
    
    passed = 0
    for name, result in checks:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:<12} : {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(checks)} 项检查通过")
    
    if passed == len(checks):
        print("\n🎉 环境配置完美！可以开始开发了！")
        print("\n💡 下一步:")
        print("   - 运行应用: uv run python app.py")
        print("   - 查看文档: http://localhost:8000/docs")
    else:
        print("\n⚠️  存在一些问题，请检查上述失败项")
        print("\n💡 常见解决方案:")
        print("   - 安装 UV: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("   - 安装依赖: uv sync")
        print("   - 使用 UV 运行: uv run python check_setup.py")

if __name__ == "__main__":
    main() 