#!/usr/bin/env python3
"""
从 articles 分支拉取文章并整理到本地目录
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

    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="articles_")
    print(f"创建临时目录: {temp_dir}")

    try:
        # 1. 克隆 articles 分支到临时目录
        print(f"正在拉取 {articles_branch} 分支...")
        subprocess.run([
            'git', 'clone',
            '--branch', articles_branch,
            '--depth', '1',
            '--single-branch',
            '.',  # 当前仓库
            temp_dir
        ], check=True, capture_output=True, text=True)

        # 2. 准备目标目录
        target_path = Path(target_dir)
        if target_path.exists():
            shutil.rmtree(target_path)
        target_path.mkdir(parents=True, exist_ok=True)

        # 3. 处理文件和文件夹
        processed_files = organize_articles_from_source(temp_dir, target_path)

        print(f"✓ 成功处理 {len(processed_files)} 个文章文件")
        print(f"✓ 文章已整理到: {target_dir}")

        return processed_files

    except subprocess.CalledProcessError as e:
        print(f"✗ Git 操作失败: {e.stderr}")
        raise
    except Exception as e:
        print(f"✗ 处理失败: {e}")
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
    """

    source_path = Path(source_dir)
    target_path = Path(target_dir)

    processed_files = []

    # 扫描源目录
    for item in source_path.iterdir():
        if item.name.startswith('.'):
            continue  # 忽略隐藏文件

        if item.is_file() and item.suffix == '.md':
            # 根目录下的 .md 文件 -> 放到 uncategorized 分组
            dest_dir = target_path / "uncategorized"
            dest_dir.mkdir(exist_ok=True)

            dest_file = dest_dir / item.name
            shutil.copy2(item, dest_file)
            processed_files.append({
                'path': str(dest_file.relative_to(target_path.parent)),
                'group': 'uncategorized',
                'filename': item.name
            })
            print(f"  → 根目录文件: {item.name} -> uncategorized/")

        elif item.is_dir():
            # 目录 -> 作为分组
            group_name = item.name

            # 检查是否只包含文件（不允许分组嵌套）
            has_subdirs = any(subitem.is_dir() for subitem in item.iterdir())
            if has_subdirs:
                print(f"⚠  警告: 分组 '{group_name}' 包含子目录，将被忽略")
                continue

            # 创建分组目录
            group_dir = target_path / group_name
            group_dir.mkdir(exist_ok=True)

            # 复制该目录下的所有 .md 文件
            md_count = 0
            for subitem in item.iterdir():
                if subitem.is_file() and subitem.suffix == '.md':
                    dest_file = group_dir / subitem.name
                    shutil.copy2(subitem, dest_file)
                    processed_files.append({
                        'path': str(dest_file.relative_to(target_path.parent)),
                        'group': group_name,
                        'filename': subitem.name
                    })
                    md_count += 1

            if md_count > 0:
                print(f"  → 分组: {group_name} ({md_count} 篇文章)")
            else:
                # 如果分组下没有文章，删除空目录
                group_dir.rmdir()

    return processed_files

def get_article_groups(source_dir):
    """
    获取文章分组信息

    Args:
        source_dir: 源目录路径

    Returns:
        dict: 分组信息
    """
    source_path = Path(source_dir)
    groups = {}

    # 先检查根目录下的文件（未分类）
    root_files = [f.name for f in source_path.iterdir()
                  if f.is_file() and f.suffix == '.md']

    if root_files:
        groups['uncategorized'] = {
            'name': '未分类',
            'count': len(root_files),
            'files': root_files
        }

    # 检查分组目录
    for item in source_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            # 检查是否只包含文件（不允许分组嵌套）
            has_subdirs = any(subitem.is_dir() for subitem in item.iterdir())
            if has_subdirs:
                continue

            md_files = [f.name for f in item.iterdir()
                       if f.is_file() and f.suffix == '.md']

            if md_files:
                groups[item.name] = {
                    'name': item.name,
                    'count': len(md_files),
                    'files': md_files
                }

    return groups