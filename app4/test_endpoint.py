"""Test the optimization endpoint directly"""
import requests
import json

# Test the optimization endpoint
data = {
    "action": "woman smiling at camera",
    "emotion": "happy",
    "product_tone": "luxury perfume"
}

print("Testing /api/prompts/optimize endpoint...")
print(f"Request data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(
        "http://localhost:8003/api/prompts/optimize",
        json=data,
        timeout=30  # 30 second timeout
    )
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except requests.exceptions.Timeout:
    print("ERROR: Request timed out after 30 seconds")
except Exception as e:
    print(f"ERROR: {e}")
