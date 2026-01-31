import httpx
import json

def test_bulk():
    url = "http://127.0.0.1:8010/processes/bulk"
    payload = {
        "numbers": [
            "0001745-93.1989.8.19.0002",
            "0000000-00.0000.0.00.0000" # Invalid one to test failure
        ]
    }
    try:
        r = httpx.post(url, json=payload, timeout=60)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Results Count: {len(data['results'])}")
            print(f"Failures: {data['failures']}")
            if data['results']:
                print(f"First result phase: {data['results'][0]['phase']}")
        else:
            print(r.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_bulk()
