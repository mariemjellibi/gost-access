import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def explain_ghost(ghost):
    prompt = f"""You are a senior identity security analyst. A ghost identity was detected in a Keycloak realm.
- Username: {ghost['username']}
- Roles: {', '.join(ghost['roles'])}
- Last login: {ghost['last_login'] if ghost['last_login'] else 'Never'}
- Risk level: {ghost['risk_level']}
- Reasons: {', '.join(ghost['reasons'])}

Respond in exactly this format:
SEVERITY: <one sentence>
EXPLANATION: <plain English, under 50 words>
FIX_COMMAND: <kcadm.sh command to disable the user>
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()