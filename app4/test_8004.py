"""Test endpoint on port 8004"""
import requests
import json

data = {
    "action": "woman smiling at camera",
    "emotion": "happy",
    "product_tone": "luxury perfume"
}

print("Testing /api/prompts/optimize on port 8004...")

try:
    response = requests.post(
        "http://localhost:8004/api/prompts/optimize",
        json=data,
        timeout=60
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except requests.exceptions.Timeout:
    print("ERROR: Request timed out after 60 seconds")
except Exception as e:
    print(f"ERROR: {e}")
