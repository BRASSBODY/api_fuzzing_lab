import requests
from mutator import generate_mutated_payloads

TARGET_URL = "http://127.0.0.1:4011/v1/ticket-bouquet"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer mock-token"
}

# Baseline valid template payload
baseline_payload = {
    "name": "VIP Ticket",
    "price": 5000,
    "quantity": 50,
    "active": True
}

def run_fuzzer():
    mutations = generate_mutated_payloads(baseline_payload)
    print(f"[*] Starting Fuzzing Run against {TARGET_URL}...")
    print(f"[*] Total mutations to test: {len(mutations)}\n")

    passed_count = 0
    flagged_count = 0

    for idx, item in enumerate(mutations, 1):
        field = item["target_field"]
        mutation_type = item["mutation_type"]
        payload = item["payload"]

        try:
            response = requests.post(TARGET_URL, json=payload, headers=headers)
            status = response.status_code

            # Standard validation response codes (API handled it correctly)
            if status in [200, 201, 400, 401, 405, 422]:
                passed_count += 1
                print(f"[{idx}/{len(mutations)}] PASS | Field: '{field}' ({mutation_type}) -> HTTP {status}")
            
            # Unhandled Server Errors (Bugs / Vulnerabilities)
            elif status >= 500:
                flagged_count += 1
                print(f"[{idx}/{len(mutations)}] 🚨 FLAGGED 500 BUG | Field: '{field}' ({mutation_type})")
                print(f"    Payload: {payload}")

        except Exception as e:
            print(f"[{idx}/{len(mutations)}] ERROR | Request failed: {e}")

    print("\n" + "="*50)
    print(f"📊 FUZZING RUN COMPLETE")
    print(f"Total Tested : {len(mutations)}")
    print(f"Handled (OK) : {passed_count}")
    print(f"Flagged (500): {flagged_count}")
    print("="*50)

if __name__ == "__main__":
    run_fuzzer()