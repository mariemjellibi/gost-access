import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ========== CONFIG ==========
KEYCLOAK_URL = "http://localhost:8080"
MASTER_USER = "admin"
MASTER_PASS = "admin"
REALM = "company-demo"

# Ghost users that MUST be flagged:
GHOST_USERS = [
    {"username": "john_s", "role": "admin"},
    {"username": "ci-bot-v1", "role": "manage-realm"},
    {"username": "intern_2024", "role": None}  # no dangerous role, just old
]

# ========== GET ADMIN TOKEN ==========
print("🔑 Getting admin token...")
r = requests.post(f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token", data={
    "client_id": "admin-cli",
    "username": MASTER_USER,
    "password": MASTER_PASS,
    "grant_type": "password"
})
if r.status_code != 200:
    print("❌ Can't get admin token. Is Keycloak running?")
    exit(1)
TOKEN = r.json()["access_token"]
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
print("✅ Token obtained.\n")

# ========== FETCH ALL USERS ==========
print("📋 Fetching users in company-demo...")
users = requests.get(f"{KEYCLOAK_URL}/admin/realms/{REALM}/users", headers=HEADERS).json()
user_map = {u["username"]: u for u in users}
print(f"Found {len(users)} user(s): {', '.join(user_map.keys())}\n")

# ========== HELPER TO ADD ATTRIBUTE ==========
def add_attribute(user_id, key, value):
    # GET full user
    r = requests.get(f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}", headers=HEADERS)
    if r.status_code != 200:
        print(f"   ❌ Could not fetch user {user_id}")
        return False
    user = r.json()
    if "attributes" not in user:
        user["attributes"] = {}
    user["attributes"][key] = [value]
    r = requests.put(f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}", headers=HEADERS, json=user)
    if r.status_code in (200, 204):
        return True
    else:
        print(f"   ❌ Failed to update: {r.status_code}")
        return False

# ========== FIX EACH GHOST USER ==========
for ghost in GHOST_USERS:
    username = ghost["username"]
    if username not in user_map:
        print(f"⚠️  User '{username}' not found. Skipping.")
        continue
    user = user_map[username]
    uid = user["id"]
    print(f"🔧 Fixing {username} (id: {uid})...")

    # 1. Add old createdTimestamp attribute
    if add_attribute(uid, "createdTimestamp", "1672531200000"):
        print("   ✅ Old timestamp added.")

    # 2. Assign dangerous role if needed
    if ghost["role"]:
        # Fetch available realm roles
        roles_r = requests.get(f"{KEYCLOAK_URL}/admin/realms/{REALM}/roles", headers=HEADERS)
        if roles_r.status_code == 200:
            all_roles = {r["name"]: r for r in roles_r.json()}
            role_name = ghost["role"]
            if role_name in all_roles:
                role_obj = all_roles[role_name]
                # Check if user already has it
                user_roles_r = requests.get(f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{uid}/role-mappings/realm", headers=HEADERS)
                current_roles = [r["name"] for r in user_roles_r.json()] if user_roles_r.status_code == 200 else []
                if role_name not in current_roles:
                    # Assign role
                    assign_r = requests.post(
                        f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{uid}/role-mappings/realm",
                        headers=HEADERS,
                        json=[role_obj]
                    )
                    if assign_r.status_code in (200, 204):
                        print(f"   ✅ Assigned '{role_name}' role.")
                    else:
                        print(f"   ❌ Failed to assign role: {assign_r.status_code}")
                else:
                    print(f"   ✔️  Already has '{role_name}' role.")
            else:
                print(f"   ⚠️  Role '{role_name}' not found in realm roles. Please create it.")
        else:
            print("   ❌ Could not fetch realm roles.")
    print()

print("🚀 All fixes applied. Now run: python3 scanner.py")