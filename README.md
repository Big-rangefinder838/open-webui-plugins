# 🧩 Open WebUI Plugins

A curated collection of plugins for [Open WebUI](https://github.com/open-webui/open-webui) — tools, filters, pipes, and actions that extend your AI chat experience.

Each plugin is a standalone Python file you can paste directly into Open WebUI's workspace.

---

## Plugin Types

| Type | What it does | Where to install |
|------|-------------|-----------------|
| **Tools** | Give your model new capabilities it can call (web search, APIs, rendering) | Workspace → Tools |
| **Filters** | Transform messages before they reach the model or before they're shown to you | Admin Panel → Functions |
| **Pipes** | Custom model endpoints — proxy, merge, or create entirely new model behaviors | Admin Panel → Functions |
| **Actions** | Buttons that appear below messages for quick actions | Admin Panel → Functions |

---

## Plugins

### Tools

| Plugin | Description |
|--------|-------------|
| [Email Composer](tools/email_composer.py) | AI-powered email drafting with an interactive Rich UI card. Full rich text editing, To/CC/BCC chips, priority, download .eml, one-click send via mailto. |

### Filters

*Coming soon*

### Pipes

*Coming soon*

### Actions

*Coming soon*

---

## How to Install a Plugin

1. Open the plugin file and copy its contents
2. In Open WebUI, go to **Workspace → Tools** (or Functions, depending on the type)
3. Click **+ Create New**
4. Paste the code, click **Save**
5. Enable it for your model — done

---

## Contributing

Found a bug or have an idea? Open an issue.
