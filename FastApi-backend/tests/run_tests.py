#!/usr/bin/env python3
"""
测试运行脚本
按功能分类运行测试
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_test_category(category: str):
    """运行指定类别的测试"""
    test_dir = project_root / "tests" / category
    
    if not test_dir.exists():
        print(f"❌ 测试类别 '{category}' 不存在")
        return False
    
    print(f"🚀 运行 {category} 类别的测试...")
    print("=" * 50)
    
    # 获取该类别下的所有测试文件
    test_files = list(test_dir.glob("test_*.py"))
    
    if not test_files:
        print(f"⚠️  {category} 类别下没有找到测试文件")
        return True
    
    success_count = 0
    total_count = len(test_files)
    
    for test_file in test_files:
        print(f"📝 运行测试: {test_file.name}")
        try:
            # 使用 uv 运行测试
            result = subprocess.run(
                ["uv", "run", "python", str(test_file)],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ {test_file.name} 运行成功")
                success_count += 1
            else:
                print(f"❌ {test_file.name} 运行失败")
                if result.stderr:
                    print(f"   错误信息: {result.stderr.strip()}")
                    
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_file.name} 运行超时")
        except Exception as e:
            print(f"💥 {test_file.name} 运行异常: {e}")
    
    print("=" * 50)
    print(f"📊 测试结果: {success_count}/{total_count} 成功")
    
    return success_count == total_count

def list_categories():
    """列出所有可用的测试类别"""
    test_dir = project_root / "tests"
    categories = []
    
    for item in test_dir.iterdir():
        if item.is_dir() and item.name != "__pycache__":
            categories.append(item.name)
    
    return sorted(categories)

def main():
    parser = argparse.ArgumentParser(description="运行项目测试")
    parser.add_argument(
        "category", 
        nargs="?", 
        help="测试类别 (account, auth, database, validation, yozuan, general)"
    )
    parser.add_argument(
        "--list", 
        action="store_true", 
        help="列出所有可用的测试类别"
    )
    parser.add_argument(
        "--all", 
        action="store_true", 
        help="运行所有测试类别"
    )
    
    args = parser.parse_args()
    
    if args.list:
        categories = list_categories()
        print("📁 可用的测试类别:")
        for category in categories:
            print(f"  - {category}")
        return
    
    if args.all:
        categories = list_categories()
        print("🚀 运行所有测试类别...")
        print("=" * 60)
        
        all_success = True
        for category in categories:
            if category != "__pycache__":
                success = run_test_category(category)
                if not success:
                    all_success = False
                print()
        
        print("=" * 60)
        if all_success:
            print("🎉 所有测试类别运行完成！")
        else:
            print("⚠️  部分测试类别运行失败")
        return
    
    if not args.category:
        print("请指定测试类别或使用 --list 查看可用类别")
        print("使用 --help 查看帮助信息")
        return
    
    # 运行指定类别的测试
    success = run_test_category(args.category)
    if success:
        print(f"🎉 {args.category} 类别测试全部通过！")
    else:
        print(f"⚠️  {args.category} 类别测试部分失败")

if __name__ == "__main__":
    main() 