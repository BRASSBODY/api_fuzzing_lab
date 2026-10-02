# 1. Schema for active/continuing or ended menu responses
USSD_SUCCESS_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["sessionStatus", "displayMessage"],
    "properties": {
        "sessionStatus": {
            "type": "string",
            "enum": ["CON", "END"]
        },
        "displayMessage": {
            "type": "string",
            "minLength": 1
        }
    },
    "additionalProperties": True
}

# 2. Schema for error responses (e.g., expired session, system error)
USSD_ERROR_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["errorCode", "message"],
    "properties": {
        "errorCode": {
            "type": "string"
        },
        "message": {
            "type": "string"
        }
    },
    "additionalProperties": True
}