"""Test endpoint with longer timeout and verbose output"""
import requests
import json

data = {
    "action": "woman smiling at camera",
    "emotion": "happy",
    "product_tone": "luxury perfume"
}

print("Testing /api/prompts/optimize endpoint...")
print(f"Request data: {json.dumps(data, indent=2)}")
print("Waiting up to 120 seconds...")

try:
    response = requests.post(
        "http://localhost:8003/api/prompts/optimize",
        json=data,
        timeout=120  # 2 minute timeout
    )
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except requests.exceptions.Timeout:
    print("ERROR: Request timed out after 120 seconds")
except Exception as e:
    print(f"ERROR: {e}")
