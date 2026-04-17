import json
import time
import threading
import os
import requests
import zipfile
import tkinter as tk
from tkinter import filedialog

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from colorama import Fore, init

init(autoreset=True)

# ================= GLOBAL =================
CONFIG_FILE = "config.json"
DATA_FILE = "accounts.json"
CFT_DIR = "cft"
CHROME_EXE = os.path.join(CFT_DIR, "chrome-win64", "chrome.exe")

lock = threading.Lock()
progress_lock = threading.Lock()

completed = 0
total = 0


# ================= INIT =================
def init_files():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "max_threads": 1,
                "manual_timeout": 60,
                "retry_count": 1
            }, f, indent=4)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f, indent=4)


def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


# ================= CLEAR =================
def clear():
    os.system("cls" if os.name == "nt" else "clear")


# ================= DOWNLOAD CHROME =================
def download_chrome():
    if os.path.exists(CHROME_EXE):
        return CHROME_EXE

    os.makedirs(CFT_DIR, exist_ok=True)

    print(Fore.YELLOW + "[AUTO] Downloading Chrome for Testing...")

    url = "https://storage.googleapis.com/chrome-for-testing-public/147.0.7727.57/win64/chrome-win64.zip"
    zip_path = os.path.join(CFT_DIR, "chrome.zip")

    r = requests.get(url, stream=True)
    if r.status_code != 200:
        raise Exception("Download Chrome failed")

    total_size = int(r.headers.get('content-length', 0))
    downloaded = 0

    with open(zip_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
            downloaded += len(chunk)

            if total_size:
                percent = downloaded / total_size * 100
                print(f"\rDownloading: {percent:.1f}%", end="")

    print("\n[EXTRACT]...")

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(CFT_DIR)

    os.remove(zip_path)

    print(Fore.GREEN + "[DONE] Chrome ready")
    return CHROME_EXE


# ================= DRIVER =================
def create_driver():
    chrome_path = download_chrome()

    options = Options()
    options.binary_location = chrome_path

    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--mute-audio")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # HEADLESS (optional)
    # options.add_argument("--headless=new")

    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    # Selenium auto driver (QUAN TRỌNG)
    return webdriver.Chrome(options=options)


# ================= FILE PICKER =================
def pick_file():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    path = filedialog.askopenfilename(
        title="Select account file",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )

    root.destroy()
    return path


# ================= DATA =================
def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with lock:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)


# ================= PARSE =================
def parse_userpass(path):
    res = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                u, p = line.strip().split(":", 1)
                res.append({
                    "username": u,
                    "password": p,
                    "cookie": "",
                    "status": "no_cookie"
                })

    return res


# ================= LOGIN =================
def login_account(acc, config):
    driver = create_driver()
    driver.get("https://www.roblox.com/login")

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "login-username"))
        ).send_keys(acc["username"])

        driver.find_element(By.ID, "login-password").send_keys(acc["password"])
        driver.find_element(By.ID, "login-button").click()

    except Exception as e:
        print(Fore.RED + f"[ERROR] {acc['username']} login fail: {e}")
        driver.quit()
        return

    for _ in range(config["manual_timeout"]):
        if "home" in driver.current_url.lower():
            for c in driver.get_cookies():
                if c["name"] == ".ROBLOSECURITY":
                    acc["cookie"] = c["value"]
                    acc["status"] = "alive"
                    driver.quit()
                    return
        time.sleep(1)

    acc["status"] = "failed"
    driver.quit()


# ================= CHECK COOKIE =================
def check_cookie(acc):
    if not acc.get("cookie"):
        return False

    try:
        res = requests.get(
            "https://users.roblox.com/v1/users/authenticated",
            cookies={".ROBLOSECURITY": acc["cookie"]},
            timeout=10
        )

        if res.status_code == 200 and "id" in res.text:
            acc["status"] = "alive"
            return True
        else:
            acc["status"] = "dead"
            return False

    except:
        acc["status"] = "dead"
        return False


# ================= PROGRESS =================
def show_progress():
    percent = (completed / total) * 100 if total else 0
    bar = "█" * int(percent // 3) + "-" * (30 - int(percent // 3))
    print(Fore.CYAN + f"\r[{bar}] {completed}/{total} ({percent:.1f}%)", end="")


# ================= MULTI =================
def run_multi(accounts, config):
    global completed, total

    total = len(accounts)
    completed = 0

    sem = threading.Semaphore(config["max_threads"])

    def worker(acc):
        global completed
        with sem:
            if not check_cookie(acc):
                login_account(acc, config)

            with progress_lock:
                completed += 1
                show_progress()

    threads = []
    for acc in accounts:
        t = threading.Thread(target=worker, args=(acc,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("\n[DONE]")


# ================= TABLE =================
def color_status(status):
    if status == "alive":
        return Fore.GREEN + "ALIVE"
    elif status == "dead":
        return Fore.RED + "DEAD"
    elif status == "no_cookie":
        return Fore.YELLOW + "NO_COOKIE"
    elif status == "failed":
        return Fore.MAGENTA + "FAILED"
    return status


def view(data):
    print("\n" + "=" * 80)
    print(Fore.CYAN + f"{'ID':<5} {'USERNAME':<25} {'STATUS':<15}")
    print("=" * 80)

    for i, acc in enumerate(data):
        print(f"{i:<5} {acc['username']:<25} {color_status(acc['status']):<15}")

    print("=" * 80)


# ================= MENU =================
def menu():
    init_files()
    config = load_config()
    data = load_data()

    while True:
        clear()

        print(Fore.CYAN + "==== ROBLOX AUTO TOOL ====")
        print("1. Import & Run")
        print("2. View Table")
        print("3. Exit")

        c = input(">> ")

        clear()

        if c == "1":
            path = pick_file()
            if not path:
                continue

            accs = parse_userpass(path)
            run_multi(accs, config)

            data.extend(accs)
            save_data(data)

            input("Done...")

        elif c == "2":
            view(data)
            input("Press Enter...")

        elif c == "3":
            break


if __name__ == "__main__":
    menu()