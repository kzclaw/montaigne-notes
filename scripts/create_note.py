#!/usr/bin/env python3
"""
Montaigne Notes 笔记创建工具
支持多种 slug 规则和通用配置
"""

import argparse
import html
import json
import re
import subprocess
from pathlib import Path

# 尝试导入 config 和 calc_slug
try:
    from config import load_config, get_slug_rule, CONFIG_DIR
    from calc_slug import calc_slug
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from config import load_config, get_slug_rule, CONFIG_DIR
    from calc_slug import calc_slug


def load_config_safe():
    """安全加载配置"""
    try:
        return load_config()
    except:
        return None


def get_full_folder_path(folder_name):
    """获取完整的文件夹路径"""
    config = load_config_safe()
    if not config:
        return folder_name
    
    root_folder = config.get("folders", {}).get("root", "")
    
    # 如果 folder_name 已经是完整路径，直接返回
    if ".montaigne.io" in folder_name:
        return folder_name
    
    # 检查是否是已知的分类文件夹（新格式：categories 列表）
    categories = config.get("folders", {}).get("categories", [])
    category_names = [c.get("name") for c in categories]
    
    if folder_name in category_names:
        return folder_name
    
    # 兼容旧格式：检查 canvas, bewitching 等键
    old_category_keys = ["canvas", "bewitching", "clipper", "nonsense"]
    folders_config = config.get("folders", {})
    for key in old_category_keys:
        if folders_config.get(key) == folder_name:
            return folder_name
    
    # 如果是根文件夹本身
    if folder_name == root_folder:
        return folder_name
    
    # 其他情况，尝试拼接根文件夹
    if root_folder and folder_name.lower() not in ["index", root_folder.lower()]:
        return f"{root_folder}/{folder_name}"
    
    return folder_name


def set_note_body_by_applescript(folder_name, note_name, html_content):
    """通过 AppleScript 设置笔记内容"""
    # 转义特殊字符
    escaped_html = html_content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    
    applescript = f'''
    tell application "Notes"
        set defaultAccount to default account
        
        -- 查找文件夹
        set targetFolder to null
        repeat with currentFolder in folders of defaultAccount
            if name of currentFolder is "{folder_name}" then
                set targetFolder to currentFolder
                exit repeat
            end if
        end repeat

        if targetFolder is null then
            return "ERROR: 找不到文件夹 " & "{folder_name}"
        end if

        -- 等待笔记创建完成
        delay 0.5

        -- 查找笔记
        set targetNote to null
        repeat with currentNote in notes of targetFolder
            if name of currentNote is "{note_name}" then
                set targetNote to currentNote
                exit repeat
            end if
        end repeat

        if targetNote is null then
            return "ERROR: 找不到笔记 " & "{note_name}"
        end if

        -- 设置笔记内容
        set body of targetNote to "{escaped_html}"

        return "SUCCESS"
    end tell
    '''

    result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
    if result.stderr:
        print(f"[ERROR] AppleScript: {result.stderr}")
    return result.stdout.strip()


def markdown_to_simple_html(markdown):
    """
    将 Markdown 转换为简单的 HTML（保留基本格式和层次）
    """
    lines = markdown.split('\n')
    html_parts = ['<div>']
    current_paragraph = []

    for line in lines:
        if line.startswith('## '):
            # 二级标题
            if current_paragraph:
                html_parts.append(' '.join(current_paragraph) + '<br>')
                current_paragraph = []
            title = line[3:].replace('**', '').strip()
            html_parts.append(f'<br><b>{title}</b><br><br>')
        elif line.startswith('- '):
            # 列表项
            if current_paragraph:
                html_parts.append(' '.join(current_paragraph) + '<br>')
                current_paragraph = []
            content = line[2:].replace('**', '').strip()
            html_parts.append(f'<br>→ {content}')
        elif line.strip() == '':
            # 空行
            if current_paragraph:
                html_parts.append(' '.join(current_paragraph) + '<br><br>')
                current_paragraph = []
            if not html_parts[-1].endswith('<br><br>'):
                html_parts.append('<br>')
        else:
            # 普通文本
            current_paragraph.append(line.replace('**', '').strip())

    if current_paragraph:
        html_parts.append(' '.join(current_paragraph))

    html_parts.append('</div>')
    html = ''.join(html_parts)
    
    # 清理多余的 <br>
    html = html.replace('<br><br><br>', '<br><br>')
    html = html.replace('<br><br><br>', '<br><br>')

    return html


