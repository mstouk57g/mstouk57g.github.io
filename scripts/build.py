#!/usr/bin/env python3
"""
基于模板的构建脚本 - 修正版
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
import sys
import json
import tempfile
from datetime import datetime
import markdown
from jinja2 import Environment, FileSystemLoader

def init_jinja():
    """初始化Jinja2模板引擎"""
    templates_dir = Path("templates")
    if not templates_dir.exists():
        # 创建模板目录
        templates_dir.mkdir(exist_ok=True)
        print("⚠ 创建模板目录: templates/")

    env = Environment(
        loader=FileSystemLoader(templates_dir),
        trim_blocks=True,
        lstrip_blocks=True
    )
    return env

def get_git_info(file_path):
    """获取Git信息"""
    try:
        # 最后修改时间
        cmd = ['git', 'log', '-1', '--format=%cd', '--date=short', '--', str(file_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        last_modified = result.stdout.strip() if result.returncode == 0 else datetime.now().strftime('%Y-%m-%d')

        # 提交次数
        cmd = ['git', 'log', '--oneline', '--', str(file_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        commit_count = len([line for line in result.stdout.strip().split('\n') if line])

        return {
            'lastModified': last_modified,
            'commitCount': max(commit_count, 1),
            'author': 'mstouk57g'
        }
    except:
        return {
            'lastModified': datetime.now().strftime('%Y-%m-%d'),
            'commitCount': 1,
            'author': 'mstouk57g'
        }

def extract_article_info(md_content, filename, group_name):
    """提取文章信息"""
    lines = md_content.strip().split('\n')

    # 提取标题
    title = Path(filename).stem
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            break

    # 提取描述
    description = ''
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#') or line.startswith('!['):
            continue
        if re.match(r'^[-*_]{3,}$', line):
            continue

        clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', line)
        clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean)
        clean = re.sub(r'\*([^*]+)\*', r'\1', clean)
        clean = re.sub(r'`([^`]+)`', r'\1', clean)

        description = clean[:150]
        if len(clean) > 150:
            description += '...'
        break

    # 计算字数
    clean_content = md_content.replace('#', '').replace('*', '').replace('`', '').strip()
    word_count = len(clean_content.split())

    return {
        'filename': filename,
        'html_name': f"{Path(filename).stem}.html",
        'title': title,
        'description': description or title,
        'word_count': word_count,
        'reading_time': max(1, word_count // 300),
        'group': group_name
    }

def convert_markdown_to_html(content):
    """转换Markdown为HTML"""
    md_extensions = [
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.toc'
    ]
    return markdown.markdown(content, extensions=md_extensions)

def fetch_articles():
    """从Git拉取文章"""
    temp_dir = tempfile.mkdtemp(prefix="articles_")

    try:
        # 获取远程URL
        cmd = ['git', 'config', '--get', 'remote.origin.url']
        result = subprocess.run(cmd, capture_output=True, text=True)
        repo_url = result.stdout.strip() if result.returncode == 0 else "."

        # 克隆articles分支
        print("📥 从Git拉取文章...")
        cmd = ['git', 'clone', '-b', 'articles', '--depth', '1', repo_url, temp_dir]
        subprocess.run(cmd, check=True)

        all_articles = []
        articles_by_group = {}

        temp_path = Path(temp_dir)

        # 处理默认分组（根目录）
        for md_file in temp_path.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            info = extract_article_info(content, md_file.name, "default")

            git_info = get_git_info(md_file)
            info.update(git_info)
            info['date'] = git_info['lastModified']
            info['commit_count'] = git_info['commitCount']
            info['author'] = git_info['author']

            all_articles.append(info)
            if "default" not in articles_by_group:
                articles_by_group["default"] = []
            articles_by_group["default"].append(info)

        # 处理分组目录
        for item in temp_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                group_name = item.name
                for md_file in item.glob("*.md"):
                    content = md_file.read_text(encoding='utf-8')
                    info = extract_article_info(content, md_file.name, group_name)

                    git_info = get_git_info(md_file)
                    info.update(git_info)
                    info['date'] = git_info['lastModified']
                    info['commit_count'] = git_info['commitCount']
                    info['author'] = git_info['author']

                    all_articles.append(info)
                    if group_name not in articles_by_group:
                        articles_by_group[group_name] = []
                    articles_by_group[group_name].append(info)

        # 按时间排序
        for group in articles_by_group.values():
            group.sort(key=lambda x: x['date'], reverse=True)
        all_articles.sort(key=lambda x: x['date'], reverse=True)

        # 保存原始文件
        temp_save = Path("temp_articles")
        if temp_save.exists():
            shutil.rmtree(temp_save)
        shutil.copytree(temp_dir, temp_save)

        shutil.rmtree(temp_dir)

        print(f"✓ 拉取完成: {len(all_articles)} 篇文章，{len(articles_by_group)} 个分组")
        return all_articles, articles_by_group

    except Exception as e:
        print(f"✗ 拉取失败: {e}")
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
        return [], {}

def generate_all_groups_page(env, groups_info, build_dir):
    """生成所有分组页面"""
    template = env.get_template("all_groups.html")

    # 计算统计数据
    total_articles = sum(info['count'] for info in groups_info.values())
    total_words = sum(info['total_words'] for info in groups_info.values())
    total_reading_time = sum(info['total_reading_time'] for info in groups_info.values())

    # 获取最近更新的文章（前5篇）
    all_articles = []
    for group_name, info in groups_info.items():
        all_articles.extend(info['articles'])
    all_articles.sort(key=lambda x: x['date'], reverse=True)
    recent_articles = all_articles[:5]

    context = {
        'title': '所有分组',
        'groups': groups_info,
        'total_articles': total_articles,
        'total_words': total_words,
        'total_reading_time': total_reading_time,
        'recent_articles': recent_articles,
        'current_year': datetime.now().year,
        'build_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    content = template.render(**context)

    groups_dir = build_dir / "articles" / "groups"
    groups_dir.mkdir(parents=True, exist_ok=True)

    (groups_dir / "index.html").write_text(content, encoding='utf-8')
    print("✓ 生成: /articles/groups/index.html")

def generate_all_articles_page(env, all_articles, groups_info, build_dir):
    """生成所有文章页面"""
    template = env.get_template("all_articles.html")

    # 计算统计数据
    total_words = sum(a['word_count'] for a in all_articles)
    total_reading_time = sum(a['reading_time'] for a in all_articles)

    context = {
        'title': '所有文章',
        'all_articles': all_articles,
        'groups_info': groups_info,
        'total_articles': len(all_articles),
        'total_words': total_words,
        'total_reading_time': total_reading_time,
        'group_count': len(groups_info),
        'current_year': datetime.now().year,
        'build_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    content = template.render(**context)

    articles_dir = build_dir / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)

    (articles_dir / "index.html").write_text(content, encoding='utf-8')
    print("✓ 生成: /articles/index.html")

def build_with_templates():
    """使用模板构建站点"""
    print("🚀 开始模板构建...")
    print("=" * 50)

    # 初始化
    env = init_jinja()
    build_dir = Path("site/_site")

    # 清理
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)

    # 1. 拉取文章
    all_articles, articles_by_group = fetch_articles()

    if not all_articles:
        print("⚠ 没有文章，构建失败")
        return False

    # 2. 复制静态文件
    print("\n📋 复制静态文件...")
    source_dir = Path("site")
    for item in source_dir.iterdir():
        if item.name in ['_site', 'articles']:
            continue
        if item.is_file():
            shutil.copy2(item, build_dir / item.name)
        elif item.is_dir():
            shutil.copytree(item, build_dir / item.name, dirs_exist_ok=True)

    # 3. 准备分组信息
    groups_info = {}
    for group_name, articles in articles_by_group.items():
        total_words = sum(a['word_count'] for a in articles)
        total_reading_time = sum(a['reading_time'] for a in articles)
        latest_date = max((a['date'] for a in articles), default='')

        groups_info[group_name] = {
            'count': len(articles),
            'total_words': total_words,
            'total_reading_time': total_reading_time,
            'latest_date': latest_date,
            'articles': articles,
            'description': f"{group_name} 分类的文章"
        }

    # 4. 生成所有分组页面
    print("\n📁 生成所有分组页面...")
    generate_all_groups_page(env, groups_info, build_dir)

    # 5. 生成每个分组页面
    print("\n📂 生成分组页面...")
    temp_articles_dir = Path("temp_articles")

    # 6. 生成所有文章页面
    print("\n📄 生成所有文章页面...")
    generate_all_articles_page(env, all_articles, groups_info, build_dir)

    for group_name, articles in articles_by_group.items():
        # 分组首页
        total_words = sum(a['word_count'] for a in articles)
        total_reading_time = sum(a['reading_time'] for a in articles)
        latest_date = max((a['date'] for a in articles), default='')

        template = env.get_template("group_index.html")
        context = {
            'title': f'{group_name} - 文章分类' if group_name != 'default' else '默认分组 - 文章分类',
            'group_name': group_name,
            'current_group': group_name,
            'articles': articles,
            'total_words': total_words,
            'total_reading_time': total_reading_time,
            'latest_date': latest_date,
            'current_year': datetime.now().year,
            'build_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        group_dir = build_dir / "articles" / "groups" / group_name
        group_dir.mkdir(parents=True, exist_ok=True)

        (group_dir / "index.html").write_text(template.render(**context), encoding='utf-8')
        print(f"✓ 生成: /articles/groups/{group_name}/")

        # 分组内的文章
        for i, article in enumerate(articles):
            # 读取Markdown内容
            md_file = temp_articles_dir / article['group'] / article['filename']
            if not md_file.exists():
                md_file = temp_articles_dir / "default" / article['filename']

            if md_file.exists():
                md_content = md_file.read_text(encoding='utf-8')
                html_content = convert_markdown_to_html(md_content)
                article['content'] = html_content

                # 获取相邻文章
                prev_article = articles[i-1] if i > 0 else None
                next_article = articles[i+1] if i < len(articles)-1 else None

                # 生成文章页面
                template = env.get_template("article_detail.html")
                context = {
                    'title': article['title'],
                    'article': article,
                    'prev_article': prev_article,
                    'next_article': next_article,
                    'current_year': datetime.now().year,
                    'build_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                article_file = group_dir / article['html_name']
                article_file.write_text(template.render(**context), encoding='utf-8')
                print(f"  → 生成: /articles/groups/{group_name}/{article['html_name']}")

    # 6. 清理
    if temp_articles_dir.exists():
        shutil.rmtree(temp_articles_dir)

    # 7. 创建.nojekyll
    (build_dir / ".nojekyll").touch()

    # 8. 复制配置文件到网站根目录
    root_files = ["CNAME", "config.json"]
    for filename in root_files:
        file_path = Path(filename)
        if file_path.exists():
            shutil.copy2(file_path, build_dir / filename)
            print(f"✓ 复制: {filename} -> {build_dir}/{filename}")
        else:
            print(f"⚠ {filename} 文件不存在")

    print("\n" + "=" * 50)
    print("🎉 模板构建完成!")
    print(f"📊 统计:")
    print(f"  文章总数: {len(all_articles)}")
    print(f"  分组数量: {len(articles_by_group)}")
    print(f"  输出目录: {build_dir}")
    print("=" * 50)
    return True

def main():
    try:
        return build_with_templates()
    except Exception as e:
        print(f"\n❌ 构建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)