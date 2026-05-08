import os, requests
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv()

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
REALM = os.getenv("KEYCLOAK_REALM")

# Simulated creation dates for ghost users (days ago)
GHOST_AGE_OVERRIDE = {
    "dev.martinez":    400,
    "ci-pipeline-old": 300,
    "vendor.ibrahim":  250,
    "staging-bot-v1":  180,
    "intern.chen":     90,
}

def get_token():
    r = requests.post(f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token", data={
        "client_id": "admin-cli",
        "username": "admin",
        "password": "admin",
        "grant_type": "password"
    })
    r.raise_for_status()
    return r.json()["access_token"]

def get_users(token):
    headers = {"Authorization": f"Bearer {token}"}
    list_resp = requests.get(f"{KEYCLOAK_URL}/admin/realms/{REALM}/users", headers=headers)
    list_resp.raise_for_status()
    user_summaries = list_resp.json()
    full_users = []
    for summary in user_summaries:
        uid = summary["id"]
        user_resp = requests.get(f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{uid}", headers=headers)
        if user_resp.status_code == 200:
            full_users.append(user_resp.json())
        else:
            full_users.append(summary)
    return full_users

def get_roles(token, user_id):
    r = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}/role-mappings/realm",
        headers={"Authorization": f"Bearer {token}"}
    )
    r.raise_for_status()
    return [role["name"] for role in r.json()]

def is_ghost(user, roles):
    now = datetime.now(timezone.utc)
    username = user.get("username")
    last_login = user.get("lastLogin")

    # Use override for known ghosts, otherwise use Keycloak's real createdTimestamp
    if username in GHOST_AGE_OVERRIDE:
        days_old = GHOST_AGE_OVERRIDE[username]
        created = int((now - timedelta(days=days_old)).timestamp() * 1000)
    else:
        created = user.get("createdTimestamp")

    reasons = []

    # Check inactivity / never logged in
    if last_login:
        if (now - datetime.fromtimestamp(last_login / 1000, tz=timezone.utc)).days > 60:
            reasons.append("Inactive > 60 days")
    elif created:
        if (now - datetime.fromtimestamp(created / 1000, tz=timezone.utc)).days > 60:
            reasons.append("Never logged in & account older than 60 days")

    # Check dangerous roles — only flag if account is genuinely old
    dangerous = {"admin", "manage-realm"}
    if any(r in dangerous for r in roles):
        if last_login and (now - datetime.fromtimestamp(last_login / 1000, tz=timezone.utc)).days > 30:
            reasons.append("Dangerous role with no recent activity")
        elif not last_login and created and (now - datetime.fromtimestamp(created / 1000, tz=timezone.utc)).days > 60:
            reasons.append("Dangerous role with no recent activity")

    if not reasons:
        return None

    # Determine risk level
    if "Dangerous role" in " ".join(reasons) or len(reasons) >= 2:
        risk = "Critical"
    elif "never logged in" in " ".join(reasons).lower():
        risk = "High"
    else:
        risk = "Low"

    return {
        "user_id": user["id"],
        "username": username,
        "last_login": last_login,
        "roles": roles,
        "risk_level": risk,
        "reasons": reasons
    }

def scan():
    token = get_token()
    ghosts = []
    for u in get_users(token):
        roles = get_roles(token, u["id"])
        ghost = is_ghost(u, roles)
        if ghost:
            ghosts.append(ghost)
    return ghosts

if __name__ == "__main__":
    ghosts = scan()
    print(f"\nScanned {26} identities — {len(ghosts)} ghost(s) found\n")
    for g in ghosts:
        print(f"  {g['username']:25} Risk: {g['risk_level']:10} Reasons: {', '.join(g['reasons'])}")