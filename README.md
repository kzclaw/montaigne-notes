# Montaigne Notes

An automation tool for creating and managing [Montaigne](https://montaigne.io) website content through Apple Notes.

## Features

- 📝 **Automated Note Creation**: Generate Apple Notes that comply with Montaigne specifications from Markdown files
- 🔢 **Multiple Slug Generation Methods**: Support for incremental numbers, date difference, pinyin/English titles, and manual input
- 📁 **Flexible Configuration System**: Different folders can use different slug rules
- 🎨 **Automatic Metadata Generation**: Auto-fill location, description, date, tags, slug fields
- 🔒 **Optional Privacy Notice**: Support for automatically appending privacy statements at the end of each article

## Quick Start

### 1. Clone or Download

```bash
git clone https://github.com/yourusername/montaigne-notes.git
cd montaigne-notes
```

### 2. Run Setup Wizard

```bash
python3 scripts/setup.py
```

The wizard will guide you through:
- Setting up your Montaigne username
- Detecting Apple Notes folders
- Configuring content categories
- Choosing slug generation methods

### 3. Create Your First Note

```bash
# Prepare a Markdown file
echo "## Hello World

This is my first Montaigne article." > /tmp/hello.md

# Create the note
python3 scripts/create_note.py \
  --folder "Blog" \
  --title "Hello World" \
  --location "Beijing" \
  --description "My first article" \
  --date "2026-03-23" \
  --tags "getting-started,Montaigne" \
  --content-file /tmp/hello.md
```

## Detailed Documentation

See [SKILL.md](SKILL.md) for complete usage guide:
- Creating a Montaigne website from scratch
- Website configuration guide
- Metadata specifications
- Troubleshooting

## Configuration

Configuration file is located at `config/config.json` (in the config folder under the skill directory):

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

## Slug Generation Methods

| Type | Description | Example |
|------|-------------|---------|
| `incremental` | Incremental numbers | `1`, `2`, `3`... |
| `date_diff` | Days since base date | `1351` |
| `pinyin` | Pinyin/English title | `my-article-title` |
| `manual` | Manual input | Custom |

## System Requirements

- macOS (requires Apple Notes)
- Python 3.7+
- Apple ID with iCloud configured

## Command Reference

### Initialize Configuration
```bash
python3 scripts/setup.py              # Full wizard
python3 scripts/setup.py --quick      # Quick setup
```

### Create Note
```bash
python3 scripts/create_note.py \
  --folder "Blog" \
  --title "Article Title" \
  --location "Beijing" \
  --description "Article summary" \
  --date "2026-03-23" \
  --tags "tag1,tag2" \
  --content-file article.md
```

### Calculate Slug
```bash
python3 scripts/calc_slug.py --folder "Blog" --date "2026-03-23"
python3 scripts/calc_slug.py --type pinyin --title "My Article"
```

### Manage Configuration
```bash
python3 scripts/config.py --show
python3 scripts/config.py --set-username "newname"
```

## Migration from Old Versions

If you used v1.x, run the following to automatically migrate your configuration:

```bash
python3 scripts/setup.py --migrate
```

## Contributing

Issues and Pull Requests are welcome!

## License

MIT License

## Related Links

- [Montaigne Official Website](https://montaigne.io)
- [Montaigne Documentation](https://docs.montaigne.io)

---

## Acknowledgments

Thanks to [@podviaznikov](https://github.com/podviaznikov) for creating [Montaigne](https://montaigne.io) - a wonderful tool that turns Apple Notes into websites.

[中文文档](README.zh.md)
