#!/usr/bin/env python3
"""
从 articles 分支拉取文章并整理到本地目录
使用 git checkout 方式而不是 git clone
"""

import os
import shutil
import tempfile
import subprocess
from pathlib import Path
import sys

def fetch_and_organize_articles(articles_branch="articles", target_dir="docs/articles"):
    """
    从 articles 分支拉取文章并整理到目标目录

    Args:
        articles_branch: 文章分支名称
        target_dir: 目标目录路径
    """

    # 获取当前仓库的根目录
    repo_root = Path.cwd()

    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="articles_fetch_")
    print(f"创建临时目录: {temp_dir}")

    try:
        # 1. 在临时目录中初始化新仓库并拉取所有分支
        print(f"正在设置临时仓库...")
        subprocess.run(['git', 'init'], cwd=temp_dir, check=True, capture_output=True)

        # 添加远程仓库（当前仓库）
        origin_url = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            cwd=repo_root,
            capture_output=True,
            text=True
        ).stdout.strip()

        if not origin_url:
            # 如果是本地仓库，使用文件路径
            origin_url = str(repo_root.absolute())

        subprocess.run(['git', 'remote', 'add', 'origin', origin_url],
                      cwd=temp_dir, check=True, capture_output=True)

        # 拉取所有分支
        print(f"正在拉取所有分支...")
        subprocess.run(['git', 'fetch', 'origin', '--depth=1'],
                      cwd=temp_dir, check=True, capture_output=True)

        # 2. 切换到 articles 分支
        print(f"正在切换到 {articles_branch} 分支...")
        subprocess.run(['git', 'checkout', f'origin/{articles_branch}'],
                      cwd=temp_dir, check=True, capture_output=True)

        # 3. 准备目标目录
        target_path = Path(target_dir)
        if target_path.exists():
            shutil.rmtree(target_path)
        target_path.mkdir(parents=True, exist_ok=True)

        # 4. 处理文件和文件夹
        processed_files = organize_articles_from_source(temp_dir, target_path)

        print(f"✓ 成功处理 {len(processed_files)} 个文章文件")
        print(f"✓ 文章已整理到: {target_dir}")

        return processed_files

    except subprocess.CalledProcessError as e:
        print(f"✗ Git 操作失败:")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        raise
    except Exception as e:
        print(f"✗ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"清理临时目录: {temp_dir}")

def organize_articles_from_source(source_dir, target_dir):
    """
    从源目录整理文章到目标目录

    Args:
        source_dir: 源目录路径
        target_dir: 目标目录路径

    Returns:
        list: 处理过的文件信息
    """

    source_path = Path(source_dir)
    target_path = Path(target_dir)

    processed_files = []

    print(f"扫描源目录: {source_path}")

    # 扫描根目录下的文件
    root_md_files = []
    group_dirs = []

    for item in source_path.iterdir():
        if item.name.startswith('.'):
            continue  # 忽略隐藏文件

        if item.is_file() and item.suffix.lower() == '.md':
            root_md_files.append(item)
        elif item.is_dir():
            group_dirs.append(item)

    # 处理根目录下的 .md 文件（未分类）
    if root_md_files:
        uncategorized_dir = target_path / "uncategorized"
        uncategorized_dir.mkdir(exist_ok=True)

        for md_file in root_md_files:
            dest_file = uncategorized_dir / md_file.name
            shutil.copy2(md_file, dest_file)
            processed_files.append({
                'path': str(dest_file.relative_to(target_path.parent)),
                'group': 'uncategorized',
                'filename': md_file.name
            })
            print(f"  → 根目录文件: {md_file.name} -> uncategorized/")

    # 处理分组目录
    for group_dir in group_dirs:
        group_name = group_dir.name

        # 创建分组目录
        target_group_dir = target_path / group_name
        target_group_dir.mkdir(exist_ok=True)

        # 收集该目录下的所有 .md 文件
        md_files = []
        for item in group_dir.rglob("*"):
            if item.is_file() and item.suffix.lower() == '.md':
                # 如果是子目录中的文件，计算相对路径
                if item.parent != group_dir:
                    # 创建在目标目录中的路径
                    rel_path = item.relative_to(group_dir)
                    dest_file = target_group_dir / rel_path.name

                    # 确保目标目录存在
                    dest_file.parent.mkdir(parents=True, exist_ok=True)

                    shutil.copy2(item, dest_file)
                    processed_files.append({
                        'path': str(dest_file.relative_to(target_path.parent)),
                        'group': group_name,
                        'filename': rel_path.name,
                        'original_path': str(rel_path)
                    })
                    print(f"  → 子目录文件: {group_name}/{rel_path} -> {group_name}/{rel_path.name}")
                else:
                    md_files.append(item)

        # 处理根目录下的 .md 文件
        for md_file in md_files:
            dest_file = target_group_dir / md_file.name
            shutil.copy2(md_file, dest_file)
            processed_files.append({
                'path': str(dest_file.relative_to(target_path.parent)),
                'group': group_name,
                'filename': md_file.name
            })
            print(f"  → 分组文件: {group_name}/{md_file.name}")

    return processed_files

def get_article_groups_from_temp(source_dir):
    """
    从临时目录获取文章分组信息

    Args:
        source_dir: 源目录路径

    Returns:
        dict: 分组信息
    """
    source_path = Path(source_dir)
    groups = {}

    # 先检查根目录下的文件（未分类）
    root_files = [f.name for f in source_path.iterdir()
                  if f.is_file() and f.suffix.lower() == '.md']

    if root_files:
        groups['uncategorized'] = {
            'name': '未分类',
            'display_name': '未分类',
            'count': len(root_files),
            'files': root_files
        }

    # 检查分组目录
    for item in source_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            group_name = item.name

            # 收集该目录下的所有 .md 文件（包括子目录中的）
            md_files = []
            for md_file in item.rglob("*.md"):
                if md_file.suffix.lower() == '.md':
                    if md_file.parent != item:
                        # 子目录中的文件，只取文件名
                        md_files.append(md_file.name)
                    else:
                        md_files.append(md_file.name)

            if md_files:
                groups[group_name] = {
                    'name': group_name,
                    'display_name': group_name,
                    'count': len(md_files),
                    'files': md_files
                }

    return groups

def main():
    """命令行入口"""
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = "docs/articles"

    print("开始从 articles 分支拉取并整理文章...")
    print("=" * 50)

    try:
        files = fetch_and_organize_articles(target_dir=target_dir)

        print("\n" + "=" * 50)
        print(f"处理完成！共处理 {len(files)} 个文件")
        print("=" * 50)

        # 显示分组统计
        groups = {}
        for f in files:
            group = f['group']
            if group not in groups:
                groups[group] = 0
            groups[group] += 1

        print("\n分组统计:")
        for group, count in sorted(groups.items()):
            print(f"  {group}: {count} 篇")

    except Exception as e:
        print(f"\n✗ 处理失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()