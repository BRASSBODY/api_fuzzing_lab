import os

class Config:
    BASE_URL = os.getenv("USSD_API_BASE_URL", "https://api.staging.internal/ussd/gateway")
    DEFAULT_MSISDN = "+2348012345678"
    DEFAULT_ROUTE = "*123#"
    TIMEOUT = 10  # Seconds