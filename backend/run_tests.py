#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
用于运行所有模块的单元测试
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_path: str = None, verbose: bool = False, coverage: bool = False):
    """
    运行测试
    
    Args:
        test_path: 测试路径，如果为None则运行所有测试
        verbose: 是否显示详细输出
        coverage: 是否生成覆盖率报告
    """
    # 获取项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 构建pytest命令
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend([
            "--cov=module_app",
            "--cov=module_admin", 
            "--cov=shared",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
    
    # 添加测试路径
    if test_path:
        cmd.append(test_path)
    else:
        cmd.append("tests/")
    
    # 添加pytest配置
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])
    
    print(f"运行测试命令: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        # 运行测试
        result = subprocess.run(cmd, check=True, capture_output=False)
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print(f"❌ 测试失败，退出码: {e.returncode}")
        return False


def run_specific_test(test_file: str, verbose: bool = False):
    """
    运行特定的测试文件
    
    Args:
        test_file: 测试文件名
        verbose: 是否显示详细输出
    """
    test_path = f"tests/{test_file}"
    if not os.path.exists(test_path):
        print(f"❌ 测试文件不存在: {test_path}")
        return False
    
    print(f"运行特定测试: {test_file}")
    return run_tests(test_path, verbose)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="运行项目测试")
    parser.add_argument(
        "--test-file", "-f",
        help="运行特定的测试文件"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出"
    )
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="生成覆盖率报告"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="运行所有测试"
    )
    
    args = parser.parse_args()
    
    if args.test_file:
        # 运行特定测试文件
        success = run_specific_test(args.test_file, args.verbose)
    elif args.all:
        # 运行所有测试
        success = run_tests(verbose=args.verbose, coverage=args.coverage)
    else:
        # 默认运行所有测试
        success = run_tests(verbose=args.verbose, coverage=args.coverage)
    
    if success:
        print("\n🎉 测试完成！")
        sys.exit(0)
    else:
        print("\n💥 测试失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
