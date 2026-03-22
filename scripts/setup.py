#!/usr/bin/env python3
"""
Montaigne Notes 初始化向导
交互式配置，支持从旧版本迁移
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent.resolve()

# 尝试导入 config 模块
try:
    from config import (
        load_config, save_config, set_username, add_folder_category,
        migrate_legacy_config, DEFAULT_CONFIG, CONFIG_FILE
    )
except ImportError:
    sys.path.insert(0, str(SCRIPT_DIR))
    from config import (
        load_config, save_config, set_username, add_folder_category,
        migrate_legacy_config, DEFAULT_CONFIG, CONFIG_FILE
    )


def print_header(text):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_step(step_num, total, text):
    """打印步骤"""
    print(f"\n[步骤 {step_num}/{total}] {text}")
    print("-" * 40)


def input_required(prompt):
    """获取必填输入"""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("⚠️  此项为必填，请重新输入")


def input_optional(prompt, default=""):
    """获取可选输入"""
    value = input(f"{prompt} [{default}]: ").strip()
    return value if value else default


def input_yes_no(prompt, default=True):
    """获取是/否输入"""
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        value = input(f"{prompt} {suffix}: ").strip().lower()
        if not value:
            return default
        if value in ('y', 'yes'):
            return True
        if value in ('n', 'no'):
            return False
        print("⚠️  请输入 y 或 n")


def input_date(prompt):
    """获取日期输入"""
    while True:
        value = input(f"{prompt} (YYYY-MM-DD): ").strip()
        if not value:
            return None
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("⚠️  日期格式不正确，请使用 YYYY-MM-DD 格式")


def detect_apple_notes_folders():
    """检测 Apple Notes 中的文件夹"""
    print("🔍 正在检测 Apple Notes 文件夹...")
    
    applescript = '''
    tell application "Notes"
        set folderList to {}
        set defaultAccount to default account
        repeat with currentFolder in folders of defaultAccount
            set end of folderList to name of currentFolder
        end repeat
        return folderList
    end tell
    '''
    
    import subprocess
    result = subprocess.run(['osascript', '-e', applescript], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        # 解析返回的列表
        folders_str = result.stdout.strip()
        # 移除 AppleScript 列表格式符号
        folders_str = folders_str.replace('{', '').replace('}', '')
        folders = [f.strip().strip('"') for f in folders_str.split(',') if f.strip()]
        return folders
    
    return []


def suggest_categories(detected_folders, username):
    """根据检测到的文件夹建议分类"""
    root_folder = f"{username}.montaigne.io"
    
    # 常见的 Montaigne 文件夹名称
    common_categories = {
        'blog': ['Blog', 'Posts', 'Articles', 'Writing', 'Canvas'],
        'life': ['Life', 'Daily', 'Personal', 'Bewitching'],
        'notes': ['Notes', 'Clippings', 'Clipper', 'Bookmarks'],
        'travel': ['Travel', 'Trips', 'Nonsense', 'Journey'],
        'drafts': ['Draft', 'Drafts', 'Templates']
    }
    
    suggested = []
    folder_lower = [f.lower() for f in detected_folders]
    
    for category_type, names in common_categories.items():
        for name in names:
            if name.lower() in folder_lower:
                suggested.append({
                    'name': name,
                    'type': category_type,
                    'exists': True
                })
                break
    
    return suggested


def configure_slug_rule(category_name):
    """配置 slug 规则"""
    print(f"\n📐 配置 [{category_name}] 的 Slug 规则")
    print("""
Slug 是文章 URL 的标识符，可以选择以下生成方式：

1. 递增数字 (1, 2, 3...) - 最简单
2. 日期差计算 (从某个日期起的天数) - 有时间意义
3. 拼音/英文标题 (wo-de-wen-zhang) - 可读性好
4. 手动输入 - 完全自定义
""")
    
    while True:
        choice = input("请选择 [1-4]: ").strip()
        
        if choice == "1":
            start_num = input_optional("起始数字", "1")
            return {
                "type": "incremental",
                "start": int(start_num) if start_num.isdigit() else 1
            }
        
        elif choice == "2":
            print("\n💡 提示：可以输入生日、纪念日、建站日期等")
            base_date = input_date("起始日期")
            if base_date:
                return {
                    "type": "date_diff",
                    "base_date": base_date
                }
        
        elif choice == "3":
            print("\n💡 会将标题自动转换为拼音或英文")
            max_len = input_optional("最大长度 (字符数)", "50")
            return {
                "type": "pinyin",
                "max_length": int(max_len) if max_len.isdigit() else 50
            }
        
        elif choice == "4":
            print("\n💡 每次创建笔记时需要手动输入 slug")
            return {
                "type": "manual"
            }
        
        print("⚠️  请输入 1-4 之间的数字")


def run_setup_wizard():
    """运行初始化向导"""
    print_header("Montaigne Notes 初始化向导")
    
    # 检查是否已有配置
    config = load_config()
    if CONFIG_FILE.exists():
        print("⚠️  检测到已有配置")
        if not input_yes_no("是否重新配置？"):
            print("\n✅ 保持现有配置")
            return config
    
    # 尝试迁移旧配置
    print("\n📦 检查旧版本配置...")
    migration_result = migrate_legacy_config()
    
    if migration_result:
        print(f"✅ 已从旧版本迁移配置")
        print(f"   位置: {migration_result['from']}")
        
        if input_yes_no("是否查看迁移后的配置并继续修改？", True):
            config = migration_result['config']
            print("\n当前配置:")
            print(json.dumps(config, indent=2, ensure_ascii=False))
        else:
            return migration_result['config']
    
    # 步骤 1: 用户名
    print_step(1, 4, "设置 Montaigne 用户名")
    print("这是你的 Montaigne 网站标识")
    print("例如：输入 'john'，网站将是 https://john.montaigne.io")
    
    if config.get('username'):
        username = input_optional("用户名", config['username'])
    else:
        username = input_required("用户名: ")
    
    set_username(username)
    print(f"✅ 网站地址: https://{username}.montaigne.io")
    
    # 步骤 2: 检测文件夹
    print_step(2, 4, "配置文件夹结构")
    detected_folders = detect_apple_notes_folders()
    
    if detected_folders:
        print(f"\n📁 检测到 {len(detected_folders)} 个文件夹:")
        for i, folder in enumerate(detected_folders[:10], 1):
            marker = " ✓" if f"{username}.montaigne.io" in folder else ""
            print(f"   {i}. {folder}{marker}")
        
        if len(detected_folders) > 10:
            print(f"   ... 还有 {len(detected_folders) - 10} 个")
    
    # 步骤 3: 配置分类
    print_step(3, 4, "设置内容分类")
    print("""
