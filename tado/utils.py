import os
import requests
import yaml


def get_environment_variable(key: str) -> str:
    """Retrieves an environment variable by name.

    Args:
      ``key`` (str):
         Environment variable name

    Returns:
      str: Environment variable value

    Raises:
      ``KeyError``: If the environment variable cannot be found

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

    Args:
      ``response`` (requests.Response):
         Response: https://requests.readthedocs.io/en/latest/api/#requests.Response

    Returns:
      bool: ``True`` if an expired token was used, ``False`` if not

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

    Args:
      ``filename`` (str):
         Full path and filename to load

    Returns:
      dict: Dictionary representation of the file

    """
    with open(filename, "r") as stream:
        return yaml.safe_load(stream)


def mask(value: str, length: int = 4) -> str:
    """Truncates a value, typically for display purposes (e.g. hiding a device's
    serial number from being displayed in full).

    Args:
      ``value`` (str):
         Input string to mask/truncate
      ``length`` (int, optional):
         String length to preserve, defaults to 4

    Returns:
      str: Truncated string suffixed by an ellipsis

    """
    return f"{str(value)[0:length]}..."
