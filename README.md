# tado-overseer
Light automation and management for Tado systems

## Tado?
[Tado](https://www.tado.com/all-en) is a smart thermostat system for home heating and ventilation systems

Home comfort can be managed on a room-by-room basis, and with additional features such as _geofencing_, _weather adaption_ and _open window detection_, it aims to improve energy efficiency as well as convenience.

Tado provides a range of products that retrofit into existing systems with management available through several interfaces, most notably [mobile apps](https://www.tado.com/all-en/tado-app) and a [web UI](https://app.tado.com/#/account/sign-in).

In addition, a RESTful web API enables programmatic management of devices and their configuration.

## Why _Tado Overseer_?
The existing UI/app interfaces are great for normal and occasional use, and smart home integrations make it even easier to manage day-to-day functions on _groups_ of devices, but it becomes more difficult to manage configuration parameters across multiple devices.

_Tado Overseer_ attempts to make this easier, by exposing certain these functions through a simple Python API.


## Using

### Docker

1. Clone the repo

   ```
   git clone https://github.com/mmcf/tado-overseer.git
   ```

1. Set your Tado credentials as environment variables

   `.env`
   ```
   TADO_USERNAME=<Your_tado_account_username_or_email>
   TADO_PASSWORD=<Your_tado_account_password>
   CLIENT_SECRET=<Tado_OAuth_client_secret>
   CLIENT_ID=tado-web-app
   ```

   **Note**: `CLIENT_ID` and `CLIENT_SECRET` can be retrieved from: `https://app.tado.com/env.js`

1. Configure your temperature offsets in `config.yaml`

   ```
   tado:
   offsets:
      Hallway: -4.0
      Kitchen: -2.7
      Study: -3.0
      Main Bathroom: -4.0
      Utility Room: -1.8
      Lounge: -3.5
   ```

1. Run the container

   ```
   docker-compose run tado-overseer scripts/apply_offsets.py [ --dry-run ]

    _            _
   | |_ __ _  __| | ___         _____   _____ _ __ ___  ___  ___ _ __
   | __/ _` |/ _` |/ _ \ _____ / _ \ \ / / _ \ '__/ __|/ _ \/ _ \ '__|
   | || (_| | (_| | (_) |_____| (_) \ V /  __/ |  \__ \  __/  __/ |
    \__\__,_|\__,_|\___/       \___/ \_/ \___|_|  |___/\___|\___|_|


   2022-12-10 23:37:52,808 [tado.base] INFO - Retrieving ACCESS TOKEN
   2022-12-10 23:37:53,839 [tado.base] INFO - Retrieved ACCESS TOKEN = [eyJh...]
   2022-12-10 23:37:53,839 [tado.base] INFO - Retrieving HOME ID
   2022-12-10 23:37:54,061 [tado.base] INFO - Retrieved HOME ID = [2461...]
   2022-12-10 23:37:54,061 [tado.base] INFO - Retrieving ZONES and DEVICES
   2022-12-10 23:37:54,289 [tado.base] INFO - Retrieved [6] ZONES and [7] DEVICES
   2022-12-10 23:37:54,289 [tado.base] INFO - Retrieving LEADER DEVICES
   2022-12-10 23:37:54,617 [tado.base] INFO - Retrieved LEADER DEVICES = ['RU15...', 'VA31...', 'VA29...', 'VA29...', 'VA00...', 'VA29...']
   2022-12-10 23:37:55,771 [tado.offsets] INFO - Applying change to [Hallway        ] - [current:-7.0, target: -4.0]
   2022-12-10 23:37:55,772 [tado.offsets] INFO - Applying change to [Kitchen        ] - [current:-7.0, target: -2.7]
   2022-12-10 23:37:55,772 [tado.offsets] INFO - Applying change to [Utility Room   ] - [current:-7.0, target: -1.8]
   2022-12-10 23:37:55,772 [tado.offsets] INFO - Applying change to [Lounge         ] - [current:-7.0, target: -3.5]
   2022-12-10 23:37:55,772 [tado.offsets] INFO - Applying change to [Study          ] - [current:-7.0, target: -3.0]
   ```

## Development

### Pre-commit hooks
This repo uses [pre-commit](https://pre-commit.com/#intro) to ensure that all code checked in follows proper Python styling guidelines.  The configuration used can be found [here](https://github.com/mmcf/tado-overseer/blob/main/.pre-commit-config.yaml).
