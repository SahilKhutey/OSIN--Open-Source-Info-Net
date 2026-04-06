# OSIN React Dashboard - File Copy Instructions

## ✅ How to Copy Files

Each component file is provided in the markdown documents. Follow these steps:

### Step 1: Setup Directories
```bash
python setup_react_dashboard.py
```

### Step 2: Install Dependencies
```bash
cd dashboard
npm install
```

### Step 3: Copy Files from Markdown

Files are organized in 2 markdown documents:

**Document 1: REACT_COMPONENT_FILES_PART1.md**
**Document 2: REACT_CSS_STYLES.md**

#### File Locations & Content Source

| File Path | Markdown Doc | Header | Lines |
|-----------|-------------|--------|-------|
| src/types/index.ts | PART1 | ## File: src/types/index.ts | 75 |
| src/store/useStore.ts | PART1 | ## File: src/store/useStore.ts | 68 |
| src/hooks/useWebSocket.ts | PART1 | ## File: src/hooks/useWebSocket.ts | 54 |
| src/components/EnhancedGlobe.tsx | PART1 | ## File: src/components/EnhancedGlobe.tsx | 107 |
| src/components/ThreatBar.tsx | PART1 | ## File: src/components/ThreatBar.tsx | 62 |
| src/components/SourcePanel.tsx | PART1 | ## File: src/components/SourcePanel.tsx | 54 |
| src/components/LiveFeed.tsx | PART1 | ## File: src/components/LiveFeed.tsx | 88 |
| src/components/Alerts.tsx | PART1 | ## File: src/components/Alerts.tsx | 67 |
| src/components/EventDetailModal.tsx | PART1 | ## File: src/components/EventDetailModal.tsx | 149 |
| src/components/EnhancedTerminal.tsx | PART1 | ## File: src/components/EnhancedTerminal.tsx | 170 |
| src/components/Dashboard.tsx | PART1 | ## File: src/components/Dashboard.tsx | 95 |
| src/App.tsx | PART1 | ## File: src/App.tsx | 68 |
| src/App.css | CSS | ## File: src/App.css | 1100+ |

---

## 📝 Detailed Copy Instructions

### For Each File:

1. **Open** the markdown document
2. **Find** the file section (marked with `## File: path/to/file.tsx`)
3. **Copy** the code between the typescript/css code fence (```typescript or ```css)
4. **Create** the file in its proper location
5. **Paste** the code
6. **Save** the file

---

## 🔍 Finding Sections in Markdown

### REACT_COMPONENT_FILES_PART1.md Structure:

```
# OSIN React Dashboard - Component Files

## File: src/types/index.ts
```typescript
... content ...
```

## File: src/store/useStore.ts
```typescript
... content ...
```

[12 more files...]
```

### REACT_CSS_STYLES.md Structure:

```
# OSIN React Dashboard - Complete CSS Stylesheet

## File: src/App.css
```css
... content ...
```
```

---

## ⚡ Quick Copy Method

Use your editor's Find/Replace or Quick Open:

### VS Code:
1. Press `Ctrl + K` then `Ctrl + O` to open file
2. Type `src/types/index.ts`
3. Create new file
4. Paste content from markdown

### Or Manual:
1. Create folder: `dashboard/src/types/`
2. Create file: `index.ts`
3. Copy-paste code from markdown

---

## ✨ Copy Order (Recommended)

**Phase 1: Types & Store (must be first)**
1. src/types/index.ts
2. src/store/useStore.ts
3. src/hooks/useWebSocket.ts

