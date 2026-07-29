# Home Assistant PC Power Requests Notes

## Scope

This repository contains the Home Assistant configuration for the house. The PC sleep-blocking monitor added on 2026-07-29 reports Windows `powercfg /requests` output from the TAIS PC into Home Assistant through HASS.Agent Satellite Service and MQTT discovery.

Do not commit Home Assistant secrets, HASS.Agent tokens, SMB passwords, MQTT passwords, browser session data, or local service logs.

## PC Power Requests Integration

Windows source scripts are stored on the PC at:

- `C:\ProgramData\HomeAssistantPowerRequests\Get-PowerRequestsState.ps1`
- `C:\ProgramData\HomeAssistantPowerRequests\Get-PowerRequestsDetails.ps1`

Repo copies of those scripts and the installer are in:

- `tools/homeassistant-power-requests\Get-PowerRequestsState.ps1`
- `tools/homeassistant-power-requests\Get-PowerRequestsDetails.ps1`
- `tools/homeassistant-power-requests\Install-SatellitePowerRequestSensors.ps1`

The installer configures `HASS.Agent Satellite Service` with two `PowershellSensor` entries that run every 30 seconds:

- `tais_pc_power_sleep_block_state`
- `tais_pc_power_sleep_block_details`

Home Assistant MQTT discovery exposes them as:

- `sensor.tais_pc_satellite_tais_pc_power_sleep_block_state`
- `sensor.tais_pc_satellite_tais_pc_power_sleep_block_details`

The Home Assistant template binary sensor is defined in:

- `packages/others/tais_pc_power_requests.yaml`

Final entity:

- `binary_sensor.tais_pc_sleep_blocked`

Expected behavior:

- `on` when `powercfg /requests` contains a blocking request line such as `[PROCESS]`, `[DRIVER]`, or `[SERVICE]`
- `off` when no blocking request exists
- attribute `requests` contains the compact blocking request details

## Operational Checks

Check the Windows service:

```powershell
Get-Service -Name 'HASS.Agent Satellite Service'
```

Check the live local parser manually from an elevated shell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\ProgramData\HomeAssistantPowerRequests\Get-PowerRequestsState.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File C:\ProgramData\HomeAssistantPowerRequests\Get-PowerRequestsDetails.ps1
```

Reload Home Assistant template entities after changing the package:

```powershell
POST /api/services/template/reload
```

Run Home Assistant config validation before restarting:

```powershell
POST /api/config/core/check_config
```

## Dashboard

The Lovelace storage dashboard has a `PC Power Requests` entities card on the Home view. If it does not appear immediately in the browser, refresh the frontend or restart Home Assistant.
