"""Create first project via API"""
import requests
import json

# Create project
response = requests.post(
    "http://localhost:8000/api/projects",
    json={
        "name": "Test Gemini 3.0 Pro Integration",
        "template": json.load(open("../templates/lve_perfume_commercial.json"))
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ Project created successfully!")
    print(f"Project ID: {data.get('project_id')}")
else:
    print(f"\n❌ Error creating project")
