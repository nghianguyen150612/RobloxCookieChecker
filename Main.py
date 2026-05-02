import requests
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.table import Table
from rich import box
from rich.progress import Progress, BarColumn, TimeRemainingColumn, TextColumn
from rich.panel import Panel
from rich.prompt import Prompt
from tkinter import Tk, filedialog

console = Console()

# =========================
# CLEAR TERMINAL
# =========================
def clear():
    os.system("cls" if os.name == "nt" else "clear")

# =========================
# DEFAULT CONFIG
# =========================
DEFAULT_CONFIG = {
    "network": {
        "timeout": 10,
        "retries": 3,
        "retry_delay": 1
    },
    "performance": {
        "threads": 10
    },
    "export": {
        "txt": True,
        "json": True
    }
}

# =========================
# CONFIG
# =========================
def load_config():
    if not os.path.exists("config.json"):
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        console.print("[yellow]Created config.json[/yellow]")
        return DEFAULT_CONFIG

    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

# =========================
# FILE PICKER
# =========================
def pick_file():
    root = Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="Select cookie file",
        filetypes=[("Text Files", "*.txt")]
    )

# =========================
# REMOVE DUPLICATES
# =========================
def remove_duplicates(cookies):
    original = len(cookies)
    unique = list(dict.fromkeys(cookies))
    removed = original - len(unique)
    return unique, removed

# =========================
# CHECK COOKIE
# =========================
def check_cookie(cookie, config):
    url = "https://users.roblox.com/v1/users/authenticated"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Cookie": f".ROBLOSECURITY={cookie}"
    }

    retries = config["network"]["retries"]
    timeout = config["network"]["timeout"]
    delay = config["network"]["retry_delay"]

    for attempt in range(retries + 1):
        try:
            res = requests.get(url, headers=headers, timeout=timeout)

            if res.status_code == 200:
                data = res.json()
                return {
                    "cookie": cookie,
                    "status": "ALIVE",
                    "userId": str(data.get("id")),
                    "username": data.get("name")
                }

            elif res.status_code == 401:
                return {"cookie": cookie, "status": "DEAD"}

            else:
                return {"cookie": cookie, "status": "UNKNOWN"}

        except requests.RequestException:
            if attempt < retries:
                time.sleep(delay)
            else:
                return {"cookie": cookie, "status": "ERROR"}

# =========================
# EXPORT TXT (IN FOLDER)
# =========================
def export_txt(results):
    os.makedirs("cookies", exist_ok=True)

    alive, dead, error = [], [], []

    for r in results:
        if r["status"] == "ALIVE":
            alive.append(r["cookie"])
        elif r["status"] == "DEAD":
            dead.append(r["cookie"])
        else:
            error.append(r["cookie"])

    def save(path, data):
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(data))

    save("cookies/alive.txt", alive)
    save("cookies/dead.txt", dead)
    save("cookies/error.txt", error)

    console.print("[green]Exported to /cookies folder[/green]")

# =========================
# MAIN CHECK FLOW
# =========================
def run_check(file_path, config):
    with open(file_path, "r", encoding="utf-8") as f:
        cookies = [line.strip() for line in f if line.strip()]

    cookies, removed = remove_duplicates(cookies)

    if removed > 0:
        console.print(f"[yellow]Removed {removed} duplicate cookies[/yellow]")

    results = []
    stats = {"ALIVE": 0, "DEAD": 0, "ERROR": 0, "UNKNOWN": 0}

    progress = Progress(
        TextColumn("[cyan]Checking"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn()
    )

    with progress:
        task = progress.add_task("check", total=len(cookies))

        with ThreadPoolExecutor(max_workers=config["performance"]["threads"]) as executor:
            futures = [executor.submit(check_cookie, c, config) for c in cookies]

            for future in as_completed(futures):
                result = future.result()
                results.append(result)

                stats[result["status"]] = stats.get(result["status"], 0) + 1
                progress.update(task, advance=1)

    if config["export"]["json"]:
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
        console.print("[green]Saved result.json[/green]")

    if config["export"]["txt"]:
        export_txt(results)

    console.print(Panel.fit(
        f"[green]ALIVE:[/green] {stats['ALIVE']}    "
        f"[red]DEAD:[/red] {stats['DEAD']}    "
        f"[yellow]ERROR:[/yellow] {stats['ERROR']}    "
        f"[white]UNKNOWN:[/white] {stats['UNKNOWN']}",
        title="Summary",
        border_style="cyan"
    ))

# =========================
# VIEW RESULTS
# =========================
def view_results():
    if not os.path.exists("result.json"):
        console.print("[red]No result.json found[/red]")
        return

    with open("result.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    table = Table(title="Cookie Results", box=box.DOUBLE_EDGE, show_lines=True)

    table.add_column("UserID", style="yellow")
    table.add_column("Username", style="cyan")
    table.add_column("Cookie", style="magenta")
    table.add_column("Status", justify="center")

    for item in data:
        cookie_short = item["cookie"][:30] + "..."

        status_color = {
            "ALIVE": "[bold green]ALIVE[/bold green]",
            "DEAD": "[bold red]DEAD[/bold red]",
            "ERROR": "[bold yellow]ERROR[/bold yellow]",
            "UNKNOWN": "[bold white]UNKNOWN[/bold white]"
        }

        table.add_row(
            item.get("userId", "-"),
            item.get("username", "-"),
            cookie_short,
            status_color.get(item["status"], "UNKNOWN")
        )

    console.print(table)

# =========================
# MENU
# =========================
def main():
    config = load_config()

    while True:
        clear()

        console.print(Panel.fit(
            "[1] Check cookies\n"
            "[2] View results\n"
            "[3] Exit",
            title="MAIN MENU",
            border_style="green"
        ))

        choice = Prompt.ask("Select option", choices=["1", "2", "3"])

        clear()

        if choice == "1":
            file_path = pick_file()
            if not file_path:
                console.print("[red]No file selected[/red]")
                input("Press Enter...")
                continue

            run_check(file_path, config)
            input("\nPress Enter to continue...")

        elif choice == "2":
            view_results()
            input("\nPress Enter to continue...")

        else:
            break


if __name__ == "__main__":
    main()