#!/usr/bin/env python3
"""
Montaigne Notes 配置管理
支持通用配置格式和配置迁移
"""

import json
import os
import sys
from pathlib import Path

# 配置目录（skill 目录下的 config 文件夹）
SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_DIR = SKILL_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "config.json"

# 其他脚本路径（用于提示信息）
SETUP_SCRIPT = SCRIPT_DIR / "setup.py"

# 默认配置
DEFAULT_CONFIG = {
    "version": "2.0.0",
    "username": "",
    "site_url": "",
    "folders": {
        "root": "",
        "categories": []
    },
    "slug_rules": {
        "default": {
            "type": "incremental",
            "start": 1
        }
    },
    "privacy_notice": {
        "enabled": False,
        "notice_text": ""
    }
}


def ensure_config_dir():
    """确保配置目录存在"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    """加载配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 合并默认配置（处理新增字段）
            merged = DEFAULT_CONFIG.copy()
            merged.update(config)
            return merged
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """保存配置"""
    ensure_config_dir()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def migrate_legacy_config():
    """
    迁移旧版配置到通用格式
    检测旧配置并自动转换
    """
    # 旧配置路径（历史兼容）
    legacy_paths = [
        Path.home() / ".workbuddy" / "config" / "montaigne-notes.json",
        Path.home() / ".config" / "openclaw" / "montaigne-notes.json",
    ]
    
    legacy_config = None
    legacy_path = None
    
    for path in legacy_paths:
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    legacy_config = json.load(f)
                    legacy_path = path
                    break
            except:
                continue
    
    if not legacy_config:
        return None
    
    # 转换旧配置到新格式
    new_config = DEFAULT_CONFIG.copy()
    
    # 迁移基本字段
    if "username" in legacy_config:
        new_config["username"] = legacy_config["username"]
        new_config["site_url"] = f"https://{legacy_config['username']}.montaigne.io"
    
    if "folders" in legacy_config:
        new_config["folders"] = legacy_config["folders"]
    
    # 迁移 slug 配置
    if "slug_base_personal" in legacy_config or "slug_base_shared" in legacy_config:
        new_config["slug_rules"] = {}
        
        # 检测文件夹并分配 slug 规则
        categories = new_config["folders"].get("categories", [])
        if not categories and "folders" in legacy_config:
            # 从旧配置推断分类
            root_folder = legacy_config["folders"].get("root", "")
            # 常见分类映射（使用用户配置的起始日期，或默认日期）
            default_personal = legacy_config.get("slug_base_personal", "2000-01-01")
            default_shared = legacy_config.get("slug_base_shared", "2020-01-01")
            category_mapping = {
                "Canvas": default_personal,
                "Bewitching": default_shared,
                "Clipper": default_personal,
                "Nonsense": default_shared,
            }
            
            for folder_name, base_date in category_mapping.items():
                new_config["slug_rules"][folder_name] = {
                    "type": "date_diff",
                    "base_date": base_date
                }
        
        new_config["slug_rules"]["default"] = {
            "type": "date_diff",
            "base_date": legacy_config.get("slug_base_personal", "2000-01-01")
        }
    
    # 保存新配置
    save_config(new_config)
    
    return {
        "migrated": True,
        "from": str(legacy_path),
        "to": str(CONFIG_FILE),
        "config": new_config
    }


def get_slug_rule(folder_name, config=None):
    """获取指定文件夹的 slug 规则"""
    if config is None:
        config = load_config()
    
    rules = config.get("slug_rules", {})
    
    # 先查找文件夹特定规则
    if folder_name in rules:
        return rules[folder_name]
    
    # 返回默认规则
    return rules.get("default", DEFAULT_CONFIG["slug_rules"]["default"])


def set_username(username):
    """设置用户名"""
    config = load_config()
    config["username"] = username
    config["site_url"] = f"https://{username}.montaigne.io"
    config["folders"]["root"] = f"{username}.montaigne.io"
    save_config(config)
    return config


def add_folder_category(name, slug_type="incremental", **kwargs):
    """添加文件夹分类"""
    config = load_config()
    
    # 添加到分类列表
    categories = config["folders"].get("categories", [])
    if name not in [c.get("name") for c in categories]:
        categories.append({"name": name})
        config["folders"]["categories"] = categories
    
    # 设置 slug 规则
    rule = {"type": slug_type}
    rule.update(kwargs)
    config["slug_rules"][name] = rule
    
    save_config(config)
    return config


def show_config():
    """显示当前配置（隐私信息脱敏）"""
    config = load_config()
    
    # 创建副本用于显示
    display_config = json.loads(json.dumps(config))
    
    # 脱敏 slug 规则中的日期
    if "slug_rules" in display_config:
        for key, rule in display_config["slug_rules"].items():
            if isinstance(rule, dict) and "base_date" in rule:
                # 显示为提示，不显示实际日期
                rule["base_date"] = "[已配置]"
    
    print(json.dumps(display_config, indent=2, ensure_ascii=False))
    return config


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Montaigne Notes 配置管理")
    parser.add_argument("--set-username", help="设置用户名")
    parser.add_argument("--add-category", help="添加文件夹分类")
    parser.add_argument("--slug-type", default="incremental", 
                       choices=["incremental", "date_diff", "pinyin", "manual"],
                       help="Slug 生成方式")
    parser.add_argument("--base-date", help="日期差计算的起始日期 (YYYY-MM-DD)")
    parser.add_argument("--show", action="store_true", help="显示当前配置")
    parser.add_argument("--migrate", action="store_true", help="尝试迁移旧配置")
    
    args = parser.parse_args()
    
    if args.migrate:
        result = migrate_legacy_config()
        if result:
            print(f"✅ 配置已迁移")
            print(f"   从: {result['from']}")
            print(f"   到: {result['to']}")
        else:
            print("ℹ️  未找到旧配置")
    
    elif args.set_username:
        config = set_username(args.set_username)
        print(f"✅ 用户名已设置: {args.set_username}")
        print(f"   网站: {config['site_url']}")
    
    elif args.add_category:
        kwargs = {}
        if args.base_date:
            kwargs["base_date"] = args.base_date
        config = add_folder_category(args.add_category, args.slug_type, **kwargs)
        print(f"✅ 分类已添加: {args.add_category}")
        print(f"   Slug 类型: {args.slug_type}")
    
    elif args.show:
        show_config()
    
    else:
        # 首次运行或没有配置时，尝试迁移
        if not CONFIG_FILE.exists():
            result = migrate_legacy_config()
            if result:
                print(f"✅ 已自动迁移旧配置")
                print(f"   从: {result['from']}")
                show_config()
            else:
                print(f"ℹ️  尚未配置，请运行 '{SETUP_SCRIPT}' 进行初始化")
        else:
            show_config()


if __name__ == "__main__":
    main()
