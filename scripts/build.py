#!/usr/bin/env python3
"""
新的主构建脚本：生成静态HTML，不再保留markdown和json
"""

import os
import json
import shutil
import subprocess
from pathlib import Path
import sys
import markdown
from datetime import datetime
import frontmatter
import html

# 添加自定义的CSS样式
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - mstouk57gの小站</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github-dark.min.css">
    <style>
        /* 毛玻璃效果 */
        .glass-card {{
            backdrop-filter: blur(10px);
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        /* Markdown内容样式 */
        .markdown-content {{
            line-height: 1.8;
            font-size: 1.125rem;
        }}
        .markdown-content h1 {{
            font-size: 2.5rem;
            font-weight: 800;
            margin: 2.5rem 0 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid rgba(255, 255, 255, 0.1);
        }}
        .markdown-content h2 {{
            font-size: 2rem;
            font-weight: 700;
            margin: 2rem 0 1rem;
            padding-bottom: 0.25rem;
            border-bottom: 2px solid rgba(255, 255, 255, 0.08);
        }}
        .markdown-content pre {{
            background-color: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 0.75rem;
            padding: 1.25rem;
            overflow-x: auto;
            margin: 1.5rem 0;
        }}
        .markdown-content a {{
            color: #93c5fd;
            text-decoration: none;
            border-bottom: 1px dashed #93c5fd;
            transition: all 0.2s;
        }}
        .markdown-content a:hover {{
            color: #60a5fa;
            border-bottom-style: solid;
        }}
    </style>
</head>
<body class="text-white min-h-screen" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
    <!-- 导航栏 -->
    <nav class="glass-card p-4 mb-8">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <a href="/" class="text-xl font-bold">mstouk57gの小站</a>
            <div class="space-x-4">
                <a href="/articles/" class="hover:text-purple-300">所有文章</a>
                <a href="/" class="hover:text-purple-300">返回首页</a>
            </div>
        </div>
    </nav>

    <!-- 主内容 -->
    <main class="max-w-4xl mx-auto px-4 py-8">
        {content}
    </main>

    <!-- 页脚 -->
    <footer class="mt-16 text-center text-sm opacity-70 py-8">
        <p>© {current_year} ntcho & ConiMite • mstouk57g</p>
        <p class="mt-2 text-xs opacity-50">最后更新于: {build_time}</p>
    </footer>

    <!-- Highlight.js 代码高亮 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', (event) => {{
            document.querySelectorAll('pre code').forEach((el) => {{
                hljs.highlightElement(el);
            }});
        }});
    </script>
</body>
</html>
"""

# 分组首页模板
GROUP_INDEX_TEMPLATE = """
<div class="glass-card rounded-2xl p-8 mb-8">
    <h1 class="text-4xl font-bold mb-4">{group_name} 分类</h1>
    <p class="text-xl opacity-80 mb-8">共 {article_count} 篇文章</p>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        {article_cards}
    </div>
</div>
"""

# 文章卡片模板
ARTICLE_CARD_TEMPLATE = """
<div class="glass-card rounded-xl p-6 hover:scale-[1.02] transition-transform cursor-pointer" onclick="window.location.href='{article_url}'">
    <div class="flex items-center justify-between mb-4">
        <div class="text-2xl text-purple-300">
            <i class="fas fa-file-alt"></i>
        </div>
        <span class="text-xs opacity-70 bg-black bg-opacity-30 px-2 py-1 rounded">
            {date}
        </span>
    </div>

    <h3 class="text-xl font-bold mb-3 line-clamp-2">{title}</h3>
    <p class="text-sm opacity-80 mb-4 line-clamp-3">{description}</p>

    <div class="flex justify-between items-center text-xs">
        <div class="flex items-center">
            <i class="fas fa-user-circle mr-1 opacity-70"></i>
            <span class="opacity-80">{author}</span>
        </div>
        <div class="flex items-center">
            <i class="fas fa-file-word mr-1 opacity-70"></i>
            <span class="opacity-80">{word_count}字</span>
        </div>
    </div>
