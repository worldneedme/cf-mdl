import os
import requests
import sys

CF_API_TOKEN = os.environ.get("CF_API_TOKEN")
CF_ZONE_ID = os.environ.get("CF_ZONE_ID")

if not all([CF_API_TOKEN, CF_ZONE_ID]):
    print("Missing Cloudflare credentials!")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {CF_API_TOKEN}",
    "Content-Type": "application/json"
}

def update_dns(dns_name, target_ips):
    if not target_ips:
        print(f"No IPs to update for {dns_name}")
        return
    print(f"=== Updating {dns_name} with {len(target_ips)} IPs ===")
    print(f"Target IPs: {target_ips}")
    list_url = f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records?type=A&name={dns_name}"
    list_resp = requests.get(list_url, headers=headers).json()
    if list_resp.get("success"):
        for record in list_resp["result"]:
            requests.delete(f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records/{record['id']}", headers=headers)
            print(f"Deleted old record: {record['content']}")
    else:
        print("Failed to fetch current DNS records.")
        return

    for ip in target_ips:
        requests.post(f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records", headers=headers, json={
            "type": "A", "name": dns_name, "content": ip, "ttl": 60, "proxied": False
        })
        print(f"Created new record for IP: {ip}")
    print(f"Successfully updated {dns_name}\n")

# --- md1.020021.qzz.io -> API 1 (All IPs) ---
try:
    print("Fetching API 1 for md1...")
    resp1 = requests.get("https://ipdb.api.030101.xyz/?type=bestcf&country=true", timeout=15)
    ips1 = [line.strip() for line in resp1.text.strip().split('\n') if line.strip()][:5]
    update_dns("md1.020021.qzz.io", ips1)
except Exception as e:
    print(f"Error processing md1: {e}")

# --- md2.020021.qzz.io -> API 2 (All IPs) ---
try:
    print("Fetching API 2 for md2...")
    resp2 = requests.get("https://addressesapi.090227.xyz/CloudFlareYes", timeout=15)
    ips2 = []
    for line in resp2.text.strip().split('\n'):
        if line.strip():
            ip = line.split('#')[0].strip()
            if ip not in ips2:
                ips2.append(ip)
    ips2 = ips2[:5]
    update_dns("md2.020021.qzz.io", ips2)
except Exception as e:
    print(f"Error processing md2: {e}")
