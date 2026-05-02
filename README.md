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
- ⚙️ Configurable via config.json
- 🖥 Clean terminal UI (auto clear)

---

## 📸 Example Output

Checking █████████████████ 100% ALIVE: 15    DEAD: 42    ERROR: 3

---

# 📦 Usage

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

### 1. Clone repository

bash git clone https://github.com/YOUR_USERNAME/CookieChecker.git cd CookieChecker 

---

### 2. Install dependencies

bash pip install -r requirements.txt 

---

### 3. Run

bash python main.py 

---

## ⚙️ Configuration

A config.json file will be created automatically on first run.

Example:

json {   "network": {     "timeout": 10,     "retries": 3,     "retry_delay": 1   },   "performance": {     "threads": 10   },   "export": {     "txt": true,     "json": true   } } 

---

## 📁 Output Structure

cookies/  ├─ alive.txt  ├─ dead.txt  └─ error.txt  result.json

---

## ⚠️ Notes

- The .exe may be flagged by antivirus (false positive from PyInstaller)
- Do not run extremely high threads (may cause rate limit)
- Use responsibly

---

## ⭐ Support

If you like this project, consider giving it a s