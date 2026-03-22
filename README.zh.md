# Montaigne Notes

通过 Apple Notes 创建和管理 [Montaigne](https://montaigne.io) 网站内容的自动化工具。

## 功能特点

- 📝 **自动化笔记创建**：从 Markdown 文件生成符合 Montaigne 规范的 Apple Notes 笔记
- 🔢 **多种 Slug 生成方式**：支持递增数字、日期差、拼音/英文标题、手动输入
- 📁 **灵活的配置系统**：不同文件夹可以使用不同的 slug 规则
- 🎨 **元数据自动生成**：自动填充 location、description、date、tags、slug 等字段
- 🔒 **可选隐私提示**：支持在每篇文章末尾自动附加隐私声明

## 快速开始

### 1. 克隆或下载本工具

```bash
git clone https://github.com/yourusername/montaigne-notes.git
cd montaigne-notes
```

### 2. 运行初始化向导

```bash
python3 scripts/setup.py
```

向导会引导你完成：
- 设置 Montaigne 用户名
- 检测 Apple Notes 文件夹
- 配置内容分类
- 选择 slug 生成方式

### 3. 创建第一篇笔记

```bash
# 准备 Markdown 文件
echo "## Hello World

这是我的第一篇 Montaigne 文章。" > /tmp/hello.md

# 创建笔记
python3 scripts/create_note.py \
  --folder "Blog" \
  --title "Hello World" \
  --location "Beijing" \
  --description "我的第一篇文章" \
  --date "2026-03-23" \
  --tags "开始,Montaigne" \
  --content-file /tmp/hello.md
```

## 详细文档

查看 [SKILL.md](SKILL.md) 获取完整的使用指南：
- 从零创建 Montaigne 网站
- 网站配置指南
- 元数据规范
- 故障排除

## 配置说明

配置文件位于 `config/config.json`（skill 目录下的 config 文件夹）：

```json
{
  "username": "your-username",
  "site_url": "https://your-username.montaigne.io",
  "folders": {
    "root": "your-username.montaigne.io",
    "categories": [
      {"name": "Blog"},
      {"name": "Life"}
    ]
  },
  "slug_rules": {
    "Blog": {
      "type": "pinyin",
      "max_length": 50
    },
    "Life": {
      "type": "date_diff",
      "base_date": "2020-01-01"
    },
    "default": {
      "type": "incremental",
      "start": 1
    }
  }
}
```

## Slug 生成方式

| 类型 | 说明 | 示例 |
|------|------|------|
| `incremental` | 递增数字 | `1`, `2`, `3`... |
| `date_diff` | 日期差（天数） | `1351` |
| `pinyin` | 拼音/英文标题 | `wo-de-wen-zhang` |
| `manual` | 手动输入 | 自定义 |

## 系统要求

- macOS（需要 Apple Notes）
- Python 3.7+
- 已配置 iCloud 的 Apple ID

## 命令参考

### 初始化配置
```bash
python3 scripts/setup.py              # 完整向导
python3 scripts/setup.py --quick      # 快速设置
```

### 创建笔记
```bash
python3 scripts/create_note.py \
  --folder "Blog" \
  --title "文章标题" \
  --location "Beijing" \
  --description "文章简介" \
  --date "2026-03-23" \
  --tags "标签1,标签2" \
  --content-file article.md
```

### 计算 Slug
```bash
python3 scripts/calc_slug.py --folder "Blog" --date "2026-03-23"
python3 scripts/calc_slug.py --type pinyin --title "我的文章"
```

### 管理配置
```bash
python3 scripts/config.py --show
python3 scripts/config.py --set-username "newname"
```

## 从旧版本迁移

如果你使用过 v1.x 版本，运行以下命令自动迁移配置：

```bash
python3 scripts/setup.py --migrate
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 相关链接

- [Montaigne 官网](https://montaigne.io)
- [Montaigne 文档](https://docs.montaigne.io)

---

## 致谢

感谢 [@podviaznikov](https://github.com/podviaznikov) 创造了 [Montaigne](https://montaigne.io) - 一个将 Apple Notes 变成网站的出色工具。

[English Documentation](README.md)
