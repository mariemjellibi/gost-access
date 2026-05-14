# 👻 Ghost Access — AI-Powered IAM Security Scanner

> Automatically detects ghost identities in enterprise Keycloak realms, explains risks with AI, and opens remediation tickets — all in a fully automated DevSecOps pipeline.

![Pipeline](https://github.com/mariemjellibi/gost-access/actions/workflows/devsecops.yml/badge.svg)

## 🔍 The Problem

Every organization accumulates **ghost identities** over time:
- Former employees whose accounts were never deactivated
- Service accounts created for projects that ended months ago
- Overprivileged bots sitting in production with admin access

These are invisible to most security teams — and they are the #1 vector for real breaches. SolarWinds. Uber. LastPass. All exploited stale identities.

## ⚡ What Ghost Access Does

1. **Scans** your Keycloak realm for all identities
2. **Detects** ghosts — inactive 60+ days, never logged in, dangerous roles with no activity
3. **Explains** each risk in plain English using Groq AI (LLaMA 3.1)
4. **Generates** exact remediation commands per ghost
5. **Automatically opens GitHub Issues** for every critical finding
6. **Runs every Monday** via scheduled GitHub Actions pipeline

## 🛡️ DevSecOps Pipeline

Every push to `main` automatically triggers 5 security gates:

| Gate | Tool | What it checks |
|------|------|----------------|
| Code Security | Bandit | Dangerous Python patterns |
| Dependency Scan | Safety | Known CVEs in libraries |
| Container Scan | Trivy | Vulnerabilities in Docker image |
| Secret Detection | detect-secrets | Exposed credentials in commits |
| IAM Ghost Scan | Custom + Groq AI | Ghost identities + auto remediation |

## 🏗️ Architecture
Keycloak Realm
↓
Python Scanner (boto3-style Admin API)
↓
Ghost Detection Engine (inactivity + role rules)
↓
Groq AI (LLaMA 3.1) — risk explanation + fix command
↓
Streamlit Dashboard + GitHub Issues
↓
GitHub Actions (runs every Monday 08:00 UTC)

## 🚀 Run Locally

```bash
# 1. Start Keycloak
docker run -d --name keycloak -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:24.0.1 start-dev

# 2. Clone and install
git clone https://github.com/mariemjellibi/gost-access
cd gost-access
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Add your GROQ_API_KEY to .env

# 4. Populate with test data
python3 populate.py

# 5. Run the dashboard
streamlit run app.py
```

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Identity Provider | Keycloak 24 (Docker) |
| Scanner | Python + Keycloak Admin REST API |
| AI Engine | Groq API — LLaMA 3.1 8B Instruct |
| Dashboard | Streamlit |
| Pipeline | GitHub Actions |
| Container Scan | Trivy |
| Secret Detection | detect-secrets |
| Code Security | Bandit + Safety |
