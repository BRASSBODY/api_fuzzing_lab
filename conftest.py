import pytest
from config import Config
from ussd_client import USSDSessionClient


@pytest.fixture(autouse=True)
def mock_ussd_gateway(requests_mock):
    terminated_sessions = set()
    request_counts = {}

    def custom_security_response(request, context):
        payload = request.json()
        session_id = payload.get("sessionIdentifier", "")
        journey = payload.get("journeyIdentifier", "")
        args = payload.get("arguments", {})
        msisdn = args.get("ACCOUNT_HOLDER_MSISDN", "")
        user_input = str(args.get("user_input", ""))

        # 1. Rate Limiting Check (> 5 requests per session triggers 429)
        request_counts[session_id] = request_counts.get(session_id, 0) + 1
        if request_counts[session_id] > 5:
            context.status_code = 429
            return {
                "errorCode": "ERR_TOO_MANY_REQUESTS",
                "message": "Rate limit exceeded. Try again later."
            }

        # 2. MSISDN Identity Mismatch / Spoofing Check
        if msisdn == "2340000000000_SPOOFED":
            context.status_code = 403
            return {
                "errorCode": "ERR_FORBIDDEN",
                "message": "Caller identity mismatch"
            }

        # 3. Payload Oversize / Injection Check
        if len(user_input) > 256 or "'; DROP TABLE" in user_input:
            context.status_code = 400
            return {
                "errorCode": "ERR_INVALID_INPUT",
                "message": "Input validation failed: Payload length or character set unsupported"
            }

        # 4. Session Replay / Closed Session Hijacking Check
        if session_id in terminated_sessions:
            context.status_code = 401
            return {
                "errorCode": "ERR_SESSION_EXPIRED",
                "message": "Session expired or invalid"
            }

        # --- E2E Functional Flow Routes ---
        if journey == "JRN-START" or args.get("operation_name") == "INITIATE_SERVICE":
            context.status_code = 200
            return {
                "sessionStatus": "CON",
                "displayMessage": "Welcome to Main Menu\n1. Check Balance\n2. Transfer Funds"
            }

        if journey == "JRN-BAL-CHECK" and user_input == "1":
            context.status_code = 200
            return {
                "sessionStatus": "END",
                "displayMessage": "Your balance is NGN 50,000.00"
            }

        if journey == "JRN-XFER-MENU" and user_input == "2":
            context.status_code = 200
            return {
                "sessionStatus": "CON",
                "displayMessage": "Enter Amount:"
            }

        if journey == "JRN-XFER-AMOUNT":
            context.status_code = 200
            return {
                "sessionStatus": "CON",
                "displayMessage": "Confirm Transfer of 5000? 1: Yes, 2: No"
            }

        if journey == "JRN-XFER-CONFIRM":
            context.status_code = 200
            return {
                "sessionStatus": "END",
                "displayMessage": "Transfer Successful"
            }

        if user_input == "999":
            context.status_code = 200
            return {
                "sessionStatus": "CON",
                "displayMessage": "Invalid selection. Please try again."
            }

        if journey == "JRN-CLOSE" or args.get("operation_name") == "TERMINATE":
            terminated_sessions.add(session_id)
            context.status_code = 200
            return {
                "sessionStatus": "END",
                "displayMessage": "Session closed"
            }

        # Fallback
        context.status_code = 400
        return {
            "errorCode": "ERR_SESSION_EXPIRED",
            "message": "Session expired or invalid"
        }

    requests_mock.post(Config.BASE_URL, json=custom_security_response)


@pytest.fixture
def ussd_client():
    """Provides a fresh USSDSessionClient instance for test cases."""
    return USSDSessionClient()

@pytest.fixture(autouse=True)
def mock_ussd_gateway(requests_mock):
    terminated_sessions = set()
    request_counts = {}

    def custom_security_response(request, context):
        payload = request.json()
        session_id = payload.get("sessionIdentifier", "")
        journey = payload.get("journeyIdentifier", "")
        args = payload.get("arguments", {})
        msisdn = args.get("ACCOUNT_HOLDER_MSISDN", "")
        user_input = str(args.get("user_input", ""))

        # 1. Rate Limiting Check (> 5 requests per session triggers 429)
        request_counts[session_id] = request_counts.get(session_id, 0) + 1
        if request_counts[session_id] > 5:
            context.status_code = 429
            return {
                "errorCode": "ERR_TOO_MANY_REQUESTS",
                "message": "Rate limit exceeded. Try again later."
            }

        # 2. MSISDN Identity Mismatch / Spoofing Check
        if msisdn == "2340000000000_SPOOFED":
            context.status_code = 403
            return {
                "errorCode": "ERR_FORBIDDEN",
                "message": "Caller identity mismatch"
            }

        # 3. Payload Oversize / Injection Check
        if len(user_input) > 256 or "'; DROP TABLE" in user_input:
            context.status_code = 400
            return {
                "errorCode": "ERR_INVALID_INPUT",
                "message": "Input validation failed: Payload length or character set unsupported"
            }

        # 4. Session Replay / Closed Session Hijacking Check
        if session_id in terminated_sessions:
            context.status_code = 401
            return {
                "errorCode": "ERR_SESSION_EXPIRED",
                "message": "Session expired or invalid"
            }

        # --- E2E Functional Flow Routes ---
        if journey == "JRN-START" or args.get("operation_name") == "INITIATE_SERVICE":
            context.status_code = 200
            return {
                "sessionStatus": "CON",
                "displayMessage": "Welcome to Main Menu\n1. Check Balance\n2. Transfer Funds"
            }

        if journey == "JRN-BAL-CHECK" and user_input == "1":
            context.status_code = 200
            return {
                "sessionStatus": "END",
                "displayMessage": "Your balance is NGN 50,000.00"
            }

        if journey == "JRN-XFER-MENU" and user_input == "2":
            context.status_code = 200
            return {
                "sessionStatus": "CON",
                "displayMessage": "Enter Amount:"
            }

        if journey == "JRN-XFER-AMOUNT":
            context.status_code = 200
            return {
                "sessionStatus": "CON",
                "displayMessage": "Confirm Transfer of 5000? 1: Yes, 2: No"
            }

        if journey == "JRN-XFER-CONFIRM":
            context.status_code = 200
            return {
                "sessionStatus": "END",
                "displayMessage": "Transfer Successful"
            }

        if user_input == "999":
            context.status_code = 200
            return {
                "sessionStatus": "CON",
                "displayMessage": "Invalid selection. Please try again."
            }

        if journey == "JRN-CLOSE" or args.get("operation_name") == "TERMINATE":
            terminated_sessions.add(session_id)
            context.status_code = 200
            return {
                "sessionStatus": "END",
                "displayMessage": "Session closed"
            }

        # Fallback
        context.status_code = 400
        return {
            "errorCode": "ERR_SESSION_EXPIRED",
            "message": "Session expired or invalid"
        }

    requests_mock.post(Config.BASE_URL, json=custom_security_response)