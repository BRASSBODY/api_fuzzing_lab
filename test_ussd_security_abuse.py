import pytest
import uuid
from ussd_client import USSDSessionClient

class TestUSSDSecurityAndAbuseScenarios:

    def test_msisdn_spoofing_prevention(self, ussd_client):
        """Verify the gateway rejects mismatched/spoofed caller MSISDN headers."""
        # Inject an unauthorized MSISDN into the session client
        ussd_client.msisdn = "2340000000000_SPOOFED"
        
        response = ussd_client.initiate_session()
        assert response.status_code == 403
        assert response.json().get("errorCode") == "ERR_FORBIDDEN"

    def test_session_replay_attack_blocked(self, ussd_client):
        """Verify an attacker cannot execute menu navigation using a terminated session ID."""
        ussd_client.initiate_session()
        ussd_client.terminate_session()

        # Attempt to replay/navigate on closed session
        replay_response = ussd_client.navigate_menu(journey_id="JRN-XFER-CONFIRM", option="1")
        assert replay_response.status_code == 401
        assert replay_response.json().get("errorCode") == "ERR_SESSION_EXPIRED"

    def test_oversized_payload_fuzz_injection(self, ussd_client):
        """Verify input fields reject oversized buffer overflow vectors and SQL injection payloads."""
        ussd_client.initiate_session()

        # 1. Oversized buffer string test (500 chars)
        overflow_vector = "A" * 500
        res_overflow = ussd_client.navigate_menu(journey_id="JRN-XFER-AMOUNT", option=overflow_vector)
        assert res_overflow.status_code == 400
        assert res_overflow.json().get("errorCode") == "ERR_INVALID_INPUT"

        # 2. SQLi injection string test
        sqli_vector = "1'; DROP TABLE users; --"
        res_sqli = ussd_client.navigate_menu(journey_id="JRN-XFER-AMOUNT", option=sqli_vector)
        assert res_sqli.status_code == 400
        assert res_sqli.json().get("errorCode") == "ERR_INVALID_INPUT"

    def test_rate_limiting_abuse_throttling(self, ussd_client):
        """Verify rapid repeated requests trigger HTTP 429 Too Many Requests."""
        ussd_client.initiate_session()

        # Fire 6 rapid requests in succession
        responses = []
        for i in range(6):
            res = ussd_client.navigate_menu(journey_id="JRN-BAL-CHECK", option="1")
            responses.append(res)

        # The 6th request must be throttled with HTTP 429
        last_response = responses[-1]
        assert last_response.status_code == 429
        assert last_response.json().get("errorCode") == "ERR_TOO_MANY_REQUESTS"