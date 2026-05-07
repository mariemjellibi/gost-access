import requests
import random
from datetime import datetime, timezone, timedelta

KEYCLOAK_URL = "http://localhost:8080"
REALM = "company-demo"

def get_token():
    r = requests.post(f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token", data={
        "client_id": "admin-cli",
        "username": "admin",
        "password": "admin",
        "grant_type": "password"
    })
    r.raise_for_status()
    return r.json()["access_token"]

def create_user(token, username, days_ago=None, roles=[]):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Calculate fake createdTimestamp
    if days_ago:
        past = datetime.now(timezone.utc) - timedelta(days=days_ago)
        created_ts = int(past.timestamp() * 1000)
    else:
        created_ts = int(datetime.now(timezone.utc).timestamp() * 1000)

    user_data = {
        "username": username,
        "enabled": True,
        "attributes": {
            "createdTimestamp": [str(created_ts)]
        }
    }

    r = requests.post(f"{KEYCLOAK_URL}/admin/realms/{REALM}/users",
                      headers=headers, json=user_data)
    if r.status_code == 409:
        print(f"  already exists: {username}")
        return
    r.raise_for_status()
    print(f"  created: {username}")

    # Get the user ID
    search = requests.get(f"{KEYCLOAK_URL}/admin/realms/{REALM}/users?username={username}",
                          headers=headers)
    user_id = search.json()[0]["id"]

    # Assign roles
    for role_name in roles:
        role_resp = requests.get(f"{KEYCLOAK_URL}/admin/realms/{REALM}/roles/{role_name}",
                                 headers=headers)
        if role_resp.status_code == 200:
            role = role_resp.json()
            requests.post(f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}/role-mappings/realm",
                          headers=headers, json=[role])

# ── GHOST USERS (will be detected) ──────────────────────────────
ghosts = [
    ("dev.martinez",    400, ["admin"]),
    ("ci-pipeline-old", 300, ["manage-realm"]),
    ("vendor.ibrahim",  250, ["manage-users"]),
    ("staging-bot-v1",  180, ["admin"]),
    ("intern.chen",     90,  []),
]

# ── ACTIVE USERS (should NOT be detected) ───────────────────────
active = [
    ("alice.dev",       5,  []),
    ("bob.smith",       2,  []),
    ("carol.ops",       10, ["manage-users"]),
    ("david.sec",       1,  ["admin"]),
    ("emma.frontend",   7,  []),
    ("farid.backend",   3,  []),
    ("grace.devops",    14, []),
    ("hassan.cloud",    4,  []),
    ("iris.data",       6,  []),
    ("james.qa",        8,  []),
    ("karima.lead",     2,  ["admin"]),
    ("liam.sre",        9,  []),
    ("maya.infra",      11, []),
    ("nour.mobile",     5,  []),
    ("omar.api",        3,  []),
    ("paula.design",    7,  []),
    ("quinn.ml",        4,  []),
    ("rania.security",  6,  ["manage-realm"]),
    ("sam.platform",    12, []),
    ("talia.product",   1,  []),
]

print("Creating ghost users...")
token = get_token()
for username, days, roles in ghosts:
    create_user(token, username, days_ago=days, roles=roles)

print("\nCreating active users...")
for username, days, roles in active:
    create_user(token, username, days_ago=days, roles=roles)

print(f"\nDone. Total users: {len(ghosts) + len(active)}")
print(f"Expected ghosts: {len(ghosts)}")