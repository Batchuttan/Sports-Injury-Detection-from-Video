import requests

API = "http://localhost:8000"

# Register or login
payload = {"email": "alex.rivera@sportsai.io", "password": "Password123!", "name": "Alex Rivera", "role": "Athlete"}
res = requests.post(f"{API}/auth/register", json=payload)
print("Register status:", res.status_code)
if res.status_code in [200, 201]:
    token = res.json().get("token")
else:
    res = requests.post(f"{API}/auth/login", json={"email": "alex.rivera@sportsai.io", "password": "Password123!"})
    token = res.json().get("token")

print("Token received:", bool(token))

headers = {"Authorization": f"Bearer {token}"}
endpoints = [
    "/notifications",
    "/athlete/assessments",
    "/athlete/performance",
    "/coach/team-monitoring",
    "/coach/workload-alerts",
    "/physio/recovery-status",
    "/scientist/biomechanical-insights",
    "/admin/users",
    "/admin/platform-stats",
]

all_passed = True
for ep in endpoints:
    r = requests.get(f"{API}{ep}", headers=headers)
    print(f"GET {ep:35} -> {r.status_code} ({len(r.content)} bytes)")
    if r.status_code != 200:
        all_passed = False

print("\nALL ENDPOINTS 200 OK:", all_passed)
