## Installation instructions:

1. Install HACS for Home Assistant
2. Navigate to HACS Store
3. Search for "Clean up snapshots service"
4. Install
5. Restart Home Assistant
6. Generate a Long Lived Token
    1. Navigate to your profile page.
    1. At the bottom of the page you will see a section called Long-Lived Access Tokens.
    1. Click create.
    1. In the pop up give your token a name.
    1. Copy the token from the following pop up **This will not be saved anywhere so put it somehwere you can find it again**
7. Copy resulting token input this in configuration.yaml:

```yaml
clean_up_snapshots_service:
  host: {{the url to access your homeassistant instance}}
  token: {{Long-Lived Access token}}
  number_of_snapshots_to_keep: 3
```

8. Restart Home Assistant
9. Look for the new clean_up_snapshots_service.clean_up Services in services.

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
---
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

