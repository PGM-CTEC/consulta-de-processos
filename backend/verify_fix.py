import httpx
import json

def test():
    try:
        r = httpx.get('http://127.0.0.1:8010/processes/0001745-93.1989.8.19.0002')
        if r.status_code != 200:
            print(f"Error: {r.status_code}")
            print(r.text)
            return
            
        data = r.json()
        print(f"Number: {data.get('number')}")
        print(f"Class: {data.get('class_nature')}")
        print(f"Subject: {data.get('subject')}")
        print(f"Court: {data.get('court')}")
        print(f"Phase: {data.get('phase')}")
        print(f"Dist Date: {data.get('distribution_date')}")
        
        movements = data.get('movements', [])
        print(f"\nMovements count: {len(movements)}")
        if movements:
            print(f"First Mov: {movements[0].get('description')}")
            print(f"First Code: {movements[0].get('code')}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test()
