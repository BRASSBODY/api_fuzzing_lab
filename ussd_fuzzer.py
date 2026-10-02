import json
import requests
from ussd_mutator import mutate_ussd_payload

# Targets pulled directly from the Postman collection
DYNAMIC_OPTIONS_URL = "https://empayit.uat.swifta.com/ussd-congo/ussd/djs/v1/getdynamicoptions"
DYNAMIC_ARGUMENTS_URL = "https://empayit.uat.swifta.com/ussd-congo/ussd/djs/v1/getdynamicarguments"

HEADERS = {
    "Content-Type": "application/json"
}

# Baseline request template from Postman "Confirm Ticket Payment" / "Get Route by Code"
BASELINE_USSD_PAYLOAD = {
    "arguments": [
        {
            "key": {"value": "operation_name"},
            "value": {"value": "confirm_ticket_payment"}
        },
        {
            "key": {"value": "ACCOUNT_HOLDER_MSISDN"},
            "value": {"value": "2348160283758"}
        },
        {
            "key": {"value": "route_number"},
            "value": {"value": "TEST"}
        },
        {
            "key": {"value": "JOURNEY_CURRENT_STATUS"},
            "value": {"value": "PUBLISHED"}
        },
        {
            "key": {"value": "ACCOUNT_HOLDER_EMAIL"},
            "value": {"value": "adeoyeajibola@gmail.com"}
        }
    ],
    "languageCode": "fr",
    "sessionIdentifier": "fuzz_session_9999",
    "journeyIdentifier": "fuzz_journey_8888"
}

def run_ussd_fuzzer(target_url=DYNAMIC_ARGUMENTS_URL):
    mutations = mutate_ussd_payload(BASELINE_USSD_PAYLOAD)
    
    print(f"[*] Starting USSD DJS Fuzzing Run against: {target_url}")
    print(f"[*] Total test vectors generated: {len(mutations)}\n")

    passed_count = 0
    flagged_count = 0

    for idx, item in enumerate(mutations, 1):
        target = item["target"]
        mutation_type = item["type"]
        payload = item["payload"]

        try:
            response = requests.post(target_url, json=payload, headers=HEADERS, timeout=10)
            status = response.status_code

            # Standard expected HTTP codes (200 OK or handled validation errors 400/422)
            if status in [200, 201, 400, 401, 403, 404, 422]:
                passed_count += 1
                print(f"[{idx}/{len(mutations)}] PASS | Target: {target:<30} | Type: {mutation_type:<18} -> HTTP {status}")

            # Flagged: Unhandled Server Crash
            elif status >= 500:
                flagged_count += 1
                print(f"\n[!] 🚨 FLAGGED HTTP {status} BUG")
                print(f"    Target Field  : {target}")
                print(f"    Mutation Type : {mutation_type}")
                print(f"    Server Response: {response.text[:200]}")
                print("-" * 60)

        except Exception as e:
            print(f"[{idx}/{len(mutations)}] REQUEST ERROR | Target: {target} | Error: {e}")

    print("\n" + "="*60)
    print("📊 USSD FUZZING RUN SUMMARY")
    print(f"Target URL   : {target_url}")
    print(f"Total Tested : {len(mutations)}")
    print(f"Passed (OK)  : {passed_count}")
    print(f"Flagged (500): {flagged_count}")
    print("="*60)

if __name__ == "__main__":
    run_ussd_fuzzer(DYNAMIC_ARGUMENTS_URL)