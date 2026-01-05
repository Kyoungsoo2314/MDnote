# MDnote - Lightweight Markdown Viewer

**One installer. Zero dependencies. Just works.**

---

## 📦 What You Get

### Single-File Installer
```
MDnote-Setup.exe  (8.5MB)
  ↓ Double-click to install
  ↓
  ✅ Executable copied
  ✅ Registry configured
  ✅ Start Menu shortcut
  ✅ README displayed
  ✅ Done!
```

---

## 🚀 Quick Build Guide

### Step 1: Build Executable
```bash
build.bat
```
Creates `dist/md_viewer.exe`

### Step 2: Create Installer
```bash
create_installer.bat
```
Creates `MDnote-Setup.exe` (ready to distribute!)

### Step 3: Test
```bash
MDnote-Setup.exe
```

That's it! 🎉

---

## 📂 Project Structure

```
031 - md viewer/
├── md_viewer.py              # Main application
├── md_viewer.ico             # App icon
├── create_icon.py            # Icon generator
│
├── build.bat                 # Build executable
├── create_installer.bat      # Create single-file installer
│
├── install_internal.bat      # Installation logic (for IExpress)
├── mdnote_installer.sed      # IExpress configuration
├── README.txt                # Post-install readme
│
├── install.bat               # Legacy installer (requires dist/)
├── uninstall.bat             # Uninstaller
├── requirements.txt          # Build dependencies
│
├── dist/                     # Build output
│   └── md_viewer.exe
│
└── mdnote-git/              # Git repository (ready to push)
    ├── All source files
    ├── README.md            # GitHub documentation
    ├── LICENSE              # MIT License
    └── .gitignore
```

---

## 🎯 Features

### Core
- ✅ **Edit & Save** markdown files (`Ctrl+E` to edit, `Ctrl+S` to save)
- ✅ Dark & Light themes (`Ctrl+T`)
- ✅ Font scaling (`Ctrl +/-/0`)
- ✅ Recent files (last 10)
- ✅ Status bar (lines/words/chars)
- ✅ Always on top option
- ✅ Auto-save settings
- ✅ Unsaved changes warning

### v3.0 New Features
- ✅ **Tab Support** - Open multiple files in tabs (`Ctrl+W` to close)
- ✅ **Folder Tree Sidebar** - Browse and open .md files (`Ctrl+Shift+O`)
- ✅ **Drag & Drop** - Drop .md files or folders to open
- ✅ **Tab Navigation** - `Ctrl+Tab` / `Ctrl+Shift+Tab`
- ✅ **Scroll Position Preserved** - Stay at same position when toggling edit mode

### Markdown Support
- H1-H6 headers
- Code blocks & inline code
- **Bold**, *italic*, ~~strikethrough~~
- Lists & checkboxes
- Blockquotes
- Horizontal rules

---

## 🛠️ For Developers

### Build Process

1. **Python Source** → PyInstaller → `md_viewer.exe`
2. **IExpress Packing**:
   ```
   md_viewer.exe
   + install_internal.bat
   + README.txt
   ↓
   MDnote-Setup.exe
   ```

### Why IExpress?

- ✅ Built into Windows
- ✅ No external dependencies
- ✅ Professional installer
- ✅ Single `.exe` output

---

## 📤 Distribution

### For End Users
Just share: `MDnote-Setup.exe`

### For GitHub
The `mdnote-git/` folder is ready:
```bash
cd mdnote-git
git add .
git commit -m "Initial commit: MDnote v2.0"
git remote add origin https://github.com/your-username/mdnote.git
git push -u origin main
```

---

## 🎨 Customization

### Change App Name
Edit in `md_viewer.py`:
- Line 4: Description
- Line 136: Window title
- Line 65: Settings folder

### Change Icon
1. Edit `create_icon.py`
2. Run: `python create_icon.py`
3. Rebuild: `build.bat`

### Change Themes
Edit color dictionaries in `md_viewer.py`:
- `DARK_THEME` (line 18)
- `LIGHT_THEME` (line 39)

---

## 📝 Version History

### v3.0 (2025-01-05) - Tab & Sidebar Update
- ✨ **NEW**: Tab support for multiple files
- ✨ **NEW**: Folder tree sidebar with .md file browser
- ✨ **NEW**: Drag & Drop support (requires `tkinterdnd2`)
- ✨ **NEW**: Tab navigation shortcuts (Ctrl+Tab, Ctrl+Shift+Tab)
- ✨ **NEW**: Middle-click to close tabs
- 🐛 **FIX**: Scroll position preserved when toggling edit mode
- 📦 Increased recent files limit (5 → 10)
- 🎨 UI redesigned with PanedWindow layout

### v2.1 (2025-12-12) - Edit & Save Feature
- ✨ **NEW**: Edit mode with Ctrl+E
- ✨ **NEW**: Save functionality with Ctrl+S
- ✨ **NEW**: Unsaved changes tracking (asterisk indicator)
- ✨ **NEW**: Save confirmation on exit
- ✨ Enhanced title bar with mode and save status

### v2.0 (2025-12-12) - MDnote Rebranding
- ✨ Renamed to MDnote
- ✨ Single-file installer (IExpress)
- ✨ Auto-show README after install
- ✨ Installation complete message
- 🐛 Fixed settings folder path

### v1.0 - Initial Release
- Basic Markdown rendering
- Dark theme only
- Manual installation

---

## 🤝 Contributing

See `mdnote-git/CONTRIBUTING.md`

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

Built with [Claude Code](https://claude.com/claude-code)

---

**Enjoy MDnote!** ⭐
