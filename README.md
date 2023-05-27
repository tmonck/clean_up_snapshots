# Clean up snapshots

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)

[![CI](https://img.shields.io/github/actions/workflow/status/tmonck/clean_up_snapshots/ci.yml?style=for-the-badge)](https://github.com/tmonck/clean_up_snapshots/actions/workflows/ci.yml)
[![Latest Release](https://img.shields.io/github/v/release/tmonck/clean_up_snapshots?color=41BDF5&style=for-the-badge)](https://github.com/tmonck/clean_up_snapshots/releases)

This Home Assistant extension exposes a service to automate the clean up of old backups.

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->

- [Clean up snapshots](#clean-up-snapshots)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Config Flow (UI)](#config-flow-ui)
  - [configuration.yaml](#configurationyaml)
- [Use in automations](#use-in-automations)

<!-- markdown-toc end -->

## Prerequisites

To be able to use this extension you must must have the following integrations enabled and configured within your Home Assistant installation.

- [Supervisor][0]

To manage the installation and upgrades easier it's recommendated to use [HACS][1].

## Installation

You can either use the easy button [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=tmonck&repository=clean_up_snapshots&category=integration)
or you can install manually with the steps below.

1. Navigate to HACS Store
2. Search for "Clean up snapshots service"
3. Click on the service, and then on _DOWNLOAD_
4. Restart Home Assistant

## Configuration

### Config Flow (UI)

Once again there is an easy button [![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg](https://my.home-assistant.io/redirect/config_flow_start/?domain=clean_up_snapshots_service) or a manual process.

1. Navigate to Settings > Devices & Services > Integrations
2. Click the Add Integration button in the bottom right of the screen
3. Search for "Clean up your snapshots"
4. Fill out the form
5. Click Submit

### configuration.yaml

> **Warning**
> The setup via the configuration.yaml file is being deprecated and will be removed in a future release.
Add the following to your configuration.yaml file. Adjust the value number snapshots you want to keep.

```yaml
clean_up_snapshots_service:
  number_of_snapshots_to_keep: 3 # optional, default value is 0
```

1. Restart Home Assistant (Settings > System > Restart)
2. Look for the new `clean_up_snapshots_service.clean_up` service (Developer Tools > Services).

## Use in automations

You can trigger this service in an automation similarly to the one below.

```yaml
alias: Daily snapshot clean up
initial_state: 'on'
trigger:
  platform: time
  at: '03:00:00'
condition:
action:
  - service: clean_up_snapshots_service.clean_up
    # Data is optional if you have defined the number of snapshots to keep in the configuration.yaml.
    # data:
      # If this property is passed to the service it will be used regardless of what you have in the configuration.yaml
      # number_of_snapshots_to_keep: 7
```

[0]: https://www.home-assistant.io/integrations/hassio
[1]: https://hacs.xyz/
