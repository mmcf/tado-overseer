import pytest
import responses
import sys

sys.path.append("../")

import tado.base  # noqa
from tado.enums import AuthenticationProperties, BaseUrls  # noqa


@pytest.fixture
def tado_manager():
    return tado.base.TadoManager(
        load_config=False,
        client_secret="dummy_secret",
        password="dummy_password",
        username="dummy_user",
    )


@pytest.fixture
def mock_responses():
    # Mocked call to get ACCESS_TOKEN
    responses.add(
        responses.POST,
        BaseUrls.TADO_AUTH_API.value,
        json={"access_token": "returned_access_token"},
        status=200,
    )
    # Mocked call to get HOME_ID
    responses.add(
        responses.GET,
        BaseUrls.TADO_BASE_API.value,
        json={"homes": [{"id": 999999, "name": "Home"}]},
        status=200,
    )
    # Mocked call to get LEADER DEVICES
    responses.add(
        responses.GET,
        f"{BaseUrls.TADO_HOME_API.value}/999999/zones",
        json=[
            {
                "id": 1,
                "name": "Lounge",
                "devices": [
                    {
                        "serialNo": "111111111111",
                        "duties": ["ZONE_UI", "ZONE_DRIVER", "ZONE_LEADER"],
                    },
                    {"serialNo": "222222222222", "duties": ["ZONE_UI"]},
                ],
            },
            {
                "id": 3,
                "name": "Kitchen",
                "devices": [
                    {
                        "serialNo": "333333333333",
                        "duties": ["ZONE_UI", "ZONE_DRIVER", "ZONE_LEADER"],
                    }
                ],
            },
        ],
        status=200,
    )


class TestAPIRequests(object):
    @responses.activate
    def test_get_access_token(self, tado_manager, mock_responses):
        tado_manager.get_access_token()
        assert tado_manager.access_token == "returned_access_token"

    @responses.activate
    def test_get_home_id(self, tado_manager, mock_responses):
        tado_manager.get_home_id()
        assert tado_manager.home_id == 999999

    @responses.activate
    def test_get_leader_devices(self, tado_manager, mock_responses):
        tado_manager.home_id = 999999
        tado_manager.get_leader_devices()
        assert tado_manager.leader_devices == {
            "Lounge": "111111111111",
            "Kitchen": "333333333333",
        }


class TestConfiguration(object):
    def test_build_authentication_params(self, tado_manager):
        params = tado_manager.build_authentication_params()
        param_dict = dict(
            param_str_pair.split("=") for param_str_pair in params.split("&")
        )
        assert param_dict["client_id"] == "tado-web-app"
        assert param_dict["client_secret"] == "dummy_secret"
        assert param_dict["grant_type"] == AuthenticationProperties.GRANT_TYPE.value
        assert param_dict["password"] == "dummy_password"
        assert param_dict["scope"] == AuthenticationProperties.SCOPE.value
        assert param_dict["username"] == "dummy_user"

    def test__prepare_headers(self, tado_manager):
        # Headers prior to access token
        headers = tado_manager._prepare_headers()
        assert len(headers) == 1
        assert "Content-Type" in headers.keys()
        assert "Authorization" not in headers.keys()

        # Headers after access token
        tado_manager.access_token = "access_token"
        headers = tado_manager._prepare_headers()
        assert len(headers) == 2
        assert "Content-Type" in headers.keys()
        assert "Authorization" in headers.keys()
        assert headers["Authorization"] == "Bearer access_token"


class TestStatics(object):
    @pytest.mark.parametrize(
        "input, output",
        [(0, 32), (0, 32.0), (0.0, 32), (0.0, 32.0), (32.7, 90.9), (-100, -148)],
    )
    def test_celsius_to_fahrenheit(self, input, output, tado_manager):
        assert tado_manager.celsius_to_fahrenheit(input) == output

    @pytest.mark.parametrize(
        "input, output",
        [(32, 0), (32.0, 0), (32, 0.0), (32.0, 0.0), (90.9, 32.7), (-148, -100)],
    )
    def test_fahrenheit_to_celsius(self, input, output, tado_manager):
        assert tado_manager.fahrenheit_to_celsius(input) == output

    @pytest.mark.parametrize(
        "input, exception_type",
        [(None, TypeError), ("aaa", ValueError), (b"0xFF", ValueError)],
    )
    def test_celsius_to_fahrenheit_invalid_input_type(
        self, input, exception_type, tado_manager
    ):
        with pytest.raises(exception_type) as exc_info:  # noqa
            _ = tado_manager.celsius_to_fahrenheit(input)

    @pytest.mark.parametrize(
        "input, exception_type",
        [(None, TypeError), ("aaa", ValueError), (b"0xFF", ValueError)],
    )
    def test_fahrenheit_to_celsius_invalid_input_type(
        self, input, exception_type, tado_manager
    ):
        with pytest.raises(exception_type) as exc_info:  # noqa
            _ = tado_manager.fahrenheit_to_celsius(input)