**Phase 2: Components (order doesn't matter)**
4. src/components/EnhancedGlobe.tsx
5. src/components/ThreatBar.tsx
6. src/components/SourcePanel.tsx
7. src/components/LiveFeed.tsx
8. src/components/Alerts.tsx
9. src/components/EventDetailModal.tsx
10. src/components/EnhancedTerminal.tsx
11. src/components/Dashboard.tsx

**Phase 3: App & Styling**
12. src/App.tsx
13. src/App.css

---

## 🎯 Verification Checklist

After copying all files, verify:

```bash
cd dashboard

# Check all files exist
ls -la src/
ls -la src/components/
ls -la src/hooks/
ls -la src/store/
ls -la src/types/

# Should show:
# src/App.tsx
# src/App.css
# src/main.tsx
# src/components/[8 files]
# src/hooks/[1 file]
# src/store/[1 file]
# src/types/[1 file]
```

---

## 🚀 After Copying: Install & Run

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Browser opens automatically or visit:
http://localhost:5173
```

---

## 🆘 If Files Won't Copy

### Option A: Use Copy Paste
1. Open markdown in browser or editor
2. Copy entire code block
3. Paste into file

### Option B: Manual Recreation
If copy-paste fails, the files are simple text—retype the key sections.

### Option C: Use Automated Script
Create a Python script to extract and write files:

```python
import re
import pathlib

markdown_file = "REACT_COMPONENT_FILES_PART1.md"

with open(markdown_file, 'r') as f:
    content = f.read()

# Find all file sections
pattern = r'## File: (src/\S+)\n\n```(?:typescript|css)\n(.*?)\n```'
matches = re.finditer(pattern, content, re.DOTALL)

for match in matches:
    filepath = match.group(1)
    code = match.group(2)
    
    pathlib.Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(code)
    
    print(f"✓ Created: {filepath}")
```

---

## 📊 File Size Reference

Expected sizes after copying:

| File | Lines | Size |
|------|-------|------|
| src/types/index.ts | 75 | ~2.5 KB |
| src/store/useStore.ts | 68 | ~2.2 KB |
| src/hooks/useWebSocket.ts | 54 | ~1.8 KB |
| src/components/EnhancedGlobe.tsx | 107 | ~3.5 KB |
| src/components/ThreatBar.tsx | 62 | ~2.1 KB |
| src/components/SourcePanel.tsx | 54 | ~1.8 KB |
| src/components/LiveFeed.tsx | 88 | ~2.9 KB |
| src/components/Alerts.tsx | 67 | ~2.2 KB |
| src/components/EventDetailModal.tsx | 149 | ~5.1 KB |
| src/components/EnhancedTerminal.tsx | 170 | ~5.7 KB |
| src/components/Dashboard.tsx | 95 | ~3.2 KB |
| src/App.tsx | 68 | ~2.3 KB |
| src/App.css | 1100+ | ~35 KB |
| **TOTAL** | **2,100+** | **~70 KB** |

---

## ✅ Common Issues

### "File not found" error
- Check path is correct
- Verify directories exist
- Use forward slashes (/) or backslashes (\) based on OS

### TypeScript errors after pasting
- Ensure no extra newlines at end
- Check no code fence markers (```) are included
- Run `npm run build` to see full errors

### CSS not loading
- Verify `src/App.css` is in correct location
- Check `src/App.tsx` imports it: `import './App.css'`
- Clear browser cache: Ctrl+Shift+Delete

---

## 🎉 Success Indicators

When done copying:

✅ All 16 files created
✅ No TypeScript errors
✅ Dashboard starts without errors
✅ Components render
✅ Styles load correctly

Run this to verify:
```bash
npm run build
```

If build succeeds → All files correct! ✨

---

## 📚 File Dependencies

Some files depend on others. Copy in this order:

```
types/index.ts
├── store/useStore.ts
├── hooks/useWebSocket.ts
└── components/
    ├── EnhancedGlobe.tsx ← depends on types
    ├── LiveFeed.tsx ← depends on types
    ├── Alerts.tsx ← depends on types & store
    ├── EventDetailModal.tsx ← depends on types
    ├── Dashboard.tsx ← depends on all components
    └── App.tsx ← depends on everything
```

**TL;DR:** Copy types first, everything else depends on it.

---

## 🎯 Next After Copying

1. ✅ Copy all files
2. ✅ Run `npm install`
3. ✅ Run `npm run dev`
4. 🌐 Open http://localhost:5173
5. 🎉 Dashboard is live!

---

Need help? All code is copy-paste ready from the markdown documents! 🚀
