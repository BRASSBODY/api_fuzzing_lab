import pytest
import requests
from ussd_mutator import mutate_ussd_payload

DYNAMIC_ARGUMENTS_URL = "https://empayit.uat.swifta.com/ussd-congo/ussd/djs/v1/getdynamicarguments"
HEADERS = {"Content-Type": "application/json"}

BASELINE_USSD_PAYLOAD = {
    "arguments": [
        {"key": {"value": "operation_name"}, "value": {"value": "confirm_ticket_payment"}},
        {"key": {"value": "ACCOUNT_HOLDER_MSISDN"}, "value": {"value": "2348160283758"}},
        {"key": {"value": "route_number"}, "value": {"value": "TEST"}},
        {"key": {"value": "JOURNEY_CURRENT_STATUS"}, "value": {"value": "PUBLISHED"}},
        {"key": {"value": "ACCOUNT_HOLDER_EMAIL"}, "value": {"value": "adeoyeajibola@gmail.com"}}
    ],
    "languageCode": "fr",
    "sessionIdentifier": "fuzz_session_9999",
    "journeyIdentifier": "fuzz_journey_8888"
}

# Generate vectors at discovery time
MUTATION_VECTORS = mutate_ussd_payload(BASELINE_USSD_PAYLOAD)

@pytest.mark.parametrize("vector", MUTATION_VECTORS, ids=lambda v: f"{v['target']}-{v['type']}")
def test_ussd_payload_resilience(vector):
    """
    Asserts that the USSD dynamic backend handles field mutations safely
    without returning HTTP 500 Unhandled Server Exceptions.
    """
    target = vector["target"]
    mutation_type = vector["type"]
    payload = vector["payload"]

    response = requests.post(DYNAMIC_ARGUMENTS_URL, json=payload, headers=HEADERS, timeout=10)

    # Core assertion: No server crashes allowed
    assert response.status_code != 500, (
        f"\n[!] 🚨 UNHANDLED SERVER CRASH (HTTP 500)"
        f"\nTarget Field  : {target}"
        f"\nMutation Type : {mutation_type}"
        f"\nResponse Body : {response.text[:200]}"
    )

    # Valid validation status codes
    assert response.status_code in [200, 201, 400, 401, 403, 404, 422], (
        f"Unexpected status code HTTP {response.status_code} for target field {target}"
    )