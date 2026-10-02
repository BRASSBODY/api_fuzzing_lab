import uuid
import requests
from jsonschema import validate
from config import Config
from schemas import USSD_SUCCESS_RESPONSE_SCHEMA, USSD_ERROR_RESPONSE_SCHEMA

class USSDSessionClient:
    """Encapsulates stateful USSD API operations for a single session with contract schema validation."""

    def __init__(self, msisdn: str = Config.DEFAULT_MSISDN, route_number: str = Config.DEFAULT_ROUTE):
        self.base_url = Config.BASE_URL
        self.msisdn = msisdn
        self.route_number = route_number
        self.session_id = f"SESS-{uuid.uuid4().hex[:8].upper()}"
        self.language_code = "en"

    def _build_payload(self, journey_id: str, operation_name: str, extra_args: dict = None) -> dict:
        arguments = {
            "operation_name": operation_name,
            "ACCOUNT_HOLDER_MSISDN": self.msisdn,
            "route_number": self.route_number
        }
        if extra_args:
            arguments.update(extra_args)

        return {
            "languageCode": self.language_code,
            "sessionIdentifier": self.session_id,
            "journeyIdentifier": journey_id,
            "arguments": arguments
        }

    def send_request(self, journey_id: str, operation_name: str, extra_args: dict = None) -> requests.Response:
        """Sends request and validates response payload against JSON schemas."""
        payload = self._build_payload(journey_id, operation_name, extra_args)
        response = requests.post(
            self.base_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=Config.TIMEOUT
        )

        # Schema Contract Validation
        data = response.json()
        if "errorCode" in data:
            validate(instance=data, schema=USSD_ERROR_RESPONSE_SCHEMA)
        else:
            validate(instance=data, schema=USSD_SUCCESS_RESPONSE_SCHEMA)

        return response

    def initiate_session(self) -> requests.Response:
        """Step 1: Dial shortcode and initialize USSD menu."""
        return self.send_request(
            journey_id="JRN-START",
            operation_name="INITIATE_SERVICE"
        )

    def navigate_menu(self, journey_id: str, option: str) -> requests.Response:
        """Step 2+: Send user input selection."""
        return self.send_request(
            journey_id=journey_id,
            operation_name="SELECT_OPTION",
            extra_args={"user_input": option}
        )

    def terminate_session(self) -> requests.Response:
        """Final Step: Explicitly close the session."""
        return self.send_request(
            journey_id="JRN-CLOSE",
            operation_name="TERMINATE"
        )