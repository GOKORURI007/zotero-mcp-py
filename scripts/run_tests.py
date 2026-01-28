#!/usr/bin/env python
"""运行测试脚本"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """执行命令并返回是否成功"""
    print(f'\n{"=" * 60}')
    print(f'{description}')
    print(f'{"=" * 60}')

    try:
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f'错误: 命令执行失败 (退出码: {e.returncode})', file=sys.stderr)
        return False
    except FileNotFoundError:
        print(f"错误: 找不到命令 '{cmd[0]}'，请确保已安装 pytest", file=sys.stderr)
        print("提示: 运行 'pip install pytest' 或 'uv add --dev pytest' 安装", file=sys.stderr)
        return False


def main() -> int:
    """主函数"""
    # 切换到项目根目录
    project_root = Path(__file__).parent.parent

    print(f'项目目录: {project_root}')
    print(f'当前Python: {sys.executable}')

    # 构建 pytest 命令
    pytest_args = ['pytest'] + sys.argv[1:]  # 支持传递额外参数

    # 运行测试
    if not run_command(pytest_args, '运行测试'):
        return 1

    print('\n' + '=' * 60)
    print('✅ 测试完成!')
    print('=' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
