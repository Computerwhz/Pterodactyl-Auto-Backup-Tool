import requests
import time

# === CONFIGURATION ===
PANEL_URL = ""  
ADMIN_API_KEY = ""
CLIENT_API_KEY = ""

dry_run = False 

# === HEADERS ===
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

def get_all_server_ids():
    """Fetch all server IDs and identifiers using the Admin API"""
    servers = []
    page = 1
    while True:
        url = f"{PANEL_URL}/api/application/servers?page={page}"
        res = requests.get(url, headers=ADMIN_HEADERS)
        res.raise_for_status()
        data = res.json()
        for s in data['data']:
            servers.append({
                "id": s['attributes']['id'],
                "identifier": s['attributes']['identifier']
            })
        if data['meta']['pagination']['current_page'] >= data['meta']['pagination']['total_pages']:
            break
        page += 1
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

def delete_oldest_backup(identifier, backups):
    """Delete the oldest backup"""
    if not backups:
        return
    oldest = sorted(backups, key=lambda b: b['attributes']['created_at'])[0]
    uuid = oldest['attributes']['uuid']
    if dry_run:
        print(f"[DRY-RUN] Would delete backup {uuid} for server {identifier}")
    else:
        url = f"{PANEL_URL}/api/client/servers/{identifier}/backups/{uuid}"
        res = requests.delete(url, headers=CLIENT_HEADERS)
        if res.status_code == 204:
            print(f"[-] Deleted oldest backup {uuid} for server {identifier}")
        else:
            print(f"[!] Failed to delete backup: {res.status_code} {res.text}")

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


def main():
    servers = get_all_server_ids()
    if not servers:
        print("[!] No servers found.")
        return

    for s in servers:
        sid = s['id']
        identifier = s['identifier']
        try:
            admin_info = get_admin_server_details(sid)
            name = admin_info['name']
            backup_limit = admin_info.get('feature_limits', {}).get('backups', 0)

            print(f"\n[*] Server: '{name}' ({identifier}) | Backup limit: {backup_limit}")

            if backup_limit == 0:
                print(f"[!] Skipping '{name}': backup limit is 0")
                continue

            backups = get_backup_info(identifier)
            print(f"[i] '{name}' has {len(backups)} backups")

            if len(backups) >= backup_limit:
                delete_oldest_backup(identifier, backups)

            create_backup(identifier)

        except Exception as e:
            print(f"[!] Error processing server {identifier}: {e}")

if __name__ == "__main__":
    main()
    