def build_metadata_html(note_title, location, description, date, tags, slug):
    """构建元数据表格 HTML"""
    # 处理 tags，确保格式正确（标签不需要加粗）
    tags_formatted = tags.replace('**', '')
    if ',' in tags_formatted and ' | ' not in tags_formatted:
        # 将逗号分隔的标签用 " , " 连接
        tag_list = [t.strip() for t in tags_formatted.split(',')]
        tags_formatted = ' , '.join(tag_list)
    
    html = f'''<div><b><h1>{note_title}</h1></b></div>
<div><object><table cellspacing="0" cellpadding="0" style="border-collapse: collapse; direction: ltr">
<tbody>
<tr><td valign="top" style="border-style: solid; border-width: 1.0px 1.0px 1.0px 1.0px; border-color: #ccc; padding: 3.0px 5.0px 3.0px 5.0px; min-width: 70px"><div>name</div>
</td><td valign="top" style="border-style: solid; border-width: 1.0px 1.0px 1.0px 1.0px; border-color: #ccc; padding: 3.0px 5.0px 3.0px 5.0px; min-width: 70px"><div>value</div>
</td></tr>
<tr><td valign="top" style="border-style: solid; border-width: 1.0px 1.0px 1.0px 1.0px; border-color: #ccc; padding: 3.0px 5.0px 3.0px 5.0px; min-width: 70px"><div>location</div>
</td><td valign="top" style="border-style: solid; border-width: 1.0px 1.0px 1.0px 1.0px; border-color: #ccc; padding: 3.0px 5.0px 3.0px 5.0px; min-width: 70px"><div>{location}</div></td></tr>
<tr><td valign="top" style="border-style: solid; border-width: 1.0px 1.0px 1.0px 1.0px; border-color: #ccc; padding: 3.0px 5.0px 3.0px 5.0px; min-width: 70px"><div>description</div>
</td><td valign="top" style="border-style: solid; border-width: 1.0px 1.0px 1.0px 1.0px; border-color: #ccc; padding: 3.0px 5.0px 3.0px 5.0px; min-width: 70px"><div>{description}</div></td></tr>
<tr><td valign="top" style="border-style: solid; border-width: 1.0px 1.0px 1.0px 1.0px; border-color: #ccc; padding: 3.0px 5.0px 3.0px 5.0px; min-width: 70px"><div>date</div>
</td><td valign="top" style="border-style: solid; border-width: 1.0px 1.0px 1.0px 1.0px; border-color: #ccc; padding: 3.0px 5.0px 3.0px 5.0px; min-width: 70px"><div>{date}</div></td></tr>
<tr><td valign="top" style="border-style: solid; border-width: 1.0px 1.0px 1.0px 1.0px; border-color: #ccc; padding: 3.0px 5.0px 3.0px 5.0px; min-width: 70px"><div>tags</div>
</td><td valign="top" style="border-style: solid; border-width: 1.0px 1.0px 1.0px 1.0px; border-color: #ccc; padding: 3.0px 5.0px 3.0px 5.0px; min-width: 70px"><div>{tags_formatted}</div></td></tr>
<tr><td valign="top" style="border-style: solid; border-width: 1.0px 1.0px 1.0px 1.0px; border-color: #ccc; padding: 3.0px 5.0px 3.0px 5.0px; min-width: 70px"><div>slug</div>
</td><td valign="top" style="border-style: solid; border-width: 1.0px 1.0px 1.0px 1.0px; border-color: #ccc; padding: 3.0px 5.0px 3.0px 5.0px; min-width: 70px"><div>{slug}</div></td></tr>
</tbody>
</table></object><br></div>'''
    return html


