#!/usr/bin/env python3
"""
Montaigne 文件夹列表脚本

列出 Apple Notes 中与 Montaigne 相关的文件夹
"""

import subprocess
import json
import sys
from pathlib import Path

# 配置路径（skill 目录下的 config 文件夹）
SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_FILE = SKILL_DIR / "config" / "config.json"

# 获取脚本所在目录，用于提示信息
SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_SCRIPT = SCRIPT_DIR / "config.py"


def load_config():
    """加载配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def list_all_folders():
    """列出所有 Apple Notes 文件夹"""
    applescript = '''
    tell application "Notes"
        set folderList to {}
        set defaultAccount to default account
        repeat with currentFolder in folders of defaultAccount
            set end of folderList to name of currentFolder
        end repeat
        return folderList as string
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
    if result.returncode == 0:
        # 解析返回的列表字符串
        folders_str = result.stdout.strip()
        # 移除 AppleScript 列表格式符号
        folders_str = folders_str.replace('"', '').replace('{', '').replace('}', '')
        folders = [f.strip() for f in folders_str.split(',') if f.strip()]
        return folders
    else:
        print(f"错误: {result.stderr}")
        return []


def find_montaigne_folders():
    """查找 Montaigne 相关的文件夹"""
    all_folders = list_all_folders()
    config = load_config()
    username = config.get("username", "")
    
    montaigne_folders = []
    
    for folder in all_folders:
        # 检查是否包含 .montaigne.io
        if ".montaigne.io" in folder.lower():
            montaigne_folders.append({
                "name": folder,
                "type": "root",
                "is_configured": username and folder.startswith(username)
            })
        # 检查是否是配置的子文件夹
        elif username:
            root_folder = f"{username}.montaigne.io"
            # 检查是否是子文件夹（通过路径格式判断）
            if folder in ["Canvas", "Bewitching", "Clipper", "Nonsense", "Draft"]:
                montaigne_folders.append({
                    "name": folder,
                    "type": "subfolder",
                    "is_configured": True
                })
    
    return montaigne_folders


def main():
    config = load_config()
    username = config.get("username", "")
    
    print("=== Montaigne 文件夹列表 ===")
    
    if username:
        print(f"\n已配置用户名: {username}")
        print(f"网站地址: {config.get('site_url', '未设置')}")
    else:
        print("\n⚠️  未配置用户名，请运行:")
        print(f"  python3 {CONFIG_SCRIPT} --set-username <用户名>")
    
    print("\n所有文件夹:")
    all_folders = list_all_folders()
    
    # 分类显示
    root_folders = []
    sub_folders = []
    other_folders = []
    
    for folder in all_folders:
        if ".montaigne.io" in folder.lower():
            root_folders.append(folder)
        elif folder in ["Canvas", "Bewitching", "Clipper", "Nonsense", "Draft", "index"]:
            sub_folders.append(folder)
        else:
            other_folders.append(folder)
    
    if root_folders:
        print("\n📁 Montaigne 网站根文件夹:")
        for folder in root_folders:
            marker = " ✓" if username and folder.startswith(username) else ""
            print(f"  - {folder}{marker}")
    
    if sub_folders:
        print("\n📂 常用子文件夹:")
        for folder in sub_folders:
            print(f"  - {folder}")
    
    if other_folders:
        print("\n📄 其他文件夹:")
        for folder in other_folders[:10]:  # 只显示前10个
            print(f"  - {folder}")
        if len(other_folders) > 10:
            print(f"  ... 还有 {len(other_folders) - 10} 个文件夹")
    
    # 检查配置是否匹配
    if username:
        expected_root = f"{username}.montaigne.io"
        if expected_root not in root_folders:
            print(f"\n⚠️  警告: 未找到配置的根文件夹 '{expected_root}'")
            print("   请确保 Apple Notes 中存在该文件夹")


if __name__ == "__main__":
    main()
