import json
import jsonpath_rw_ext as jp
import logging
import requests
import sys
import urllib.parse
from retry import retry

from tado.enums import AuthenticationProperties, BaseUrls, EnvVarNames
from tado import utils

log = logging.getLogger(__name__)


class TokenExpired(Exception):
    """Exception raised when an API request is made with an expired token"""

    pass


class TadoManager:
    """Base class used to orchestrate interaction with the Tado API.

    Authentication with the Tado API uses credentials in the following order:

    1. Via **arguments** supplied to this class during instantiation

       * ``username``, ``password``, ``client_id``, ``client_secret``

    2. Via **environment variables** configured by the user

       * ``TADO_USERNAME``, ``TADO_PASSWORD``, ``CLIENT_ID``, ``CLIENT_SECRET``

    :param username: Tado account username, defaults to None
    :type username: str, optional
    :param password: Tado account password, defaults to None
    :type password: str, optional
    :param client_secret: Tado OAuth client secret, defaults to None
    :type client_secret: str, optional
    :param client_id: Tado OAuth client identifier, defaults to "tad-web-app"
    :type client_id: str, optional
    """

    def __init__(
        self,
        username: str = None,
        password: str = None,
        client_secret: str = None,
        client_id: str = "tado-web-app",
    ) -> None:
        """Constructor method"""
        self.username = username
        self.password = password
        self.client_secret = client_secret
        self.client_id = client_id
        self.access_token = None
        self.home_id = None
        self.zones = None
        self.leader_devices = None
        self._load_config()

    def _load_config(self) -> None:
        """Bootstrap configuration method.

        This runs the minimum set of calls to render the package functional (i.e.
        authentication with the Tado API, and retrieval of basic configuration
        information).
        """
        self.get_access_token()
        self.get_home_id()
        self.get_zones()
        self.get_leader_devices()

    def _prepare_headers(self) -> dict:
        """Prepares the set of web request headers for each API call.

        If the ``access_token`` has already been retrieved, it will be included
        in the headers as a bearer authentication token.

        :return: Dict of headers
        :rtype: dict
        """
        headers = {}
        headers["Content-Type"] = "application/json"
        try:
            headers["Authorization"] = f"Bearer {self.access_token}"
        except AttributeError:
            # Ignore - we just don't have the access token yet
            pass
        return headers

    @retry(TokenExpired, tries=2)
    def _call_tado_api(self, method: str, url: str, data: dict = {}) -> str:
        """Convenience wrapper method to call API endpoints with automatic retry.

        :param method: HTTP method (e.g. ``GET``, ``POST``, ``PUT``)
        :type method: str
        :param url: URL as constructed and requested by the method caller
        :type url: str
        :param data: Request body, defaults to {}
        :type data: dict, optional
        :raises TokenExpired: Raised when an API request uses an expired token
        :return: Stringified JSON response from the called API
        :rtype: str
        """
        try:
            response = requests.request(
                method, url, headers=self._prepare_headers(), data=json.dumps(data)
            )
        except Exception:
            log.exception("Exception occurred while calling API")
        else:
            if utils.has_token_expired(response):
                self.get_access_token()
                raise TokenExpired("Token expired, retrying")
            elif response.status_code != 200:
                log.error(
                    f"API request unsuccessful [HTTP code: {response.status_code}]"
                )
                sys.exit(-1)
            else:
                resp_json = response.json()
                return resp_json

    def build_authentication_params(self) -> str:
        """Prepares the set of query parameters required to retrieve an access token
        from the Tado API.

        * **Client ID** - e.g. ``tado-web-app``
        * **Client Secret** - as retrieved from ``https://app.tado.com/env.js``
        * **Grant Type** - e.g. ``password``
        * **Scope** - e.g. ``home.user``
        * **Tado username** - sourced from class instantiation argument or environment
        * **Tado password** - sourced from class instantiation argument or environment

        :return: URL encoded string of query parameters
        :rtype: str
        """
        auth_environment = dict(
            grant_type=AuthenticationProperties.GRANT_TYPE.value,
            scope=AuthenticationProperties.SCOPE.value,
            client_id=self.client_id
            if self.client_id
            else utils.get_environment_variable(EnvVarNames.CLIENT_ID.value),
            client_secret=self.client_secret
            if self.client_secret
            else utils.get_environment_variable(EnvVarNames.CLIENT_SECRET.value),
            password=self.password
            if self.password
            else utils.get_environment_variable(EnvVarNames.TADO_PASSWORD.value),
            username=self.username
            if self.username
            else utils.get_environment_variable(EnvVarNames.TADO_USERNAME.value),
        )
        return urllib.parse.urlencode(auth_environment)

    def get_access_token(self) -> None:
        """Generates and uses a new authorization token for all subsequent requests."""
        log.info("Retrieving ACCESS TOKEN")
        url = "?".join(
            [BaseUrls.TADO_AUTH_API.value, self.build_authentication_params()]
        )
        try:
            access_token = self._call_tado_api("POST", url)["access_token"]
        except KeyError:
            log.exception("Unable to extract ACCESS TOKEN from API response")
        else:
            log.info(f"Retrieved ACCESS TOKEN = [{utils.mask(access_token)}]")
            self.access_token = access_token

    def get_home_id(self) -> None:
        """Retrieves the Tado home identifier."""
        log.info("Retrieving HOME ID")
        url = BaseUrls.TADO_BASE_API.value
        try:
            home_id = self._call_tado_api("GET", url)["homes"][0]["id"]
        except KeyError:
            log.exception("Unable to extract HOME ID from API response")
        else:
            log.info(f"Retrieved HOME ID = [{utils.mask(home_id)}]")
            self.home_id = home_id

    def get_zones(self) -> None:
        """Retrieves the list of zones and full configuration for each."""
        log.info("Retrieving ZONES and DEVICES")
        url = f"{BaseUrls.TADO_HOME_API.value}/{self.home_id}/zones"
        zones = self._call_tado_api("GET", url)
        device_count = len(jp.match("$.[*].devices[*].serialNo", zones))
        log.info(f"Retrieved [{len(zones)}] ZONES and [{device_count}] DEVICES")
        self.zones = zones
        return

    def get_leader_devices(self) -> None:
        """Retrieves the set of ``zone_name:device_serial_number`` for the **leader**
        device in each zone (i.e. the device designated to provide the temperature
        reading for its zone).
        """
        log.info("Retrieving LEADER DEVICES")
        url = f"{BaseUrls.TADO_HOME_API.value}/{self.home_id}/zones"
        devices = {
            i["name"]: jp.match("$.devices[?(duties[*]~'ZONE_LEADER')]", i)[0][
                "serialNo"
            ]
            for i in self._call_tado_api("GET", url)
        }
        log.info(
            f"Retrieved LEADER DEVICES = {[utils.mask(i) for i in devices.values()]}"
        )
        self.leader_devices = devices

    @staticmethod
    def celsius_to_fahrenheit(input_temperature: float) -> float:
        """Converts a given temperature from celsius to fahrenheit.

        :param input_temperature: Temperature in celsius
        :type input_temperature: float
        :return: Temperature in fahrenheit
        :rtype: float
        """
        output_temperature = round((float(input_temperature) * float(9 / 5)) + 32, 1)
        return output_temperature

    @staticmethod
    def fahrenheit_to_celsius(input_temperature: float) -> float:
        """Converts a given temperature from fahrenheit to celsius.

        :param input_temperature: Temperature in fahrenheit
        :type input_temperature: float
        :return: Temperature in celsius
        :rtype: float
        """
        output_temperature = round((float(input_temperature) - 32.0) * float(5 / 9), 1)
        return output_temperature
