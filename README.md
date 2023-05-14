

# Clean up snapshots

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)
[![CI](https://github.com/tmonck/clean_up_snapshots/actions/workflows/ci.yml/badge.svg)](https://github.com/tmonck/clean_up_snapshots/actions/workflows/ci.yml)

This Home Assistant extension exposes a service to automate the clean up of old backups.

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Prerequisites](#prerequisites)
- [HACS installation:](#hacs-installation)
- [Use in automations](#use-in-automations)
- [Configuration:](#configuration)

<!-- markdown-toc end -->

## Prerequisites

To be able to use this extension you must must have the following integrations enabled and configured within your Home Assistant installation.

- [HTTP][0]
- [API][1]

To manage the installation and upgrades easier it's recommendated to use [HACS][2].

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=tmonck&repository=clean_up_snapshots&category=integration)

## HACS installation:
1. Navigate to HACS Store
2. Search for "Clean up snapshots service"
3. Click on the service, and then on _DOWNLOAD_
4. Restart Home Assistant (Settings > System > Restart)
5. Add the integration via one of the options below:
    1. Add it via the Settings > Devices & Services > ...
    2. **:warning: Warning this is deprecated** Add the following to your configuration.yaml:
      ```yaml
      clean_up_snapshots_service:
        number_of_snapshots_to_keep: 3 # optional, default value is 0
      ```
6. Restart Home Assistant (Settings > System > Restart)
7. Look for the new `clean_up_snapshots_service.clean_up` service (Developer Tools > Services).



5. 
> **Warning**
> The setup via the configuration.yaml file is being deprecated and will be removed in a future release.
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

## Configuration:
When configuring this plugin you will need to define a the following parameter:

`number_of_snapshots_to_keep:` - (Optional) The number of snapshots you wish to retain, default is 0 (retain all)


[0]: https://www.home-assistant.io/integrations/http/
[1]: https://www.home-assistant.io/integrations/api/
[2]: https://hacs.xyz/
