import requests
import time
import json
import os
import tkinter as tk
from tkinter import messagebox

# === CONFIGURATION ===
CONFIG_FILE = "config.json"

dry_run = False  # default fallback; overridden by config
PANEL_URL = ""
ADMIN_API_KEY = ""
CLIENT_API_KEY = ""
auto_delete_locked_backups = -1  # -1=ask, 1=auto delete next unlocked, 0=skip backup creation

# === HEADERS (initialized after loading config) ===
ADMIN_HEADERS = {}
CLIENT_HEADERS = {}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

# Global config loaded once
user_config = load_config()

def apply_config():
    global dry_run, PANEL_URL, ADMIN_API_KEY, CLIENT_API_KEY, auto_delete_locked_backups
    global ADMIN_HEADERS, CLIENT_HEADERS

    PANEL_URL = user_config.get("panel_url", "").rstrip("/")
    ADMIN_API_KEY = user_config.get("admin_api_key", "")
    CLIENT_API_KEY = user_config.get("client_api_key", "")
    dry_run = user_config.get("dry_run", False)
    auto_delete_locked_backups = user_config.get("auto_delete_locked_backups", -1)

    ADMIN_HEADERS = {
        "Authorization": f"Bearer {ADMIN_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    CLIENT_HEADERS = {
        "Authorization": f"Bearer {CLIENT_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

apply_config()

def ask_user_to_delete_next(server_name):
    # Use config if set to auto yes or no
    if auto_delete_locked_backups in (0,1):
        return auto_delete_locked_backups == 1

    response = {"choice": None}

    def on_yes():
        response["choice"] = True
        if remember_var.get():
            user_config["auto_delete_locked_backups"] = 1
            save_config(user_config)
            apply_config()
        popup.destroy()

    def on_no():
        response["choice"] = False
        if remember_var.get():
            user_config["auto_delete_locked_backups"] = 0
            save_config(user_config)
            apply_config()
        popup.destroy()

    popup = tk.Toplevel()
    popup.title("Backup Locked")

    label = tk.Label(popup, text=f"The oldest backup for '{server_name}' is locked or can't be deleted.\nDelete the next available backup?")
    label.pack(padx=20, pady=10)

    remember_var = tk.BooleanVar()
    remember_chk = tk.Checkbutton(popup, text="Always choose this option", variable=remember_var)
    remember_chk.pack()

    btn_frame = tk.Frame(popup)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Yes", width=10, command=on_yes).pack(side="left", padx=5)
    tk.Button(btn_frame, text="No", width=10, command=on_no).pack(side="right", padx=5)

    popup.grab_set()
    popup.wait_window()

    return response["choice"]

def get_all_server_ids():
    """Fetch all server IDs and identifiers using the Admin API"""
    if not PANEL_URL or not ADMIN_API_KEY:
        return []

    servers = []
    page = 1
    try:
        while True:
            url = f"{PANEL_URL}/api/application/servers?page={page}"
            res = requests.get(url, headers=ADMIN_HEADERS)
            if res.status_code == 404:
                break
            res.raise_for_status()
            data = res.json()
            for s in data.get('data', []):
                servers.append({
                    "id": s['attributes']['id'],
                    "identifier": s['attributes']['identifier']
                })
            if data['meta']['pagination']['current_page'] >= data['meta']['pagination']['total_pages']:
                break
            page += 1
    except Exception as e:
        print(f"[!] Error fetching servers: {e}")
    return servers

def get_admin_server_details(server_id):
    """Use Admin API to get full details including feature_limits"""
    url = f"{PANEL_URL}/api/application/servers/{server_id}"
    res = requests.get(url, headers=ADMIN_HEADERS)
    res.raise_for_status()
    return res.json()['attributes']

def get_backup_info(identifier):
    """List backups using Client API"""
    url = f"{PANEL_URL}/api/client/servers/{identifier}/backups"
    res = requests.get(url, headers=CLIENT_HEADERS)
    if res.status_code == 200:
        return res.json()['data']
    print(f"[!] Could not fetch backups for {identifier}: {res.status_code}")
    return []

def delete_oldest_backup(identifier, backups, server_name=""):
    """Delete the oldest *deletable* backup, prompting the user if needed"""
    if not backups:
        return

    # Sort by creation time ascending (oldest first)
    sorted_backups = sorted(backups, key=lambda b: b['attributes']['created_at'])

    for backup in sorted_backups:
        uuid = backup['attributes']['uuid']
        is_locked = backup['attributes'].get('is_locked', False)

        if is_locked:
            user_agrees = ask_user_to_delete_next(server_name)
            if not user_agrees:
                print(f"[-] Skipping deletion for {identifier}")
                return
            continue  # try next backup

        # Attempt to delete
        if dry_run:
            print(f"[DRY-RUN] Would delete backup {uuid} for server {identifier}")
            return
        else:
            url = f"{PANEL_URL}/api/client/servers/{identifier}/backups/{uuid}"
            res = requests.delete(url, headers=CLIENT_HEADERS)
            if res.status_code == 204:
                print(f"[-] Deleted backup {uuid} for server {identifier}")
                return
            else:
                print(f"[!] Failed to delete backup: {res.status_code} {res.text}")
                # Ask again if want to try next?
                user_agrees = ask_user_to_delete_next(server_name)
                if not user_agrees:
                    return

def create_backup(identifier):
    """Create a new backup"""
    name = f"AutoBackup-{time.strftime('%Y%m%d-%H%M%S')}"
    if dry_run:
        print(f"[DRY-RUN] Would create backup named '{name}' for server {identifier}")
    else:
        url = f"{PANEL_URL}/api/client/servers/{identifier}/backups"
        data = {"name": name, "ignored": "", "is_locked": False}
        res = requests.post(url, headers=CLIENT_HEADERS, json=data)
        if res.status_code in [200, 201]:
            backup = res.json()
            name = backup['attributes']['name']
            print(f"[+] Backup '{name}' was created for server {identifier} (status: pending)")
        else:
            print(f"[!] Failed to create backup: {res.status_code} {res.text}")

def options_window(root):
    win = tk.Toplevel(root)
    win.title("Options")

    tk.Label(win, text="Panel URL:").pack(anchor="w", padx=10, pady=(10, 0))
    panel_var = tk.StringVar(value=user_config.get("panel_url", ""))
    panel_entry = tk.Entry(win, textvariable=panel_var, width=50)
    panel_entry.pack(padx=10)

    tk.Label(win, text="Admin API Key:").pack(anchor="w", padx=10, pady=(10, 0))
    admin_var = tk.StringVar(value=user_config.get("admin_api_key", ""))
    admin_entry = tk.Entry(win, textvariable=admin_var, show="*", width=50)
    admin_entry.pack(padx=10)

    tk.Label(win, text="Client API Key:").pack(anchor="w", padx=10, pady=(10, 0))
    client_var = tk.StringVar(value=user_config.get("client_api_key", ""))
    client_entry = tk.Entry(win, textvariable=client_var, show="*", width=50)
    client_entry.pack(padx=10)

    dry_run_var = tk.BooleanVar(value=user_config.get("dry_run", False))
    dry_chk = tk.Checkbutton(win, text="Dry run (no changes)", variable=dry_run_var)
    dry_chk.pack(anchor="w", padx=10, pady=(10, 0))

    tk.Label(win, text="If the oldest backup can't be deleted:").pack(anchor="w", padx=10, pady=(10, 0))
    auto_delete_var = tk.IntVar(value=user_config.get("auto_delete_locked_backups", -1))
    frame_radio = tk.Frame(win)
    frame_radio.pack(anchor="w", padx=20)

    tk.Radiobutton(frame_radio, text="Ask every time", variable=auto_delete_var, value=-1).pack(anchor="w")
    tk.Radiobutton(frame_radio, text="Automatically delete next available backup", variable=auto_delete_var, value=1).pack(anchor="w")
    tk.Radiobutton(frame_radio, text="Skip backup creation", variable=auto_delete_var, value=0).pack(anchor="w")

    def save_and_close():
        user_config["panel_url"] = panel_var.get().strip()
        user_config["admin_api_key"] = admin_var.get().strip()
        user_config["client_api_key"] = client_var.get().strip()
        user_config["dry_run"] = dry_run_var.get()
        user_config["auto_delete_locked_backups"] = auto_delete_var.get()
        save_config(user_config)
        apply_config()
        win.destroy()

    btn_save = tk.Button(win, text="Save", command=save_and_close)
    btn_save.pack(pady=10)

def start_UI():
    root = tk.Tk()
    root.title("Pterodactyl Backup Tool")

    # Buttons frame (top)
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    btn_options = tk.Button(btn_frame, text="Options", command=lambda: options_window(root))
    btn_options.pack(side="left", padx=5)

    btn_backup = tk.Button(btn_frame, text="Start Backup", command=lambda: start_backup(root))
    btn_backup.pack(side="left", padx=5)

    servers = []
    check_vars = []  # List of (label, BooleanVar, checkbox_widget)

    # Fetch servers
    server_list = get_all_server_ids()
    if not server_list:
        # no servers or config missing
        label = tk.Label(root, text="No servers found or API not configured.")
        label.pack(pady=20)
    else:
        for serverid in server_list:
            try:
                server_details = get_admin_server_details(server_id=serverid['id'])
                name = server_details.get("name", "Unknown Server")
                backups_limit = server_details.get("feature_limits", {}).get("backups", 0)
                display_text = f"{name} ({serverid['identifier']})"
                servers.append((display_text, backups_limit))
            except Exception as e:
                print(f"[!] Could not get details for server {serverid['id']}: {e}")
                servers.append((f"Server {serverid['identifier']} (details error)", 0))

        # Frame for checkboxes
        checkbox_frame = tk.Frame(root)
        checkbox_frame.pack()

        if servers:
            # "Select All" checkbox variable
            select_all_var = tk.BooleanVar()

            def toggle_all():
                new_state = select_all_var.get()
                for _, var, chk in check_vars:
                    if chk['state'] != 'disabled':
                        var.set(new_state)

            # Add "Select All" checkbox
            select_all_chk = tk.Checkbutton(checkbox_frame, text="Select All", variable=select_all_var, command=toggle_all)
            select_all_chk.pack(anchor="w")

            # Add individual server checkboxes
            for server, backups_limit in servers:
                var = tk.BooleanVar()
                chk = tk.Checkbutton(checkbox_frame, text=server, variable=var)
                if backups_limit == 0:
                    chk.configure(state="disabled")
                    # Optional: add a tooltip or a suffix label explaining why disabled
                    # Here just appending " (No backups allowed)" to text
                    chk.configure(text=server + " (Backups disabled)")
                chk.pack(anchor="w")
                check_vars.append((server, var, chk))

        else:
            label = tk.Label(root, text="No servers available.")
            label.pack(pady=20)

    def show_selected():
        selected = [name for name, var, chk in check_vars if var.get()]
        if not selected:
            messagebox.showinfo("No Selection", "Please select at least one server to backup.")
            return

        # Map display names back to identifiers (by extracting between parentheses)
        selected_ids = []
        for display_name in selected:
            # Example: "ServerName (identifier)" or "ServerName (identifier) (Backups disabled)"
            # Strip suffix if present
            clean_name = display_name.split(" (Backups disabled)")[0]
            if "(" in clean_name and clean_name.endswith(")"):
                identifier = clean_name.split("(")[-1][:-1]
                selected_ids.append(identifier)
        root.selected_ids = selected_ids  # save for backup process
        run_backup_process(root)

    def start_backup(root):
        show_selected()

    def run_backup_process(root):
        selected = getattr(root, "selected_ids", [])
        if not selected:
            return
        for identifier in selected:
            print(f"Backing up server {identifier} ...")
            backups = get_backup_info(identifier)
            delete_oldest_backup(identifier, backups, server_name=identifier)
            create_backup(identifier)
        messagebox.showinfo("Backup Complete", "Backup process completed.")

    root.mainloop()

def main():
    start_UI()

if __name__ == "__main__":
    main()