</div>
"""

# 文章详情页模板
ARTICLE_DETAIL_TEMPLATE = """
<div class="glass-card rounded-2xl p-8 mb-8">
    <!-- 返回按钮 -->
    <div class="mb-8">
        <a href="{group_index_url}" class="inline-flex items-center glass-card px-4 py-2 rounded-lg hover:bg-white hover:bg-opacity-10 transition">
            <i class="fas fa-arrow-left mr-2"></i> 返回{group_name}分类
        </a>
    </div>

    <!-- 文章头部 -->
    <div class="text-center mb-12">
        <div class="inline-block mb-6">
            <span class="text-xs uppercase tracking-wider opacity-70 bg-purple-600 bg-opacity-30 px-3 py-1 rounded-full">
                <i class="far fa-clock mr-1"></i>{date}
            </span>
        </div>
        <h1 class="text-4xl md:text-5xl font-bold mb-6">{title}</h1>
        {description_html}
    </div>

    <!-- 文章内容 -->
    <div class="markdown-content">
        {content}
    </div>

    <!-- 文章元信息 -->
    <div class="glass-card rounded-xl p-6 mt-12">
        <div class="flex flex-col md:flex-row justify-between items-center">
            <div class="mb-4 md:mb-0 text-center md:text-left">
                <div class="flex items-center">
                    <div class="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center mr-3">
                        <i class="fas fa-user text-lg"></i>
                    </div>
                    <div>
                        <div class="font-bold">{author}</div>
                        <div class="text-sm opacity-70">作者</div>
                    </div>
                </div>
            </div>

            <div class="text-center md:text-right">
                <div class="flex items-center">
                    <i class="fas fa-file-word text-xl mr-3 text-purple-300"></i>
                    <div>
                        <div class="font-bold">{word_count} 字</div>
                        <div class="text-sm opacity-70">阅读约需 {reading_time} 分钟</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
