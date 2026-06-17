import os
import requests
import sys

CF_API_TOKEN = os.environ.get("CF_API_TOKEN")
CF_ZONE_ID = os.environ.get("CF_ZONE_ID")
CF_DNS_NAME = os.environ.get("CF_DNS_NAME")

if not all([CF_API_TOKEN, CF_ZONE_ID, CF_DNS_NAME]):
    print("Missing Cloudflare credentials!")
    sys.exit(1)

# 1. Fetch IPs
try:
    resp = requests.get("https://ip.v2too.top/api/nodes", timeout=10)
    data = resp.json()
    
    # 2. Filter carrier == "cm" and sort by speed desc
    cm_nodes = [n for n in data if n.get("carrier") == "cm"]
    cm_nodes.sort(key=lambda x: x.get("speed", 0), reverse=True)
    
    # Take top 6
    top_6 = cm_nodes[:6]
    target_ips = [n.get("ip") for n in top_6 if n.get("ip")]
    
    print(f"Top 6 IPs: {target_ips}")
    
    if not target_ips:
        print("No valid IPs found.")
        sys.exit(1)
        
    # 3. Update Cloudflare
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Get current records
    list_url = f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records?type=A&name={CF_DNS_NAME}"
    list_resp = requests.get(list_url, headers=headers).json()
    
    if not list_resp.get("success"):
        print("Failed to fetch current DNS records.")
        sys.exit(1)
        
    current_records = list_resp["result"]
    
    # Delete old records
    for record in current_records:
        rec_id = record["id"]
        del_url = f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records/{rec_id}"
        requests.delete(del_url, headers=headers)
        print(f"Deleted old record: {record['content']}")
        
    # Create new records
    for ip in target_ips:
        create_url = f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records"
        payload = {
            "type": "A",
            "name": CF_DNS_NAME,
            "content": ip,
            "ttl": 60,
            "proxied": False
        }
        requests.post(create_url, headers=headers, json=payload)
        print(f"Created new record for IP: {ip}")
        
    print("DNS Update Completed Successfully!")

except Exception as e:
    print(f"Error occurred: {e}")
    sys.exit(1)
