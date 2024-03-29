# Clean up snapshots

[![HACS Badge][hacs_badge]][hacs_custom_components]
[![Code style][code_style_badge]][code_style_repo]

[![CI][build_badge]][build_workflow]
[![Latest Release][release_badge]][releases_page]

This Home Assistant extension exposes a service to automate the clean up of old backups.

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->

- [Clean up snapshots](#clean-up-snapshots)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
  - [configuration.yaml](#configurationyaml)
- [Use in automations](#use-in-automations)

<!-- markdown-toc end -->

## Prerequisites

To be able to use this extension you must have the following integrations enabled and configured within your Home Assistant installation.

- [Supervisor][supervisor]

To manage the installation and upgrades easier it's recommended to use [HACS][hacs].

## Installation

You can either use the easy button [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.][my_hacs_repo_badge]][my_integration_lookup]
or you can install manually with the steps below.

1. Navigate to HACS Store
2. Search for "Clean up snapshots service"
3. Click on the service, and then on _DOWNLOAD_
4. Restart Home Assistant

## Configuration

Adding the Clean up snaphots service can be done via the user interface by using this My button:

[![Open your Home Assistant instance and start setting up a new integration.][my_config_flow_start_badge]][my_integration_config_flow]

If the above My button doesn't work, you can also perform the following steps manually:

1. Browse to your Home Assistant instance.
1. In the sidebar, select [Settings][home_assistant_settings].
1. From the configuration menu, select [Devices & Services][home_assistant_devices_services]
1. In the bottom right, select the [Add Integration][my_integration_config_flow] button.
1. From the list, search and select "Clean up snapshots service".
1. Follow the instructions on screen to complete the setup.

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

[build_badge]: https://img.shields.io/github/actions/workflow/status/tmonck/clean_up_snapshots/ci.yml?style=for-the-badge
[build_workflow]: https://github.com/tmonck/clean_up_snapshots/actions/workflows/ci.yml
[code_style_badge]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
[code_style_repo]: https://github.com/psf/black
[hacs]: https://hacs.xyz/
[hacs_badge]: https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge
[hacs_custom_components]: https://github.com/custom-components/hacs
[home_assistant_settings]: https://my.home-assistant.io/redirect/config
[home_assistant_devices_services]: https://my.home-assistant.io/redirect/integrations
[my_config_flow_start_badge]: https://my.home-assistant.io/badges/config_flow_start.svg
[my_hacs_repo_badge]: https://my.home-assistant.io/badges/hacs_repository.svg
[my_integration_config_flow]: https://my.home-assistant.io/redirect/config_flow_start/?domain=clean_up_snapshots_service
[my_integration_lookup]: https://my.home-assistant.io/redirect/hacs_repository/?owner=tmonck&repository=clean_up_snapshots&category=integration
[release_badge]: https://img.shields.io/github/v/release/tmonck/clean_up_snapshots?color=41BDF5&style=for-the-badge
[releases_page]: https://github.com/tmonck/clean_up_snapshots/releases
[supervisor]: https://www.home-assistant.io/integrations/hassio
