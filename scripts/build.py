#!/usr/bin/env python3
"""
主构建脚本：拉取文章、生成索引、构建完整站点
"""

import os
import json
import shutil
import subprocess
from pathlib import Path
import sys

# 添加脚本目录到路径
sys.path.append(os.path.dirname(__file__))
from fetch_articles import fetch_and_organize_articles
from generate_articles_index import generate_articles_index_with_groups

def clean_build_dir(build_dir="docs/_site"):
    """清理构建目录"""
    build_path = Path(build_dir)
    if build_path.exists():
        shutil.rmtree(build_path)
    build_path.mkdir(parents=True, exist_ok=True)
    print(f"✓ 清理构建目录: {build_dir}")

def copy_frontend_files(source_dir="docs", target_dir="docs/_site"):
    """复制前端文件到构建目录"""
    source_path = Path(source_dir)
    target_path = Path(target_dir)

    # 复制所有文件，除了 articles 目录（会重新生成）
    for item in source_path.iterdir():
        if item.name in ['articles', '_site']:
            continue  # 跳过 articles 目录和构建目录本身

        if item.is_file():
            shutil.copy2(item, target_path / item.name)
        elif item.is_dir():
            shutil.copytree(item, target_path / item.name,
                          dirs_exist_ok=True)

    print(f"✓ 复制前端文件到构建目录")

def create_nojekyll_file(build_dir="docs/_site"):
    """创建 .nojekyll 文件"""
    nojekyll_path = Path(build_dir) / ".nojekyll"
    nojekyll_path.touch()
    print(f"✓ 创建 .nojekyll 文件")

def main():
    print("=" * 50)
    print("开始构建站点")
    print("=" * 50)

    # 配置
    BUILD_DIR = "docs/_site"
    ARTICLES_DIR = "docs/articles"

    try:
        # 1. 清理构建目录
        clean_build_dir(BUILD_DIR)

        # 2. 从 articles 分支拉取并整理文章
        print("\n1. 拉取并整理文章...")
        processed_files = fetch_and_organize_articles(
            articles_branch="articles",
            target_dir=ARTICLES_DIR
        )

        # 3. 生成带分组的文章索引
        print("\n2. 生成文章索引...")
        articles_index = generate_articles_index_with_groups(ARTICLES_DIR)

        # 4. 复制前端文件
        print("\n3. 复制前端文件...")
        copy_frontend_files(target_dir=BUILD_DIR)

        # 5. 复制文章目录到构建目录
        articles_src = Path(ARTICLES_DIR)
        articles_dst = Path(BUILD_DIR) / "articles"
        if articles_src.exists():
            shutil.copytree(articles_src, articles_dst, dirs_exist_ok=True)
            print(f"✓ 复制文章到构建目录")

        # 6. 保存文章索引到构建目录
        index_file = Path(BUILD_DIR) / "articles-list.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(articles_index, f, ensure_ascii=False, indent=2)
        print(f"✓ 保存文章索引: {index_file}")

        # 7. 创建 .nojekyll 文件
        create_nojekyll_file(BUILD_DIR)

        # 8. 生成分组信息
        print("\n4. 生成分组信息...")
        groups_info = generate_groups_info(ARTICLES_DIR)
        groups_file = Path(BUILD_DIR) / "groups-list.json"
        with open(groups_file, 'w', encoding='utf-8') as f:
            json.dump(groups_info, f, ensure_ascii=False, indent=2)
        print(f"✓ 保存分组信息: {groups_file}")

        print("\n" + "=" * 50)
        print("构建完成!")
        print(f"输出目录: {BUILD_DIR}")
        print(f"文章总数: {len(articles_index)}")
        print(f"分组数量: {len(groups_info)}")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"\n✗ 构建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_groups_info(articles_dir):
    """生成分组信息"""
    groups = {}

    articles_path = Path(articles_dir)

    for group_dir in articles_path.iterdir():
        if group_dir.is_dir():
            group_name = group_dir.name
            md_files = list(group_dir.glob("*.md"))

            if md_files:
                groups[group_name] = {
                    'name': group_name,
                    'path': f"articles/{group_name}",
                    'count': len(md_files),
                    'articles': [
                        {
                            'filename': f.name,
                            'path': f"articles/{group_name}/{f.name}"
                        }
                        for f in md_files
                    ]
                }

    return groups

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)