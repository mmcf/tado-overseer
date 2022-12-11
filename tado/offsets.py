import dictdiffer
import logging
from pathlib import Path
from tado import utils
from tado.base import TadoManager
from tado.enums import BaseUrls

log = logging.getLogger(__name__)


class TadoOffsetsManager(TadoManager):
    """Manage temperature offsets for zones and devices.

    Each zone in a Tado home has a designated *leader* device which is responsible for
    providing temperature readings for that zone.  Depending on the proximity of the
    device to heat or cold sources (e.g. radiators, windows etc.) it may be necessary
    to "offset" the readings from that device by a certain temperature, to provide a
    more representative/accurate reading for that zone.  This class can be used to
    inspect and set these offsets.

    **Offsets** are defined as pairs of: ``zone_name:temperature_offset_in_celsius``

    Args:
      ``offsets_dict`` (dict: dict, optional):
         Inline dict of offsets to set, defaults to ``{}``

      ``offsets_file`` (str, optional):
         YAML file with offsets to set, defaults to ``config.yaml``

    """

    def __init__(
        self, offsets_dict: dict = {}, offsets_file: str = "config.yaml", **kwargs
    ) -> None:
        """Constructor method"""
        super().__init__(**kwargs)
        self.offsets_file = offsets_file
        self.offsets_dict = offsets_dict
        if self.offsets_dict:
            self.user_config = self.offsets_dict
        elif Path(self.offsets_file).is_file():
            self.user_config = utils.load_yaml_file(self.offsets_file)

    def get_current_device_offsets(self) -> dict:
        """Retrieves the *currently* configured temperature offset values from the
        leader device in each zone.

        Returns:
          dict: Set of ``zone_name:current_offset_temperature`` entries

        """
        room_offsets = {}
        for room_name, serial_no in self.leader_devices.items():
            url = f"{BaseUrls.TADO_DEVICE_API.value}/{serial_no}/temperatureOffset"
            device_offset = self._call_tado_api("GET", url)["celsius"]
            room_offsets[room_name] = device_offset
        return room_offsets

    def get_target_device_offsets(self) -> dict:
        """Retrieves the *target* temperature offset values to be set in each zone,
        as defined by the user in the input configuration file.

        Returns:
          dict: Set of ``zone_name:target_offset_temperature`` entries

        """
        return self.user_config["tado"]["offsets"]

    def apply_offset_changes(self, dry_run=False) -> None:
        """Sets the target offset to any zone which has a different value already set.

        This function compares the set of user-provided (target) offsets with the
        existing (current) offsets for each zone.  For any zone where the target offset
        is different, a ``PUT`` request is issued to the Tado API to change the offset.

        Args:
          ``dry_run`` (bool, optional, optional):
             Doesn't modify offsets when set to ``True``, defaults to ``False``
        """
        for delta in list(
            dictdiffer.diff(
                self.get_target_device_offsets(), self.get_current_device_offsets()
            )
        ):
            if delta[0] == "change":
                # Extract change details
                room_name, target_temp, current_temp = (
                    delta[1],
                    delta[2][0],
                    delta[2][1],
                )

                # Apply correction
                serial_no = self.leader_devices[room_name]
                url = f"{BaseUrls.TADO_DEVICE_API.value}/{serial_no}/temperatureOffset"
                data_payload = dict(celsius=f"{target_temp:.1f}")
                log.info(
                    "Applying change to [{}] - [current:{}, target: {}]".format(
                        room_name.ljust(15), current_temp, target_temp
                    )
                )
                if not dry_run:
                    self._call_tado_api("PUT", url, data_payload)
