---
name: montaigne-notes
description: "Create and manage Montaigne website content via Apple Notes. Automates the creation of blog posts with proper metadata (location, description, date, tags, slug) for Montaigne.io websites."
description_zh: "通过 Apple Notes 创建和管理 Montaigne 网站内容"
description_en: "Create and manage Montaigne website content via Apple Notes"
---

# Montaigne Notes

Montaigne Notes 是一个用于通过 Apple Notes 创建和管理 [Montaigne](https://montaigne.io) 网站内容的工具。它自动化了符合 Montaigne 规范的笔记创建流程，包括元数据表格生成、slug 计算和正文格式转换。

## 什么是 Montaigne？

Montaigne 是一个仅使用 Apple Notes 创建和发布网站的工具。核心价值：
- 无需编程知识，零门槛建站
- 数据源：Apple Notes（原生应用，跨设备同步）
- 发布方式：通过 iCloud 分享文件夹给 Montaigne
- 自动化：内容更新自动同步到网站

官方文档：https://docs.montaigne.io

---

## 适用场景

**当用户提到以下意图时使用此工具：**
- 「发布到 Montaigne 网站」
- 「创建 Montaigne 笔记」
- 「在 Apple Notes 里写博客」
- 「用 Montaigne 发文章」
- 「更新我的 Montaigne 网站」
- 任何涉及 Montaigne 网站内容管理的请求

---

## 从零创建 Montaigne 网站

### 完整建站流程

#### 步骤 1：注册 Montaigne 账号

1. 访问 https://montaigne.io
2. 点击 "Create your website"
3. 使用 Apple ID 登录
4. 选择网站用户名（如：john）
5. 获得网站地址：`https://john.montaigne.io`

#### 步骤 2：运行初始化向导

```bash
python3 scripts/setup.py
```

向导会引导你：
- 设置用户名
- 检测 Apple Notes 文件夹
- 配置内容分类
- 选择 slug 生成方式

#### 步骤 3：创建 Apple Notes 文件夹结构

在 Apple Notes 中创建以下文件夹：

```
{username}.montaigne.io/     ← 网站根文件夹（必须）
├── Blog/                    ← 博客文章（可选）
├── Life/                    ← 生活记录（可选）
├── Notes/                   ← 收集箱（可选）
└── Draft/                   ← 草稿（可选）
```

#### 步骤 4：创建网站首页（index）

在 `{username}.montaigne.io` 文件夹中创建 `index` 笔记：

```markdown
***

# index

***

name | value
---|---
emoji | 📝
title | 我的博客
layout | timeline
fontFamily | avenir
backgroundColor | #ffffff
textColor | #000000
linkColor | #1F64CC
openExternalLinksInNewTab | yes
showNoteNavigation | yes
showBreadcrumbs | yes

欢迎来到我的博客！这里记录我的思考、生活和技术分享。

***
```

#### 步骤 5：分享文件夹给 Montaigne

1. 在 Apple Notes 中右键点击 `{username}.montaigne.io` 文件夹
2. 选择 "共享文件夹"
3. 选择 "仅受邀用户" 或 "任何拥有链接的用户"
4. 权限选择 "可更改"（允许 Montaigne 读取内容）
5. 复制分享链接

#### 步骤 6：在 Montaigne 中连接文件夹

1. 访问 https://montaigne.io/dashboard
2. 粘贴 Apple Notes 的分享链接
3. Montaigne 会自动同步文件夹内容
4. 等待几分钟，网站即可访问

#### 步骤 7：创建第一篇内容

使用工具创建笔记：

```bash
# 创建正文文件
cat > /tmp/first_post.md << 'EOF'
## 我的第一篇博客

这是我的 Montaigne 网站的第一篇文章！

## 为什么选择 Montaigne

- 无需编程，零门槛建站
- 使用熟悉的 Apple Notes
- 自动同步，随时更新
EOF

# 创建笔记
python3 scripts/create_note.py \
  --folder "Blog" \
  --title "Hello Montaigne" \
  --location "Beijing" \
  --description "我的第一篇 Montaigne 博客文章" \
  --date "2026-03-23" \
  --tags "Montaigne,博客,开始" \
  --content-file /tmp/first_post.md
```

#### 步骤 8：验证网站

1. 访问 `https://{username}.montaigne.io`
2. 检查首页是否正常显示
3. 检查文章是否正确发布
4. 检查导航和链接是否正常

---

## 初始设置（已建站用户）

### 配置用户名

```bash
python3 scripts/config.py --set-username "your-username"
python3 scripts/config.py --show
```

配置将保存在 `config/config.json`（skill 目录下的 config 文件夹）。

---

## 核心功能

### 1. 创建 Montaigne 笔记

**完整命令：**
```bash
python3 scripts/create_note.py \
  --folder "Blog" \
  --title "文章标题" \
  --location "Beijing" \
  --description "文章简介" \
  --date "2026-03-22" \
  --tags "标签1,标签2,标签3" \
  --content-file /path/to/content.md
```

**参数说明：**

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `--folder` | 是 | 目标文件夹名 | `Blog`, `Life` |
| `--title` | 是 | 笔记标题 | `我的第一篇文章` |
| `--location` | 是 | 地点（英文） | `Beijing`, `Shanghai` |
| `--description` | 是 | 文章简介 | `关于思考的意义` |
| `--date` | 是 | 日期 YYYY-MM-DD | `2026-03-22` |
| `--tags` | 是 | 标签（逗号分隔） | `思考,成长,哲学` |
| `--content-file` | 是 | 正文 Markdown 文件路径 | `/tmp/article.md` |
| `--slug` | 否 | 指定 slug 值 | `my-first-post` |

### 2. Slug 计算方式

Slug 是 Montaigne 用于生成文章 URL 的标识符。支持多种生成方式：

**配置方式：**
```bash
python3 scripts/setup.py
```

**可选类型：**

| 类型 | 说明 | 示例 |
|------|------|------|
| **incremental** | 递增数字 | `1`, `2`, `3`... |
| **date_diff** | 日期差（从起始日期起的天数） | `1351` |
| **pinyin** | 拼音/英文标题 | `wo-de-wen-zhang` |
| **manual** | 手动输入 | 每次创建时指定 |

**不同文件夹可以配置不同的 slug 规则。**

### 3. 计算 Slug

```bash
# 根据配置自动计算
python3 scripts/calc_slug.py --folder "Blog" --date "2026-03-22"

# 强制指定类型
python3 scripts/calc_slug.py --type date_diff --date "2026-03-22" --base-date "2020-01-01"

# 拼音 slug
python3 scripts/calc_slug.py --type pinyin --title "我的文章标题"
```

### 4. 列出网站笔记

```bash
# 列出所有 Montaigne 文件夹
python3 scripts/list_folders.py

# 列出指定文件夹的笔记
python3 scripts/list_notes.py --folder "Blog"
```

### 5. 验证笔记格式

```bash
python3 scripts/validate.py --folder "Blog" --title "文章标题"
```

---

## 元数据规范

### 必填字段

所有 Montaigne 笔记必须包含以下元数据：

```markdown
name | value
---|---
location | Beijing
description | 文章简介
date | 2026-03-22
tags | 标签1 , 标签2 , 标签3
slug | 123
```

### 字段说明

| 字段 | 格式要求 | 示例 |
|------|---------|------|
| **location** | 英文，英文逗号分隔 | `Beijing`, `Beijing, Shanghai` |
| **description** | 一句话概括 | `关于思考的意义与价值` |
| **date** | YYYY-MM-DD | `2026-03-22` |
| **tags** | 英文逗号分隔 | `思考 , 成长 , 哲学` |
| **slug** | 数字或字符串 | `123` 或 `my-post` |

---

## 网站配置指南

### Metadata 配置（index 页面）

在 `{username}.montaigne.io` 文件夹中创建 `index` 笔记，用于配置整个网站的外观和行为。

**index 笔记示例：**
```markdown
***

# index

***

name | value
---|---
emoji | 📝
title | 我的博客
layout | timeline
fontFamily | avenir
backgroundColor | #ffffff
textColor | #000000
linkColor | #1F64CC
openExternalLinksInNewTab | yes
showNoteNavigation | yes
showBreadcrumbs | yes
hideFooterLinks | no
width | wide

欢迎来到我的博客！

***
```

### 常用配置属性

| 属性 | 说明 | 示例 |
|------|------|------|
| **emoji** | 网站 logo 和 favicon | `📝`, `🦞` |
| **title** | 网站标题 | `我的博客` |
| **layout** | 布局方式 | `timeline`, `list`, `grid`, `table` |
| **fontFamily** | 字体 | `helvetica`, `avenir`, `georgia` |
| **fontSize** | 字体大小 | `16px`, `18px` |
| **backgroundColor** | 背景颜色 | `#ffffff`, `#f5f5f5` |
| **textColor** | 主文本颜色 | `#000000`, `#333333` |
| **linkColor** | 链接颜色 | `#1F64CC`, `#0066cc` |
| **width** | 布局宽度 | `wide`（占满页面）, `none`（默认） |
| **openExternalLinksInNewTab** | 外部链接新标签页打开 | `yes`, `no` |
| **showNoteNavigation** | 显示笔记导航 | `yes`, `no` |
| **showBreadcrumbs** | 显示面包屑导航 | `yes`, `no` |
| **hideFooterLinks** | 隐藏页脚链接 | `yes`, `no` |
| **hideHeader** | 隐藏页眉 | `yes`, `no` |

### 布局选项

| 布局 | 说明 | 适用场景 |
|------|------|---------|
| **timeline** | 时间线视图（默认） | 博客、日记 |
| **list** | 列表视图 | 文章列表 |
| **grid** | 网格视图 | 作品集、图片展示 |
| **table** | 表格视图 | 数据展示、对比 |

### 字体选项

| 字体 | 说明 |
|------|------|
| **helvetica** | Helvetica（默认） |
| **avenir** | Avenir（苹果设计字体） |
| **georgia** | Georgia（衬线字体，适合阅读） |
| **times** | Times New Roman |
| **sans-serif** | 系统无衬线字体 |

### 文件夹级配置

每个文件夹可以有自己的 `index` 笔记，用于配置该文件夹的展示方式。

**示例：Blog 文件夹的 index**
```markdown
***

# index

***

name | value
---|---
layout | list
title | 技术博客
emoji | 💻

这里收录我的技术文章。

***
```

### 导航菜单配置

在 index 笔记中添加 `links` 属性创建顶部导航菜单：

```markdown
name | value
---|---
emoji | 📝
title | 我的博客
layout | timeline
links | [首页](/) , [关于](/about) , [GitHub](https://github.com/username)
```

### 预览属性配置

使用 `previewProps` 自定义列表页显示的信息：

```markdown
name | value
---|---
previewProps | date, author, tags
```

这会在文章列表中显示日期、作者和标签。

---

## 正文格式规范

### 支持的 Markdown 语法

工具会自动将 Markdown 转换为 Apple Notes 兼容的 HTML：

| Markdown | 转换结果 |
|---------|---------|
| `## 标题` | 加粗标题 + 段落分隔 |
| `- 列表项` | `→ 列表项` |
| `**粗体**` | 粗体文本 |
| 空行 | 段落分隔 |

### 示例正文文件

```markdown
## 核心观点

思考是人类区别于动物的重要特征。

## 思考的价值

- 帮助我们理解世界
- 指导我们的行动
- 促进个人成长

思考的过程比结果更重要。
```

---

## 完整工作流示例

### 场景：发布一篇博客文章

**步骤 1：准备正文文件**

```bash
cat > /tmp/my_article.md << 'EOF'
## 为什么选 Montaigne？

我想搭建一个个人博客，但不想折腾域名、服务器、部署。

## 搭建过程

### 第一步：创建文件夹

在 Apple Notes 创建一个 "Blog" 文件夹。

### 第二步：填写元数据

每篇文章需要 6 个字段。

### 第三步：分享文件夹

右键文件夹，选择"共享"。

## 总结

用 Apple Notes 搭网站比想象中简单！
EOF
```

**步骤 2：创建笔记**

```bash
python3 scripts/create_note.py \
  --folder "Blog" \
  --title "如何用 Apple Notes 零代码创建网站" \
  --location "Beijing" \
  --description "记录用 Montaigne 搭建网站的全过程" \
  --date "2026-03-22" \
  --tags "Montaigne,Apple Notes,自动化" \
  --content-file /tmp/my_article.md
```

**步骤 3：验证结果**

```bash
# 查看笔记列表
python3 scripts/list_notes.py --folder "Blog"
```

---

## 隐私设置（可选）

如果需要在每篇文章末尾添加隐私提示或身份声明，可以在初始化时配置：

```bash
python3 scripts/setup.py
```

在隐私设置步骤中输入提示文本，创建笔记时会自动附加到文章末尾。

---

## 文件限制

| 文件类型 | 最大大小 |
|---------|---------|
| 图片 | 50MB |
| 音频 | 100MB |
| 视频 | 100MB |

---

## 故障排除

### 问题：找不到 Montaigne 文件夹

**解决：**
```bash
# 检查配置
python3 scripts/config.py --show

# 手动指定文件夹路径
python3 scripts/create_note.py \
  --folder "username.montaigne.io/Blog" \
  ...
```

### 问题：笔记格式不正确

**解决：**
```bash
# 验证笔记格式
python3 scripts/validate.py \
  --folder "Blog" \
  --title "文章标题"
```

### 问题：Slug 计算错误

**解决：**
- 确认 `--date` 格式为 YYYY-MM-DD
- 检查文件夹的 slug 规则配置
- 使用 `--slug` 手动指定

---

## 参考资源

- **Montaigne 官方文档**：https://docs.montaigne.io
- **Montaigne 主页**：https://montaigne.io

---

*版本：v2.0.0*
*最后更新：2026-03-23*
