import requests
import os
from dotenv import load_dotenv
import json

print("=" * 60)
print("🔍 SENTINEL AI - FULL DIAGNOSTIC")
print("=" * 60)

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

# Test 1: Check API Key
print("\n1️⃣ CHECK API KEY")
print("-" * 60)
if api_key:
    print(f"✅ API Key loaded: {api_key[:20]}...")
else:
    print("❌ API Key NOT loaded!")
    exit(1)

# Test 2: Check FastAPI server
print("\n2️⃣ CHECK FASTAPI SERVER")
print("-" * 60)
try:
    response = requests.get('http://127.0.0.1:8000/health', timeout=5)
    print(f"✅ FastAPI is running!")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"❌ FastAPI is NOT running!")
    print(f"   Error: {str(e)}")
    print(f"   FIX: Run: python -m uvicorn main:app --reload")
    exit(1)

# Test 3: Check Google Gemini API directly
print("\n3️⃣ CHECK GOOGLE GEMINI API")
print("-" * 60)
url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}'
payload = {
    'contents': [{
        'role': 'user',
        'parts': [{'text': 'Test message'}]
    }]
}
headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            candidates = data.get('candidates', [])
            if candidates:
                text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                print(f"✅ Google Gemini API is working!")
                print(f"   Response: {text[:100]}...")
            else:
                print(f"⚠️ No candidates in response")
                print(f"   Response: {json.dumps(data, indent=2)[:200]}")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {str(e)}")
            print(f"   Raw response: {response.text[:200]}")
    else:
        print(f"❌ Google API returned status {response.status_code}")
        try:
            error_data = response.json()
            print(f"   Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
        except:
            print(f"   Response: {response.text[:200]}")
            
except requests.Timeout:
    print(f"❌ Google API Timeout")
except requests.ConnectionError as e:
    print(f"❌ Connection Error: {str(e)}")
except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")

# Test 4: Test FastAPI /analyze endpoint
print("\n4️⃣ TEST FASTAPI /ANALYZE ENDPOINT")
print("-" * 60)
try:
    # Create a test file
    test_content = b"This is a test document. The main topic is testing."
    files = {'file': ('test.txt', test_content)}
    data = {'question': 'What is the main topic?'}
    
    response = requests.post(
        'http://127.0.0.1:8000/analyze',
        files=files,
        data=data,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        answer = result.get('answer', '')
        print(f"✅ /analyze endpoint works!")
        print(f"   Answer: {answer[:100]}...")
    else:
        print(f"❌ /analyze returned status {response.status_code}")
        print(f"   Response: {response.text[:300]}")
        
except Exception as e:
    print(f"❌ Error testing /analyze: {str(e)}")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)

