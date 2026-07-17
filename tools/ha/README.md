# Home Assistant helper scripts

Run these from PowerShell on Windows from this folder:

```powershell
cd H:\tools\ha
```

## Token setup

Most scripts call the Home Assistant REST API at `http://192.168.1.8:8123`.

Create a Long-Lived Access Token in Home Assistant:

```text
Profile -> Security -> Long-lived access tokens -> Create token
```

Then choose one option.

For the current PowerShell session only:

```powershell
$env:HA_TOKEN = 'paste-token-here'
```

Or create a local token file next to these scripts:

```powershell
Set-Content -Path .\.ha_token -Value 'paste-token-here'
```

`.ha_token` is ignored by Git.

## Main workflow

After editing YAML:

```powershell
.\ha-check.ps1
.\ha-reload-automations.ps1
.\ha-reload-autogen.ps1
```

## API-based commands

```powershell
.\ha-check.ps1
.\ha-restart.ps1
.\ha-reload-automations.ps1
.\ha-reload-scripts.ps1
.\ha-reload-scenes.ps1
.\ha-reload-templates.ps1
.\ha-reload-core-config.ps1
.\ha-reload-all.ps1
.\ha-reload-autogen.ps1
```

## SSH-based commands

These use the SSH alias `home-192-168-1-8`.

```powershell
.\ha-logs.ps1
.\ha-start.ps1
.\ha-stop.ps1
```

Note: `ha-start.ps1` and `ha-stop.ps1` require the SSH environment to have Supervisor CLI access. If they fail with `unauthorized: missing or invalid API token`, use the Home Assistant UI or a host-level shell instead.
