# Clean up snapshots

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![CI](https://github.com/tmonck/clean_up_snapshots/actions/workflows/ci.yml/badge.svg)](https://github.com/tmonck/clean_up_snapshots/actions/workflows/ci.yml)

This Home Assistant extension exposes a service to automate the clean up of old snapshots.

## Prerequisites

To be able to use this extension you must must have the following integrations enabled and configured within your Home Assistant installation.

- [HTTP][0]
- [API][1]

To manage the installation and upgrades easier it's recommendated to use [HACS][2].

## HACS installation:

1. Navigate to HACS Store
2. Search for "Clean up snapshots service"
3. Click on the service, and then on _DOWNLOAD_
4. Restart Home Assistant (Settings > System > Restart)
5. Add the following to your configuration.yaml:
```yaml
clean_up_snapshots_service:
  number_of_snapshots_to_keep: 3 # optional, default value is 0
```
6. Restart Home Assistant (Settings > System > Restart)
7. Look for the new `clean_up_snapshots_service.clean_up` service (Developer Tools > Services).

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
      # number_of_backups_to_keep: 7
```

## Configuration:
When configuring this plugin you will need to define a the following parameter:

`number_of_snapshots_to_keep:` - (Optional) The number of snapshots you wish to retain, default is 0 (retain all)


[0]: https://www.home-assistant.io/integrations/http/
[1]: https://www.home-assistant.io/integrations/api/
[2]: https://hacs.xyz/