"""

def clean_build_dir(build_dir="docs/_site"):
    """清理构建目录"""
    build_path = Path(build_dir)
    if build_path.exists():
        shutil.rmtree(build_path)
    build_path.mkdir(parents=True, exist_ok=True)

    # 创建articles目录结构
    (build_path / "articles").mkdir(parents=True, exist_ok=True)
    (build_path / "articles" / "groups").mkdir(parents=True, exist_ok=True)

    print(f"✓ 清理并创建构建目录: {build_dir}")

def copy_static_files(source_dir="docs", target_dir="docs/_site"):
    """复制静态文件（不包括文章相关文件）"""
    source_path = Path(source_dir)
    target_path = Path(target_dir)

    # 复制必要的文件
    files_to_copy = [
        "index.html", "404.html", "style.css", "script.js",
        "favicon.ico", "CNAME", "config.json"
    ]

    for file_name in files_to_copy:
        file_path = source_path / file_name
        if file_path.exists():
            shutil.copy2(file_path, target_path / file_name)
            print(f"✓ 复制: {file_name}")

def process_markdown_file(md_file, group_name="default"):
    """处理单个Markdown文件，返回文章信息"""
    try:
        # 读取文件内容
        content = md_file.read_text(encoding='utf-8')

        # 解析frontmatter（如果有）
        metadata = {}
        if content.startswith('---'):
            try:
                post = frontmatter.loads(content)
                content = post.content
                metadata = post.metadata
            except:
                pass

        # 提取标题
        title = metadata.get('title', md_file.stem)
        description = metadata.get('description', '')
        author = metadata.get('author', 'mstouk57g')

        # 如果没有frontmatter，从内容中提取
        lines = content.strip().split('\n')
        for line in lines:
            if line.startswith('# ') and not title:
                title = line[2:].strip()
                break

        # 计算字数
        word_count = len(content.replace('#', '').replace('*', '').replace('`', '').strip().split())
        reading_time = max(1, word_count // 300)

        # 获取Git信息
        git_info = get_git_info(md_file)

        # 转换Markdown为HTML
        md_extensions = [
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.tables',
            'markdown.extensions.toc',
            'markdown.extensions.fenced_code'
        ]
        html_content = markdown.markdown(content, extensions=md_extensions)

        return {
            'filename': md_file.name,
            'title': title,
            'description': description,
            'author': author or git_info['author'],
            'content': html_content,
            'word_count': word_count,
            'reading_time': reading_time,
            'last_modified': git_info['lastModified'],
            'group': group_name,
            'html_filename': f"{md_file.stem}.html",
            'date': datetime.fromisoformat(git_info['lastModified'].replace('Z', '+00:00')).strftime('%Y年%m月%d日')
        }

    except Exception as e:
        print(f"✗ 处理文件 {md_file} 失败: {e}")
        return None

def get_git_info(file_path):
    """获取文件的Git信息"""
    try:
        # 简化版Git信息获取
        return {
            'author': 'mstouk57g',
            'lastModified': datetime.now().isoformat(),
        }
    except:
        return {
            'author': 'mstouk57g',
            'lastModified': datetime.now().isoformat(),
        }

def generate_article_html(article_info, build_dir):
    """生成文章详情HTML页面"""
    # 构建文章内容
    description_html = ""
    if article_info['description']:
        description_html = f"""
        <div class="max-w-2xl mx-auto">
            <p class="text-xl opacity-90 italic border-l-4 border-purple-500 pl-4 py-2">
                {article_info['description']}
            </p>
        </div>
        """

    article_content = ARTICLE_DETAIL_TEMPLATE.format(
        group_index_url=f"/articles/groups/{article_info['group']}/",
        group_name=article_info['group'],
        title=article_info['title'],
        description_html=description_html,
        content=article_info['content'],
        author=article_info['author'],
        word_count=article_info['word_count'],
        reading_time=article_info['reading_time'],
        date=article_info['date']
    )

    # 生成完整HTML
    full_html = HTML_TEMPLATE.format(
        title=article_info['title'],
        content=article_content,
        current_year=datetime.now().year,
        build_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    # 保存文件
    group_dir = build_dir / "articles" / "groups" / article_info['group']
    group_dir.mkdir(parents=True, exist_ok=True)

    article_file = group_dir / article_info['html_filename']
    article_file.write_text(full_html, encoding='utf-8')

    return str(article_file.relative_to(build_dir))

def generate_group_index(group_name, articles, build_dir):
    """生成分组首页"""
    if not articles:
        return None

    # 构建文章卡片
    article_cards = []
    for article in articles:
        article_url = f"/articles/groups/{group_name}/{article['html_filename']}"
        article_cards.append(ARTICLE_CARD_TEMPLATE.format(
            article_url=article_url,
            title=article['title'],
            description=article['description'] or article['title'],
            author=article['author'],
            word_count=article['word_count'],
            date=article['date']
        ))

    # 构建分组首页内容
    group_content = GROUP_INDEX_TEMPLATE.format(
        group_name=group_name,
        article_count=len(articles),
        article_cards='\n'.join(article_cards)
    )

    # 生成完整HTML
    full_html = HTML_TEMPLATE.format(
        title=f"{group_name} 分类",
        content=group_content,
        current_year=datetime.now().year,
        build_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    # 保存文件
    group_dir = build_dir / "articles" / "groups" / group_name
    group_dir.mkdir(parents=True, exist_ok=True)

    index_file = group_dir / "index.html"
    index_file.write_text(full_html, encoding='utf-8')

    return str(index_file.relative_to(build_dir))

def generate_main_articles_index(all_articles, build_dir):
    """生成所有文章总览页"""
    # 按分组组织文章
    articles_by_group = {}
    for article in all_articles:
        group = article['group']
        if group not in articles_by_group:
            articles_by_group[group] = []
        articles_by_group[group].append(article)

    # 构建分组区块
    group_sections = []
    for group_name, group_articles in articles_by_group.items():
        # 构建该分组的文章列表
        article_list = []
        for article in group_articles:
            article_url = f"/articles/groups/{group_name}/{article['html_filename']}"
            article_list.append(f"""
            <div class="mb-4">
                <a href="{article_url}" class="flex justify-between items-center p-4 glass-card rounded-lg hover:bg-white hover:bg-opacity-10 transition">
                    <div>
                        <h4 class="font-bold">{article['title']}</h4>
                        <p class="text-sm opacity-70 mt-1">{article['description'] or ''}</p>
                    </div>
                    <div class="text-right">
                        <div class="text-xs opacity-70">{article['date']}</div>
                        <div class="text-xs opacity-50">{article['author']}</div>
                    </div>
                </a>
            </div>
            """)

        group_sections.append(f"""
        <div class="mb-12">
            <div class="flex items-center justify-between mb-6">
                <h2 class="text-2xl font-bold">{group_name} ({len(group_articles)}篇)</h2>
                <a href="/articles/groups/{group_name}/" class="text-purple-300 hover:text-purple-400">
                    查看全部 <i class="fas fa-arrow-right ml-1"></i>
                </a>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                {''.join(article_list[:4])}
            </div>
        </div>
        """)

    # 构建总览页内容
    total_articles = len(all_articles)
    total_groups = len(articles_by_group)

    content = f"""
    <div class="glass-card rounded-2xl p-8 mb-8">
        <h1 class="text-4xl font-bold mb-4">所有文章</h1>
        <div class="flex space-x-6 mb-8 text-center">
            <div>
                <div class="text-3xl font-bold">{total_articles}</div>
                <div class="text-sm opacity-70">文章总数</div>
            </div>
            <div>
                <div class="text-3xl font-bold">{total_groups}</div>
                <div class="text-sm opacity-70">分类数量</div>
            </div>
        </div>

        {''.join(group_sections)}
    </div>
    """

    # 生成完整HTML
    full_html = HTML_TEMPLATE.format(
        title="所有文章",
        content=content,
        current_year=datetime.now().year,
        build_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    # 保存文件
    index_file = build_dir / "articles" / "index.html"
    index_file.write_text(full_html, encoding='utf-8')

    return str(index_file.relative_to(build_dir))

def fetch_articles_from_git(articles_branch="articles"):
    """从Git仓库拉取文章"""
    try:
        # 创建临时目录
        import tempfile
        temp_dir = tempfile.mkdtemp()

        # 克隆文章分支
        repo_url = get_git_remote_url()
        subprocess.run([
            'git', 'clone', '-b', articles_branch,
            '--depth', '1', repo_url, temp_dir
        ], check=True)

        # 扫描文章
        all_articles = []

        temp_path = Path(temp_dir)

        # 先扫描根目录的markdown文件（默认分组）
        for md_file in temp_path.glob("*.md"):
            article = process_markdown_file(md_file, "default")
            if article:
                all_articles.append(article)

        # 扫描子目录作为分组
        for item in temp_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                group_name = item.name
                for md_file in item.glob("*.md"):
                    article = process_markdown_file(md_file, group_name)
                    if article:
                        all_articles.append(article)

        # 清理临时目录
        shutil.rmtree(temp_dir)

        return all_articles

    except Exception as e:
        print(f"✗ 从Git拉取文章失败: {e}")
        return []

def get_git_remote_url():
    """获取Git远程仓库URL"""
    try:
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except:
        return "."

def main():
    print("=" * 50)
    print("开始构建静态HTML站点")
    print("=" * 50)

    try:
        # 配置
        BUILD_DIR = Path("docs/_site")

        # 1. 清理并创建构建目录
        clean_build_dir(BUILD_DIR)

        # 2. 复制静态文件
        copy_static_files(target_dir=BUILD_DIR)

        # 3. 从Git拉取并处理文章
        print("\n1. 从Git拉取文章...")
        all_articles = fetch_articles_from_git("articles")

        if not all_articles:
            print("⚠ 没有找到文章，创建示例文章...")
            # 可以在这里创建示例文章

        print(f"✓ 找到 {len(all_articles)} 篇文章")

        # 4. 按分组组织文章
        articles_by_group = {}
        for article in all_articles:
            group = article['group']
            if group not in articles_by_group:
                articles_by_group[group] = []
            articles_by_group[group].append(article)

        # 5. 生成分组页面和文章页面
        print("\n2. 生成分组和文章页面...")
        for group_name, group_articles in articles_by_group.items():
            print(f"  处理分组: {group_name} ({len(group_articles)}篇)")

            # 生成分组首页
            group_index_path = generate_group_index(group_name, group_articles, BUILD_DIR)
            print(f"    ✓ 生成分组首页: {group_index_path}")

            # 生成每篇文章的HTML
            for article in group_articles:
                article_path = generate_article_html(article, BUILD_DIR)
                print(f"    ✓ 生成文章: {article_path}")

        # 6. 生成所有文章总览页
        print("\n3. 生成总览页面...")
        main_index_path = generate_main_articles_index(all_articles, BUILD_DIR)
        print(f"✓ 生成总览页: {main_index_path}")

        # 7. 创建.htaccess或配置重定向（如果需要）
        create_redirect_rules(BUILD_DIR)

        print("\n" + "=" * 50)
        print("构建完成!")
        print(f"输出目录: {BUILD_DIR}")
        print(f"文章总数: {len(all_articles)}")
        print(f"分组数量: {len(articles_by_group)}")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"\n✗ 构建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_redirect_rules(build_dir):
    """创建重定向规则（用于处理旧URL）"""
    # 创建.htaccess文件（Apache）
    htaccess_content = """
# 旧URL重定向到新URL
RewriteEngine On

# 旧的article.html?name=xxx 重定向到新的分组文章
RewriteCond %{QUERY_STRING} ^name=([^&]+)
RewriteRule ^article\.html$ /articles/groups/default/%1.html [R=301,L]

# 如果没有找到文件，尝试默认分组
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^articles/([^/.]+)\.html$ /articles/groups/default/$1.html [R=301,L]
"""

    htaccess_file = build_dir / ".htaccess"
    htaccess_file.write_text(htaccess_content, encoding='utf-8')

    # 也可以创建Netlify的_redirects文件
    redirects_content = """
# 旧URL重定向
/article.html?name=* /articles/groups/default/:splat.html 301
/articles/*.html /articles/groups/default/:splat.html 301
"""

    redirects_file = build_dir / "_redirects"
    redirects_file.write_text(redirects_content, encoding='utf-8')

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)