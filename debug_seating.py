
import requests
import json

BASE_URL = "http://127.0.0.1:8081"

def debug_seating():
    # 1. List arrangements
    print("--- Listing Arrangements ---")
    try:
        resp = requests.get(f"{BASE_URL}/api/seating/arrangements")
        if resp.status_code != 200:
            print(f"Error: {resp.text}")
            return
        
        data = resp.json()
        print(f"Total Arrangements: {data['total']}")
        if data['total'] == 0:
            print("No arrangements found!")
            return
            
        for arr in data['arrangements']:
            print(f"ID: {arr['id']}, Date: {arr['exam_date']}, Subjects: {arr['subjects']}")

        # 2. Search for student REG1009
        print("\n--- Searching for Student REG1009 ---")
        # Try both payload formats
        search_payload = {"value": "REG1009"}
        print(f"Payload: {search_payload}")
        resp = requests.post(f"{BASE_URL}/api/arrangements/search", json=search_payload)
        
        if resp.status_code == 200:
            results = resp.json()
            print(f"Success: {results['success']}")
            print(f"Count: {results['count']}")
            print(f"Results: {json.dumps(results['results'], indent=2)}")
        else:
            print(f"Error searching: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_seating()
