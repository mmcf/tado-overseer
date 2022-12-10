from enum import Enum


class EnvVarNames(Enum):
    """Environment variable names used for configuration purposes"""

    CLIENT_ID = "CLIENT_ID"
    CLIENT_SECRET = "CLIENT_SECRET"
    TADO_USERNAME = "TADO_USERNAME"
    TADO_PASSWORD = "TADO_PASSWORD"


class BaseUrls(Enum):
    """Base URL prefixes for various Tado APIs"""

    TADO_AUTH_API = "https://auth.tado.com/oauth/token"
    TADO_BASE_API = "https://my.tado.com/api/v2/me"
    TADO_HOME_API = "https://my.tado.com/api/v2/homes"
    TADO_DEVICE_API = "https://my.tado.com/api/v2/devices"


class AuthenticationProperties(Enum):
    """Static properties used during authentication with Tado APIs"""

    GRANT_TYPE = "password"
    SCOPE = "home.user"
