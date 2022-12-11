import sys

sys.path.append("../")

import pytest  # noqa
import tado.base  # noqa


@pytest.fixture
def tado_manager():
    return tado.base.TadoManager(load_config=False)


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
