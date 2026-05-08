import requests
import json

url = "http://localhost:8000/api/emotion-trend/analyze"

with open("test_emotion_trend.json", "r", encoding="utf-8") as f:
    data = json.load(f)

response = requests.post(url, json=data)
print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
