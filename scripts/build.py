#!/usr/bin/env python3
"""
构建网站
"""

import os
import re
import shutil
import requests
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
        templates_dir.mkdir(exist_ok=True)
        print("⚠ 创建模板目录: templates/")
    for subdir in ["home", "articles"]:
        subdir_path = templates_dir / subdir
        if not subdir_path.exists():
            subdir_path.mkdir(exist_ok=True)
            print(f"⚠ 创建模板子目录: templates/{subdir}/")

    env = Environment(
        loader=FileSystemLoader([
            str(templates_dir / "home"),
            str(templates_dir / "articles")
        ]),
        trim_blocks=True,
        lstrip_blocks=True
    )
    return env

def get_git_info(file_path):
    """获取Git信息"""
    try:
        # 第一次提交的作者（原作者）
        cmd = ['git', 'log', '--reverse', '--format=%an', '--', str(file_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        first_author_line = result.stdout.strip().split('\n')[0] if result.returncode == 0 and result.stdout.strip() else None
        author_name = first_author_line if first_author_line else None

        # 第一次提交的邮箱
        cmd = ['git', 'log', '--reverse', '--format=%ae', '--', str(file_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        first_email_line = result.stdout.strip().split('\n')[0] if result.returncode == 0 and result.stdout.strip() else None
        author_email = first_email_line if first_email_line else None

        # 最后一次修改时间
        cmd = ['git', 'log', '-1', '--format=%cd', '--date=short', '--', str(file_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        last_modified = result.stdout.strip() if result.returncode == 0 else datetime.now().strftime('%Y-%m-%d')

        # 提交次数
        cmd = ['git', 'log', '--oneline', '--', str(file_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        commit_count = len([line for line in result.stdout.strip().split('\n') if line])

        # 获取作者头像URL
        avatar_url = ''
        if author_name:
            avatar_url = f"https://avatars.githubusercontent.com/{author_name}"

        return {
            'lastModified': last_modified,
            'commitCount': commit_count,
            'author': author_name or 'Unknown',
            'author_email': author_email,
            'avatar_url': avatar_url
        }
    except Exception as e:
        print(f"⚠ 获取Git信息失败: {e}")
        return {
            'lastModified': datetime.now().strftime('%Y-%m-%d'),
            'commitCount': 1,
            'author': 'Unknown',
            'author_email': None,
            'avatar_url': ''
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
        'group': group_name,
        'avatar_url': '',
        'author_email': ''
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
            info['avatar_url'] = git_info.get('avatar_url', '')
            info['author_email'] = git_info.get('author_email', '')

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
                    info['avatar_url'] = git_info.get('avatar_url', '')
                    info['author_email'] = git_info.get('author_email', '')

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

        # 将根目录的.md文件移动到default文件夹
        default_dir = temp_save / "default"
        default_dir.mkdir(exist_ok=True)

        # 移动根目录的.md文件到default文件夹
        for md_file in temp_save.glob("*.md"):
            if md_file.is_file():
                target_path = default_dir / md_file.name
                shutil.move(str(md_file), str(target_path))
                print(f"📁 移动文件: {md_file.name} -> default/")

        shutil.rmtree(temp_dir)

        print(f"✓ 拉取完成: {len(all_articles)} 篇文章，{len(articles_by_group)} 个分组")
        return all_articles, articles_by_group

    except Exception as e:
        print(f"✗ 拉取失败: {e}")
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
        return [], {}

def generate_home_page(env, config, build_dir):
    """生成主页"""
    try:
        template = env.get_template("index.html")

        context = {
            'site': config['site'],
            'buttons': config['buttons'],
            'socialLinks': config['socialLinks'],
            'background': config['background'],
            'styles': config['styles'],
            'title': config['site']['title'],
            'current_year': datetime.now().year,
            'build_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        content = template.render(**context)
        (build_dir / "index.html").write_text(content, encoding='utf-8')
        print("✓ 生成: /index.html")
        return True

    except Exception as e:
        print(f"✗ 生成主页失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_all_groups_page(env, groups_info, build_dir):
    """生成所有分组页面"""
    try:
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
        return True

    except Exception as e:
        print(f"✗ 生成所有分组页面失败: {e}")
        return False

def generate_all_articles_page(env, all_articles, groups_info, build_dir):
    """生成所有文章页面"""
    try:
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
        return True

    except Exception as e:
        print(f"✗ 生成所有文章页面失败: {e}")
        return False

def generate_group_pages(env, articles_by_group, build_dir):
    """生成分组页面"""
    temp_articles_dir = Path("temp_articles")

    for group_name, articles in articles_by_group.items():
        try:
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

            # 分组内的文章详情页
            generate_article_pages(env, articles, group_name, group_dir, temp_articles_dir)

        except Exception as e:
            print(f"✗ 生成分组 '{group_name}' 页面失败: {e}")

def generate_article_pages(env, articles, group_name, group_dir, temp_articles_dir):
    """生成文章详情页面"""
    for i, article in enumerate(articles):
        try:
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

        except Exception as e:
            print(f"✗ 生成文章 '{article['title']}' 页面失败: {e}")

def copy_static_files(build_dir):
    """复制静态文件"""
    source_dir = Path("site")

    # 要复制的文件列表
    static_files = [
        ("style.css", "CSS样式文件"),
        ("404.html", "404页面"),
        ("favicon.ico", "网站图标")
    ]

    for filename, description in static_files:
        file_path = source_dir / filename
        if file_path.exists():
            try:
                shutil.copy2(file_path, build_dir / filename)
                print(f"✓ 复制: {filename} ({description})")
            except Exception as e:
                print(f"⚠ 复制 {filename} 失败: {e}")
        else:
            print(f"⚠ {filename} 不存在，跳过复制")


def build_with_templates():
    """使用模板构建站点"""
    print("🚀 开始模板构建...")
    print("=" * 50)

    # 初始化模板环境
    env = init_jinja()
    build_dir = Path("site/_site")

    # 清理构建目录
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)

    # 1. 读取配置文件
    print("📄 读取配置文件...")
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        print("✓ 配置文件读取成功")
    except Exception as e:
        print(f"✗ 读取配置文件失败: {e}")
        return False

    # 更新config配置信息（从GitHub API）
    print("\n🌐 从GitHub API获取用户信息...")
    try:
        username = config['site']['username']
        api_url = f"https://api.github.com/users/{username}"

        # 使用 requests 调用 GitHub API
        response = requests.get(api_url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/vnd.github.v3+json'
        }, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # 更新配置
            if data.get('name'):
                config['site']['name'] = data['name']
                print(f"✓ 更新 name: {data['name']}")

            if data.get('bio'):
                config['site']['subtitle'] = data['bio']
                print(f"✓ 更新 subtitle: {data['bio'][:50]}...")

        else:
            print(f"⚠ GitHub API 返回状态码: {response.status_code}")
    except Exception as e:
        print(f"⚠ 从GitHub API获取信息失败: {e}")
        print("⚠ 使用配置文件中的原始信息")

    # 2. 生成主页
    print("\n🏠 生成主页...")
    if not generate_home_page(env, config, build_dir):
        print("⚠ 主页生成失败，继续构建其他页面")

    # 3. 拉取文章
    print("\n📥 拉取文章...")
    all_articles, articles_by_group = fetch_articles()

    if all_articles:
        print(f"✓ 拉取完成: {len(all_articles)} 篇文章，{len(articles_by_group)} 个分组")

        # 4. 准备分组信息
        print("\n📊 准备分组信息...")
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

        # 5. 生成所有分组页面
        print("\n📁 生成所有分组页面...")
        generate_all_groups_page(env, groups_info, build_dir)

        # 6. 生成所有文章页面
        print("\n📄 生成所有文章页面...")
        generate_all_articles_page(env, all_articles, groups_info, build_dir)

        # 7. 生成分组页面
        print("\n📂 生成分组页面...")
        generate_group_pages(env, articles_by_group, build_dir)
    else:
        print("⚠ 没有文章可构建，跳过文章相关页面")

    # 8. 复制静态文件
    print("\n📋 复制静态文件...")
    copy_static_files(build_dir)

    # 9. 创建.nojekyll
    (build_dir / ".nojekyll").touch()
    print("✓ 创建: .nojekyll")

    # 10. 清理临时文件
    print("\n🧹 清理临时文件...")
    temp_articles_dir = Path("temp_articles")
    if temp_articles_dir.exists():
        shutil.rmtree(temp_articles_dir)
        print("✓ 清理: temp_articles/")

    print("\n" + "=" * 50)
    print("🎉 模板构建完成!")
    print(f"📊 统计:")
    print(f"  文章总数: {len(all_articles)}")
    print(f"  分组数量: {len(articles_by_group)}")
    print(f"  输出目录: {build_dir}")
    print("=" * 50)
    return True


def main():
    """主函数"""
    try:
        # 检查必要的目录和文件
        if not Path("config.json").exists():
            print("❌ 错误: config.json 不存在")
            return False

        if not Path("templates").exists():
            print("⚠ 警告: templates 目录不存在，尝试创建...")
            Path("templates").mkdir(exist_ok=True)
            Path("templates/home").mkdir(exist_ok=True)
            Path("templates/articles").mkdir(exist_ok=True)
            print("⚠ 请确保模板文件已放置在 templates/home/ 和 templates/articles/ 目录中")

        # 执行构建
        success = build_with_templates()
        return success

    except Exception as e:
        print(f"\n❌ 构建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)