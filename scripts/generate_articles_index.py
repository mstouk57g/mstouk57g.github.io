#!/usr/bin/env python3
"""
自动生成 articles 目录下文章的索引 JSON 文件
"""

import os
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path


def get_git_info(file_path):
    """获取文件的 Git 信息"""
    try:
        # 获取最后修改信息（作者、时间）
        last_commit_cmd = [
            'git', 'log', '-1', '--pretty=format:%H|%an|%ad',
            '--date=iso', '--follow', '--', file_path
        ]
        last_commit = subprocess.check_output(last_commit_cmd, text=True).strip()

        # 获取首次提交信息（创建时间）
        first_commit_cmd = [
            'git', 'log', '--reverse', '--pretty=format:%H|%ad',
            '--date=iso', '--follow', '--', file_path
        ]
        first_commit_output = subprocess.check_output(first_commit_cmd, text=True).strip()

        # 获取提交总数
        count_cmd = ['git', 'log', '--oneline', '--follow', '--', file_path]
        commit_count = len(subprocess.check_output(count_cmd, text=True).strip().split('\n'))

        if last_commit:
            last_commit_parts = last_commit.split('|')
            last_hash = last_commit_parts[0]
            last_author = last_commit_parts[1] if len(last_commit_parts) > 1 else 'mstouk57g'
            last_date = last_commit_parts[2] if len(last_commit_parts) > 2 else datetime.now().isoformat()
        else:
            last_hash = ''
            last_author = 'mstouk57g'
            last_date = datetime.now().isoformat()

        # 获取创建时间（第一次提交的时间）
        if first_commit_output:
            first_commit_lines = first_commit_output.split('\n')
            if first_commit_lines:
                first_commit = first_commit_lines[0].split('|')
                created_date = first_commit[1] if len(first_commit) > 1 else last_date
            else:
                created_date = last_date
        else:
            created_date = last_date

        return {
            'author': last_author,
            'lastModified': last_date,
            'created': created_date,
            'commitCount': commit_count if commit_count > 0 else 1,
            'lastCommitHash': last_hash
        }

    except subprocess.CalledProcessError as e:
        print(f"警告: 无法获取 {file_path} 的 Git 信息: {e}")
        return {
            'author': 'mstouk57g',
            'lastModified': datetime.now().isoformat(),
            'created': datetime.now().isoformat(),
            'commitCount': 1,
            'lastCommitHash': ''
        }


def extract_title_and_description(content, filename):
    """从 Markdown 内容中提取标题和描述"""
    lines = content.split('\n')

    # 提取标题（查找第一个 # 标题）
    title = Path(filename).stem  # 默认使用文件名（不带扩展名）
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            break
        elif line.startswith('## '):
            title = line[3:].strip()
            break

    # 提取描述（第一个非空、非标题、非图片、非链接的段落）
    description = ''
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#') or line.startswith('![') or line.startswith('['):
            continue
        if re.match(r'^[-*_]{3,}$', line):  # 跳过分隔线
            continue

        # 清理 Markdown 格式
        clean_line = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', line)  # 移除链接
        clean_line = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_line)  # 移除加粗
        clean_line = re.sub(r'\*([^*]+)\*', r'\1', clean_line)      # 移除斜体
        clean_line = re.sub(r'`([^`]+)`', r'\1', clean_line)        # 移除代码

        description = clean_line[:150]
        if len(clean_line) > 150:
            description += '...'
        break

    return title, description


def count_words(content):
    """计算文章字数"""
    # 移除 Markdown 语法和特殊字符
    clean_content = re.sub(r'[#*`\-_\[\]\(\)!]', ' ', content)
    clean_content = re.sub(r'\s+', ' ', clean_content)

    # 分割单词并计数
    words = clean_content.strip().split()
    return len(words)


def generate_articles_index():
    """生成文章索引"""
    articles_dir = Path('./docs/articles')
    output_file = Path('./articles-list.json')
    scripts_dir = Path('./scripts')

    # 确保 scripts 目录存在
    scripts_dir.mkdir(parents=True, exist_ok=True)

    # 确保 articles 目录存在
    if not articles_dir.exists() or not articles_dir.is_dir():
        print('articles 目录不存在，创建空索引')
        output_file.write_text('[]')
        return []

    # 获取所有 .md 文件
    articles = []
    md_files = list(articles_dir.glob('*.md'))

    print(f"找到 {len(md_files)} 个 Markdown 文件")

    for md_file in md_files:
        try:
            # 读取文件内容
            content = md_file.read_text(encoding='utf-8')

            # 提取标题和描述
            title, description = extract_title_and_description(content, md_file.name)

            # 获取 Git 信息
            git_info = get_git_info(str(md_file))

            # 计算字数
            word_count = count_words(content)

            article_info = {
                'filename': md_file.name,
                'title': title,
                'description': description,
                'author': git_info['author'],
                'lastModified': git_info['lastModified'],
                'created': git_info['created'],
                'commitCount': git_info['commitCount'],
                'wordCount': word_count,
                'lastCommitHash': git_info['lastCommitHash']
            }

            articles.append(article_info)
            print(f"已处理: {md_file.name}")

        except Exception as e:
            print(f"处理文件 {md_file.name} 时出错: {e}")

    # 按最后修改时间倒序排序
    articles.sort(key=lambda x: x['lastModified'], reverse=True)

    # 写入 JSON 文件
    with output_file.open('w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"成功生成了 {len(articles)} 篇文章的索引")
    return articles

def generate_articles_index_with_groups(articles_dir="./docs/articles"):
    """生成带分组的文章索引"""
    articles_path = Path(articles_dir)

    if not articles_path.exists():
        return {"articles": [], "groups": {}}

    all_articles = []
    groups_info = {}

    # 遍历所有分组目录
    for group_dir in articles_path.iterdir():
        if group_dir.is_dir():
            group_name = group_dir.name
            group_articles = []

            # 处理该分组下的所有文章
            for md_file in group_dir.glob("*.md"):
                try:
                    content = md_file.read_text(encoding='utf-8')

                    # 提取标题和描述
                    title, description = extract_title_and_description(content, md_file.name)

                    # 获取 Git 信息
                    git_info = get_git_info(str(md_file))

                    # 计算字数
                    word_count = count_words(content)

                    article_info = {
                        'filename': md_file.name,
                        'title': title,
                        'description': description,
                        'author': git_info['author'],
                        'lastModified': git_info['lastModified'],
                        'created': git_info['created'],
                        'commitCount': git_info['commitCount'],
                        'wordCount': word_count,
                        'lastCommitHash': git_info['lastCommitHash'],
                        'group': group_name,
                        'path': f"articles/{group_name}/{md_file.name}"
                    }

                    group_articles.append(article_info)
                    all_articles.append(article_info)

                except Exception as e:
                    print(f"处理文件 {md_file.name} 时出错: {e}")

            # 添加到分组信息
            if group_articles:
                groups_info[group_name] = {
                    'name': group_name,
                    'count': len(group_articles),
                    'articles': [{
                        'filename': a['filename'],
                        'title': a['title']
                    } for a in group_articles]
                }

    # 按最后修改时间倒序排序
    all_articles.sort(key=lambda x: x['lastModified'], reverse=True)

    # 生成完整索引
    result = {
        'articles': all_articles,
        'groups': groups_info,
        'total': len(all_articles),
        'groupCount': len(groups_info),
        'generatedAt': datetime.now().isoformat()
    }

    # 保存到根目录
    output_file = Path("./articles-list.json")
    with output_file.open('w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"成功生成了 {len(all_articles)} 篇文章的索引，共 {len(groups_info)} 个分组")
    return result