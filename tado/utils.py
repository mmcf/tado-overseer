import os
import requests
import yaml


def get_environment_variable(key: str) -> str:
    """Retrieves an environment variable by name.

    :param key: Environment variable name
    :type key: str
    :raises KeyError: If the environment variable cannot be found
    :return: Environment variable value
    :rtype: str
    """
    try:
        env_var = os.environ[key]
    except KeyError:
        raise KeyError(f"Unable to retrieve environment: {key}")
    else:
        return env_var


def has_token_expired(response: requests.Response) -> bool:
    """Evaluates an API response to determine if an expired token was the cause of
    an *HTTP 401 Unauthorized* error.

    :param response: https://requests.readthedocs.io/en/latest/api/#requests.Response
    :type response: requests.Response
    :return: ``True`` if an expired token was used, ``False`` if not
    :rtype: bool
    """
    if response.status_code == 401:
        try:
            if any(
                d.get("title", None) == "access token is expired"
                for d in response.json()["errors"]
            ):
                return True
            else:
                return False
        except KeyError:
            return False


def load_yaml_file(filename: str) -> dict:
    """Loads a given YAML file.

    :param filename: Full path and filename to load
    :type filename: str
    :return: Dictionary representation of the file
    :rtype: dict
    """
    with open(filename, "r") as stream:
        return yaml.safe_load(stream)


def mask(value: str, length: int = 4) -> str:
    """Truncates a value, typically for display purposes (e.g. hiding a device's
    serial number from being displayed in full).

    :param value: Input string to mask/truncate
    :type value: str
    :param length: String length to preserve, defaults to 4
    :type length: int, optional
    :return: Truncated string suffixed by an ellipsis
    :rtype: str
    """
    return f"{str(value)[0:length]}..."
