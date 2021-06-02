# Clean up snapshots

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

This Home Assistant extension exposes a service to automate the clean up of old snapshots.

## Prerequisites

To be able to use this extension you must must have the following integrations enabled and configured within your Home Assistant installation.

- [HTTP][0]
- [API][1]

To manage the installation and upgrades easier it's recommendated to use [HACS][2].

## HACS installation:

1. Navigate to HACS Store
2. Under the Integrations tab, click the add button (the one with a plus sign)
3. Search for "Clean up snapshots service"
4. Click on the service, and then on _Install this repository in HACS_
5. Restart Home Assistant (Configuration > Server Controls > Restart)
6. Generate a Long Lived Token
    1. Navigate to your [profile page](https://www.home-assistant.io/docs/authentication/#your-account-profile).
    1. At the bottom of the page you will see a section called Long-Lived Access Tokens.
    1. Click _Create token_.
    1. In the pop up give your token a name.
    1. Copy the token from the following pop up **This will not be saved anywhere so put it somewhere you can find it again**
7. Copy resulting token input this in configuration.yaml:
```yaml
clean_up_snapshots_service:
  host: !secret base_url
  token: !secret clean_up_token
  number_of_snapshots_to_keep: 3
```

8. Restart Home Assistant (Configuration > Server Controls > Restart)
9. Look for the new `clean_up_snapshots_service.clean_up` service (Developer Tools > Services).

## Consumption in automations
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
When configuring this plugin you will need to define a few parameters.

1. `host (Required)` - This is the url to access your home assisant instance. The url can have a trailing `/` if you desire. It can also be `https` or `http`
   1. https://hassio:8123
   1. https://hassio:8123/
2. `token (Required)` - The Long-Lived Access token you generated during installation.
3. `number_of_snapshots_to_keep (Optional - default value is 3)` - The number of snapshots you wish to retain.
4. `use_ssl_with_ip_address (Optional - default value is False)` - If you wish to verify the SSL Certificate for your home assistant instance and you are using an IP Address for your url then you need to set this to `True`.

### Example configurations

``` yaml
clean_up_snapshots_service:
  host: !secret base_url
  token: !secret clean_up_token
  number_of_snapshots_to_keep: 3

clean_up_snapshots_service:
  host: "https://hassio:8123"
  token: mytoken
  number_of_snapshots_to_keep: 3

clean_up_snapshots_service:
  host: http://hassio:8123
  token: mytoken
  number_of_snapshots_to_keep: 3

clean_up_snapshots_service:
  host: http://hassio:8123/
  token: mytoken
  number_of_snapshots_to_keep: 3

clean_up_snapshots_service:
  host: https://1.1.1.1:8123
  token: mytoken
  number_of_snapshots_to_keep: 3
  use_ssl_with_ip_address: True
```
*Note* When using hassio as your domain you may need to have your url be hassio.lan:8123
[See issue #12](https://github.com/tmonck/clean_up_snapshots/issues/12)


[0]: https://www.home-assistant.io/integrations/http/
[1]: https://www.home-assistant.io/integrations/api/
[2]: https://hacs.xyz/
