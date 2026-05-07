import requests, os

TOKEN = os.getenv("TOKEN")
BASE = "http://localhost:8080/admin/realms/company-demo"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

USERS = [
    ("97a1b579-0574-420c-bc29-6de265ced90c", "john_s"),
    ("8da991e4-dff0-4b26-8e65-3bb83ae57995", "ci-bot-v1"),
    ("dd9832bb-7d1e-4706-9701-7e309c2a6a53", "intern_2024")
]

for uid, name in USERS:
    r = requests.get(f"{BASE}/users/{uid}", headers=HEADERS)
    if r.status_code != 200:
        print(f"❌ Failed to get {name}")
        continue
    user = r.json()
    user.setdefault("attributes", {})["createdTimestamp"] = ["1672531200000"]
    r = requests.put(f"{BASE}/users/{uid}", headers=HEADERS, json=user)
    if r.status_code in (200, 204):
        print(f"✅ Added old timestamp to {name}")
    else:
        print(f"❌ Update failed for {name}: {r.status_code}")