你可以为不同类型的内容设置不同的文件夹和 slug 规则。
例如：
- Blog 文章 → 使用拼音 slug
- 生活记录 → 使用日期差 slug
- 收集箱 → 使用递增数字
""")
    
    # 建议的分类
    suggested = suggest_categories(detected_folders, username)
    
    if suggested and input_yes_no("是否使用检测到的文件夹作为分类？", True):
        for item in suggested:
            if item['name'] == f"{username}.montaigne.io":
                continue  # 跳过根文件夹
            
            print(f"\n📂 配置分类: {item['name']}")
            slug_rule = configure_slug_rule(item['name'])
            add_folder_category(item['name'], **slug_rule)
            print(f"✅ 已添加: {item['name']} ({slug_rule['type']})")
    
    # 手动添加更多分类
    while input_yes_no("\n是否添加更多分类？"):
        category_name = input_required("分类名称: ")
        slug_rule = configure_slug_rule(category_name)
        add_folder_category(category_name, **slug_rule)
        print(f"✅ 已添加: {category_name}")
    
    # 步骤 4: 隐私设置
    print_step(4, 4, "隐私设置（可选）")
    print("""
如果你需要在每篇文章中添加隐私提示或身份声明，
可以在这里设置，创建笔记时会自动附加。
""")
    
    if input_yes_no("是否启用隐私提示？"):
        notice = input("请输入隐私提示文本（支持多行，空行结束）：\n")
        lines = [notice]
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        
        config = load_config()
        config["privacy_notice"] = {
            "enabled": True,
            "notice_text": "\n".join(lines)
        }
        save_config(config)
        print("✅ 隐私提示已设置")
    
    # 完成
    print_header("初始化完成！")
    config = load_config()
    
    print(f"🌐 网站: {config['site_url']}")
    print(f"📁 根文件夹: {config['folders']['root']}")
    print("\n📂 内容分类:")
    for name, rule in config.get('slug_rules', {}).items():
        if name != 'default':
            print(f"   - {name}: {rule['type']}")
    
    setup_script = SCRIPT_DIR / "setup.py"
    print(f"\n💡 提示：随时运行 '{setup_script}' 可以重新配置")
    print(f"💡 配置位置: {CONFIG_FILE}")
    
    return config


def quick_setup():
    """快速设置（最小配置）"""
    print_header("Montaigne Notes 快速设置")
    
    username = input_required("用户名: ")
    set_username(username)
    
    # 设置一个默认的递增 slug
    config = load_config()
    config["slug_rules"]["default"] = {
        "type": "incremental",
        "start": 1
    }
    save_config(config)
    
    print(f"\n✅ 快速设置完成！")
    print(f"   网站: https://{username}.montaigne.io")
    print(f"   Slug: 递增数字 (1, 2, 3...)")
    setup_script = SCRIPT_DIR / "setup.py"
    print(f"\n💡 运行 '{setup_script} --wizard' 进行完整配置")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Montaigne Notes 初始化向导")
    parser.add_argument("--wizard", action="store_true", 
                       help="运行完整配置向导")
    parser.add_argument("--quick", action="store_true",
                       help="快速设置（仅用户名）")
    parser.add_argument("--migrate", action="store_true",
                       help="仅迁移旧配置")
    
    args = parser.parse_args()
    
    if args.migrate:
        result = migrate_legacy_config()
        if result:
            print(f"✅ 配置已迁移")
            print(f"   从: {result['from']}")
            print(f"   到: {result['to']}")
        else:
            print("ℹ️  未找到旧配置")
    
    elif args.quick:
        quick_setup()
    
    else:
        # 默认运行完整向导
        run_setup_wizard()


if __name__ == "__main__":
    main()
