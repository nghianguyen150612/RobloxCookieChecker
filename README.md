# 🍪 Cookie Checker

A fast and simple Roblox cookie checker with multi-threading, progress bar, and clean export system.

---

## 🚀 Features

- ⚡ Multi-threaded checking
- 🔁 Retry system (network-safe)
- 🧹 Auto remove duplicate cookies
- 📊 Progress bar with ETA
- 📁 Export results:
  - cookies/alive.txt
  - cookies/dead.txt
  - cookies/error.txt
- 💾 JSON output (result.json)
- 🖥 Clean terminal UI (auto clear)

---

## 📦 Usage

## ▶️ Option 1 — Use Prebuilt EXE (Recommended)

### 1. Download

- Go to Releases
- Download: CookieChecker.exe

---

### 2. Run

- Double-click CookieChecker.exe
- A menu will appear:

[1] Check cookies [2] View results [3] Exit

---

### 3. Check cookies

- Select option 1
- Choose your .txt cookie file
- Wait for the checking process

---

### 4. Results

After completion, files will be created:

cookies/  ├─ alive.txt  ├─ dead.txt  └─ error.txt  result.json

---

## 🧑‍💻 Option 2 — Run from Source

### 1. Install dependencies

pip install -r requirements.txt

---

### 2. Run

python main.py

---

## ⚠️ Notes

- The .exe may be flagged by antivirus (false positive from PyInstaller)
- Running too many threads may cause rate limits
- Use responsibly

---

## ⭐ Support

If you find this project useful, consider giving it a sta