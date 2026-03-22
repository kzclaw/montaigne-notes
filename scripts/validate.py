#!/usr/bin/env python3
"""
Montaigne 笔记验证脚本

验证笔记是否符合 Montaigne 规范
"""

import argparse
import subprocess
import re
from pathlib import Path

# 配置路径（skill 目录下的 config 文件夹）
SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_FILE = SKILL_DIR / "config" / "config.json"


def get_full_folder_path(folder_name):
    """获取完整的文件夹路径"""
    import json
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        root_folder = config.get("folders", {}).get("root", "")
        
        # 如果 folder_name 已经是完整路径，直接返回
        if ".montaigne.io" in folder_name:
            return folder_name
        
        # 检查 folder_name 是否是已知的子文件夹
        known_folders = ["Canvas", "Bewitching", "Clipper", "Nonsense", "Draft"]
        if folder_name in known_folders:
            return folder_name
        
        # 如果是根文件夹本身
        if folder_name == root_folder:
            return folder_name
        
        # 其他情况，尝试拼接根文件夹
        if root_folder and folder_name.lower() not in ["index", root_folder.lower()]:
            return f"{root_folder}/{folder_name}"
    
    return folder_name


def get_note_body(folder_name, note_name):
    """获取笔记内容"""
    full_folder = get_full_folder_path(folder_name)
    
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
            return "ERROR: 找不到文件夹"
        end if
        
        -- 查找笔记
        set targetNote to null
        repeat with currentNote in notes of targetFolder
            if name of currentNote is "{note_name}" then
                set targetNote to currentNote
                exit repeat
            end if
        end repeat
        
        if targetNote is null then
            return "ERROR: 找不到笔记"
        end if
        
        return body of targetNote
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
    return result.stdout.strip()


def extract_metadata(body):
    """从笔记内容中提取元数据"""
    metadata = {}
    
    # 简单模式匹配 - 查找字段名后的 <div>值</div>
    # location: 在 "location" 之后查找下一个 <div>内容</div>
    loc_pattern = r'location</div>\s*</td>\s*<td[^>]*>\s*<div>([^<]+)</div>'
    loc_match = re.search(loc_pattern, body, re.DOTALL)
    if loc_match:
        metadata['location'] = loc_match.group(1).strip()
    
    # description
    desc_pattern = r'description</div>\s*</td>\s*<td[^>]*>\s*<div>([^<]+)</div>'
    desc_match = re.search(desc_pattern, body, re.DOTALL)
    if desc_match:
        metadata['description'] = desc_match.group(1).strip()
    
    # date
    date_pattern = r'date</div>\s*</td>\s*<td[^>]*>\s*<div>(\d{4}-\d{2}-\d{2})</div>'
    date_match = re.search(date_pattern, body, re.DOTALL)
    if date_match:
        metadata['date'] = date_match.group(1).strip()
    
    # tags
    tags_pattern = r'tags</div>\s*</td>\s*<td[^>]*>\s*<div>([^<]+)</div>'
    tags_match = re.search(tags_pattern, body, re.DOTALL)
    if tags_match:
        metadata['tags'] = tags_match.group(1).strip()
    
    # slug
    slug_pattern = r'slug</div>\s*</td>\s*<td[^>]*>\s*<div>(\d+)</div>'
    slug_match = re.search(slug_pattern, body, re.DOTALL)
    if slug_match:
        metadata['slug'] = slug_match.group(1).strip()
    
    return metadata


def validate_metadata(metadata):
    """验证元数据"""
    errors = []
    warnings = []
    
    # 检查必填字段
    required_fields = ['location', 'description', 'date', 'tags', 'slug']
    for field in required_fields:
        if field not in metadata or not metadata[field]:
            errors.append(f"缺少必填字段: {field}")
    
    # 验证 location
    if 'location' in metadata:
        location = metadata['location']
        # 检查是否使用中文
        if re.search(r'[\u4e00-\u9fff]', location):
            errors.append(f"location 应使用英文: {location}")
        # 检查是否使用中文逗号
        if '，' in location:
            errors.append(f"location 应使用英文逗号分隔: {location}")
    
    # 验证 date
    if 'date' in metadata:
        date = metadata['date']
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
            errors.append(f"date 格式应为 YYYY-MM-DD: {date}")
    
    # 验证 slug
    if 'slug' in metadata:
        slug = metadata['slug']
        if not slug.isdigit():
            errors.append(f"slug 应为数字: {slug}")
    
    # 验证 tags
    if 'tags' in metadata:
        tags = metadata['tags']
        # 检查是否使用粗体标记
        if '**' not in tags:
            warnings.append("tags 建议使用粗体标记: **标签**")
        # 检查是否使用中文逗号
        if '、' in tags or '，' in tags:
            warnings.append("tags 应使用英文逗号分隔")
    
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="验证 Montaigne 笔记")
    parser.add_argument("--folder", required=True, help="文件夹名")
    parser.add_argument("--title", required=True, help="笔记标题")
    
    args = parser.parse_args()
    
    print(f"=== 验证笔记: {args.title} ===")
    print(f"文件夹: {get_full_folder_path(args.folder)}")
    print()
    
    # 获取笔记内容
    body = get_note_body(args.folder, args.title)
    
    if body.startswith("ERROR"):
        print(f"❌ {body}")
        return 1
    
    # 提取元数据
    metadata = extract_metadata(body)
    
    print("提取的元数据:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    print()
    
    # 验证元数据
    errors, warnings = validate_metadata(metadata)
    
    if errors:
        print("❌ 错误:")
        for error in errors:
            print(f"  - {error}")
        print()
    
    if warnings:
        print("⚠️  警告:")
        for warning in warnings:
            print(f"  - {warning}")
        print()
    
    if not errors and not warnings:
        print("✅ 笔记格式正确！")
    elif not errors:
        print("✅ 笔记基本格式正确，但有一些建议")
    else:
        print("❌ 笔记存在格式问题，请修正后重试")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
