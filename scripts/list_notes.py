#!/usr/bin/env python3
"""
Montaigne 笔记列表脚本

列出指定文件夹中的笔记
"""

import argparse
import subprocess
import json
from pathlib import Path

# 配置路径（skill 目录下的 config 文件夹）
SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_FILE = SKILL_DIR / "config" / "config.json"


def load_config():
    """加载配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def get_full_folder_path(folder_name):
    """获取完整的文件夹路径"""
    config = load_config()
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


def list_notes_in_folder(folder_name):
    """列出文件夹中的笔记"""
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
            return "ERROR: 找不到文件夹 " & "{full_folder}"
        end if
        
        -- 列出笔记
        set noteList to {{}}
        repeat with currentNote in notes of targetFolder
            set noteInfo to {{name:name of currentNote, modificationDate:modification date of currentNote}}
            set end of noteList to noteInfo
        end repeat
        
        return noteList as string
    end tell
    '''
    
    # 使用 memo CLI 更简单
    result = subprocess.run(
        ['memo', 'notes', '-f', full_folder],
        capture_output=True, text=True
    )
    
    return result.stdout, result.stderr, result.returncode


def main():
    parser = argparse.ArgumentParser(description="列出 Montaigne 笔记")
    parser.add_argument("--folder", required=True, help="文件夹名")
    parser.add_argument("--raw", action="store_true", help="显示原始输出")
    
    args = parser.parse_args()
    
    config = load_config()
    full_folder = get_full_folder_path(args.folder)
    
    print(f"=== {args.folder} 笔记列表 ===")
    print(f"完整路径: {full_folder}")
    
    if config.get("username"):
        print(f"网站: {config.get('site_url')}")
    
    print()
    
    stdout, stderr, returncode = list_notes_in_folder(args.folder)
    
    if returncode == 0:
        if stdout.strip():
            print(stdout)
        else:
            print("该文件夹中没有笔记")
    else:
        print(f"错误: {stderr}")
        print("\n提示: 确保已安装 memo CLI")
        print("  brew tap antoniorodr/memo && brew install antoniorodr/memo/memo")


if __name__ == "__main__":
    main()