def create_note(folder_name, note_title, location, description, date, tags, slug, content_file):
    """创建 Montaigne 笔记"""
    
    # 读取正文内容
    with open(content_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 跳过 YAML frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    
    # 检查是否需要添加隐私提示
    config = load_config_safe()
    privacy_notice = config.get("privacy_notice", {}) if config else {}
    if privacy_notice.get("enabled") and privacy_notice.get("notice_text"):
        content = content + "\n\n---\n\n" + privacy_notice["notice_text"]
    
    # 构建完整 HTML
    metadata_html = build_metadata_html(note_title, location, description, date, tags, slug)
    content_html = markdown_to_simple_html(content)
    full_html = metadata_html + content_html
    
    # 获取完整文件夹路径
    full_folder = get_full_folder_path(folder_name)
    
    # 直接创建笔记
    applescript = f'''
    tell application "Notes"
        set defaultAccount to default account
        
        -- 查找文件夹
        set targetFolder to null
        repeat with currentFolder in folders of defaultAccount
            if name of currentFolder is "{full_folder}" then
                set targetFolder to currentFolder
                exit repeat
            end if
        end repeat
        
        if targetFolder is null then
            return "ERROR: 找不到文件夹 " & "{full_folder}"
        end if
        
        -- 创建笔记
        set newNote to make new note at targetFolder with properties {{name:"{note_title}", body:""}}
        
        return "SUCCESS"
    end tell
    '''
    result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
    if result.stderr:
        print(f"[ERROR] Create AppleScript: {result.stderr}")
    
    # 设置笔记内容
    result = set_note_body_by_applescript(full_folder, note_title, full_html)
    
    if "SUCCESS" in result:
        print(f"✅ 笔记创建成功: {note_title}")
        print(f"📁 文件夹: {full_folder}")
        print(f"🔗 Slug: {slug}")
        return True
    else:
        print(f"❌ 笔记创建失败: {result}")
        return False


def main():
    parser = argparse.ArgumentParser(description="创建 Montaigne 笔记")
    parser.add_argument("--folder", required=True, help="目标文件夹名")
    parser.add_argument("--title", required=True, help="笔记标题")
    parser.add_argument("--location", required=True, help="地点（英文）")
    parser.add_argument("--description", required=True, help="文章简介")
    parser.add_argument("--date", required=True, help="日期 (YYYY-MM-DD)")
    parser.add_argument("--tags", required=True, help="标签（逗号分隔）")
    parser.add_argument("--content-file", required=True, help="正文 Markdown 文件路径")
    parser.add_argument("--slug", help="指定 slug 值（自动计算则省略）")
    parser.add_argument("--slug-base", help="Slug 计算起始日期")

    args = parser.parse_args()

    # 计算 slug
    if args.slug:
        slug = args.slug
    else:
        # 获取文件夹的 slug 规则
        rule = get_slug_rule(args.folder)
        rule_type = rule.get('type', 'incremental')
        
        if rule_type == 'manual':
            print("❌ 此文件夹配置为手动输入 slug，请使用 --slug 参数指定")
            return 1
        
        try:
            slug = calc_slug(
                folder_name=args.folder,
                date_str=args.date,
                title=args.title
            )
        except Exception as e:
            print(f"❌ Slug 计算失败: {e}")
            return 1

    # 创建笔记
    success = create_note(
        folder_name=args.folder,
        note_title=args.title,
        location=args.location,
        description=args.description,
        date=args.date,
        tags=args.tags,
        slug=slug,
        content_file=args.content_file
    )

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
