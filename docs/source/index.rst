Welcome to tado-overseer's documentation!
=========================================

.. note:: This is a work in progress.  Please feel free to fork this project or submit a PR to add any functionality you need.

What is Tado?
*************

`Tado`_ is a smart thermostat system for home heating and ventilation systems.  Temperatures can be managed on a room by room basis (through "zoning"), while additional features such as *geofencing*, *weather adaption* and *open window detection* provide energy efficiency and convenience benefits.

Tado devices can be added retrospectively to existing systems, and allow the user to easily manage their devices via `mobile apps`_ (iOS and Android) and a `web UI`_.

In addition, a RESTful web API enables programmatic management of devices and their configuration.

.. _Tado: https://www.tado.com/all-en
.. _mobile apps: https://www.tado.com/all-en/tado-app
.. _web UI: https://app.tado.com/#/account/sign-in

Tado Entities
*************

A typical Tado deployment consists of the following entities:

- **OWNER**:
     This is the account that owns the installation.  Identified by ``id``.

- **HOME**:
     Each **owner** has one or more **homes** defined in their account, each identified by a unique numeric ``homes.id``.

- **ZONE(s)**:
     Each **home** has one or more **zones** (e.g. rooms, buildings or other groups of devices).  Each zone is identified by a unique numeric ``id``.

- **DEVICE(s)**:
     Each **zone** has one or more **devices** associated to it.  Each **device** can be a part of only one **zone**.  Each **zone** has one designated "leader" device, responsible for providing the temperature reading for the zone.

  ::

     ┌─────────┐1       *┌────────┐1       *┌────────┐1       *┌────────┐
     │  OWNER  │─────────│  HOME  │─────────│  ZONE  │─────────│ DEVICE │
     └─────────┘         └────────┘         └────────┘         └────────┘

Each device has a number of pertinent properties:

  - **Serial Number** (``serialNo``): acts as the device identifier for all API requests.
  - **Roles** (``duties``): a list of assigned roles that the device performs.  Leader devices are identified via the presence of the ``ZONE_LEADER`` role.
  - **Status Fields**
     - **Battery** (``batteryState``): shows if the device has any outstanding battery level warnings.
     - **Connection** (``connectionState.value``): shows if the device is currently reachable and actively managed by Tado.
     - **Mount** (``mountingState.value``): shows if the device has been properly installed and calibrated.


Getting Started
***************

Docker
^^^^^^

1. Clone the repo::

      git clone https://github.com/mmcf/tado-overseer.git

2. Set your Tado credentials as environment variables::

      TADO_USERNAME=<Your_tado_account_username_or_email>
      TADO_PASSWORD=<Your_tado_account_password>
      CLIENT_SECRET=<Tado_OAuth_client_secret>
      CLIENT_ID=tado-web-app

**Note**: ``CLIENT_ID`` and ``CLIENT_SECRET`` can be retrieved from `here`_.

.. _here: https://app.tado.com/env.js

3. Configure your temperature offsets in ``config.yaml``::

      tado:
        offsets:
          Hallway: -4.0
          Kitchen: -2.7
          Study: -3.0
          Main Bathroom: -4.0
          Utility Room: -1.8
          Lounge: -3.5

4. Run the container::

      docker-compose run tado-overseer scripts/apply_offsets.py --offsets-file config.yaml [ --dry-run ]

   Which will produce output similar to::

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
      2022-12-10 23:37:54,617 [tado.base] INFO - Retrieved LEADER DEVICES = ['RU15...', 'VA31...', 'VA29...', 'VA29...', 'VA00...   ', 'VA29...']
      2022-12-10 23:37:55,771 [tado.offsets] INFO - Applying change to [Hallway        ] - [current:-7.0, target: -4.0]
      2022-12-10 23:37:55,772 [tado.offsets] INFO - Applying change to [Kitchen        ] - [current:-7.0, target: -2.7]
      2022-12-10 23:37:55,772 [tado.offsets] INFO - Applying change to [Utility Room   ] - [current:-7.0, target: -1.8]
      2022-12-10 23:37:55,772 [tado.offsets] INFO - Applying change to [Lounge         ] - [current:-7.0, target: -3.5]
      2022-12-10 23:37:55,772 [tado.offsets] INFO - Applying change to [Study          ] - [current:-7.0, target: -3.0]




.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
