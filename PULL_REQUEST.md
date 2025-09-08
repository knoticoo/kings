# Pull Request: Discord Text Auto-Formatting for Guides

## 🎯 Overview
This PR implements automatic Discord text formatting for the King's Choice Management app guides system, making it easy to convert Discord markdown to properly formatted HTML guides.

## ✨ Features Added

### 1. Discord Text Auto-Formatter
- **New file**: `static/js/discord-formatter.js`
- Automatically detects and converts Discord markdown to HTML
- Supports tier list formatting (EX+, EX, SSS, S, A, B, C, F)
- Converts bold, italic, code, and header formatting
- Auto-converts list items to proper HTML lists

### 2. Simplified Guide Interface
- **Removed search bar** from guides list page
- **Removed Related Guides section** from guide view
- **Removed Guide Information sidebar** from guide view
- **Full-width layout** for guide content (col-12)
- Cleaner, more focused user experience

### 3. Enhanced Guide Editor
- Updated both add and edit guide templates
- Added Discord formatting instructions
- Auto-format button for manual formatting
- Paste detection for automatic formatting

## 🔧 Technical Changes

### Files Modified:
- `templates/guides/admin/add.html` - Enhanced with Discord formatting UI
- `templates/guides/admin/edit.html` - Enhanced with Discord formatting UI  
- `templates/guides/list.html` - Removed search bar
- `templates/guides/view.html` - Removed sidebar, full-width layout

### Files Added:
- `static/js/discord-formatter.js` - Core Discord formatting functionality
- `create_intellect_tier_list.py` - Sample script for creating tier list guides

## 🎮 Discord Format Support

The formatter automatically converts:

| Discord Format | HTML Output |
|----------------|-------------|
| `**bold**` | **bold** |
| `*italic*` | *italic* |
| `` `code` `` | `code` |
| `# Header` | <h1>Header</h1> |
| `` `EX+` `` | <h2>**EX+**</h2> |
| `- Item` | <ul><li>Item</li></ul> |

## 📝 Example Usage

**Input (Discord text):**
```
# **`INTELLECT TIER KNIGHT LIST`**

`EX+`
- Joan of Arc

`EX`  
- Queen Elizabeth
```

**Output (Auto-formatted HTML):**
```html
<h1><strong>INTELLECT TIER KNIGHT LIST</strong></h1>

<h2><strong>EX+</strong></h2>
<ul>
<li>Joan of Arc</li>
</ul>

<h2><strong>EX</strong></h2>
<ul>
<li>Queen Elizabeth</li>
</ul>
```

## 🚀 How to Use

1. Go to **Add Guide** or **Edit Guide**
2. **Paste Discord text** in the content area
3. Text is **automatically formatted** to HTML
4. Click **"Format Discord Text"** button for manual formatting
5. Save the guide with properly formatted content

## 🎨 UI Improvements

- **Cleaner guide list** without search clutter
- **Full-width guide view** for better content reading
- **Simplified sidebar** with focused Discord formatting tips
- **Auto-formatting feedback** with success messages

## 🧪 Testing

The formatter has been tested with:
- ✅ Tier list formatting (EX+, EX, SSS, S, A, B, C, F)
- ✅ Bold and italic text conversion
- ✅ Code block formatting
- ✅ Header conversion (#, ##, ###)
- ✅ List item conversion (- items)
- ✅ Mixed content formatting

## 📋 Checklist

- [x] Discord text auto-formatting implemented
- [x] Search bar removed from guides list
- [x] Related guides section removed
- [x] Guide information sidebar removed
- [x] Full-width layout implemented
- [x] Guide editor enhanced with formatting UI
- [x] Auto-format button added
- [x] Paste detection implemented
- [x] Success/error messaging added
- [x] Documentation updated

## 🔗 Related Issues

This PR addresses the need for easy Discord text formatting in the King's Choice Management app, specifically for creating tier list guides from Discord content.

---

**Repository**: `knoticoo/kings`  
**Branch**: `cursor/organize-game-guide-text-automatically-fbf3`  
**Target**: `main`