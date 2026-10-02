import pytest
from ussd_client import USSDSessionClient
from jsonschema import ValidationError


@pytest.fixture
def ussd_client():
    """Provides a fresh USSD session instance and handles cleanup on teardown."""
    client = USSDSessionClient()
    yield client
    # Session teardown execution
    try:
        client.terminate_session()
    except Exception:
        pass


class TestUSSDAccountBalanceJourney:
    """E2E Journey: Check Account Balance Flow (*123# -> Option 1)."""

    def test_successful_balance_check_flow(self, ussd_client):
        # 1. Dial USSD Shortcode
        init_res = ussd_client.initiate_session()
        assert init_res.status_code == 200
        init_data = init_res.json()
        assert init_data.get("sessionStatus") == "CON"
        assert "Welcome to Main Menu" in init_data.get("displayMessage", "")

        # 2. Select Option 1 (Check Balance)
        nav_res = ussd_client.navigate_menu(journey_id="JRN-BAL-CHECK", option="1")
        assert nav_res.status_code == 200
        nav_data = nav_res.json()
        assert nav_data.get("sessionStatus") == "END"
        assert "Your balance is" in nav_data.get("displayMessage", "")


class TestUSSDTransferFundsJourney:
    """E2E Journey: Multi-step Funds Transfer Flow (*123# -> Option 2 -> Enter Amount -> Confirm)."""

    def test_transfer_funds_full_lifecycle(self, ussd_client):
        # Step 1: Initiate session
        step1 = ussd_client.initiate_session()
        assert step1.status_code == 200
        assert step1.json().get("sessionStatus") == "CON"

        # Step 2: Select Transfer Option
        step2 = ussd_client.navigate_menu(journey_id="JRN-XFER-MENU", option="2")
        assert step2.status_code == 200
        assert "Enter Amount" in step2.json().get("displayMessage", "")

        # Step 3: Enter Transfer Amount
        step3 = ussd_client.send_request(
            journey_id="JRN-XFER-AMOUNT",
            operation_name="INPUT_AMOUNT",
            extra_args={"amount": "5000"}
        )
        assert step3.status_code == 200
        assert "Confirm Transfer of 5000? 1: Yes, 2: No" in step3.json().get("displayMessage", "")

        # Step 4: Confirm Action
        step4 = ussd_client.send_request(
            journey_id="JRN-XFER-CONFIRM",
            operation_name="CONFIRM_ACTION",
            extra_args={"user_input": "1"}
        )
        assert step4.status_code == 200
        assert step4.json().get("sessionStatus") == "END"
        assert "Transfer Successful" in step4.json().get("displayMessage", "")


class TestUSSDEdgeAndExceptionFlows:
    """E2E Journey: Session Expiry and Invalid Route Handling."""

    def test_invalid_menu_option_retry_prompt(self, ussd_client):
        ussd_client.initiate_session()
        
        # Send invalid menu choice
        res = ussd_client.navigate_menu(journey_id="JRN-MENU-SEL", option="999")
        assert res.status_code == 200
        assert res.json().get("sessionStatus") == "CON"
        assert "Invalid selection" in res.json().get("displayMessage", "")

    def test_session_reuse_after_termination(self, ussd_client):
        ussd_client.initiate_session()
        ussd_client.terminate_session()
    
        # Re-using the terminated session ID should return an error payload
        stale_res = ussd_client.navigate_menu(journey_id="JRN-BAL-CHECK", option="1")
        assert stale_res.status_code == 200
        assert stale_res.json().get("errorCode") == "ERR_SESSION_EXPIRED"
        
class TestUSSDEdgeAndExceptionFlows:
    # ... existing tests ...

    def test_schema_validation_failure_on_malformed_response(self, ussd_client, requests_mock):
        """Ensures client raises ValidationError if gateway returns malformed payload without displayMessage or errorCode."""
        from config import Config
        
        # Override mock with invalid schema response missing required fields
        requests_mock.post(Config.BASE_URL, json={"sessionStatus": "CON"}, status_code=200)

        with pytest.raises(ValidationError):
            ussd_client.initiate_session()