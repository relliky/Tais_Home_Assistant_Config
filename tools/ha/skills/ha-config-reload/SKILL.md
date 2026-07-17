---
name: ha-config-reload
description: Generate, check, and reload this Home Assistant configuration after Codex edits files in the mounted HA config project. Use after modifying Home Assistant YAML, generated package source code such as python_templates/gen_config_yaml.py, packages, automations, scripts, scenes, templates, customize files, or related files under the config share, especially when the user asks to apply, reload, validate, regenerate, or test Home Assistant configuration changes.
---

# Home Assistant Config Reload

Use this skill after editing files in this Home Assistant config project.

The config share is mounted on Windows as `H:\`. Helper scripts live in `H:\tools\ha`.
The same config is available on the Home Assistant host as `/config`, with SSH alias `home-192-168-1-8`.

## Required Workflow

After any Home Assistant config edit:

1. If the edit touched generated-package source, regenerate generated YAML first.

Generated-package source includes:

- `H:\python_templates\gen_config_yaml.py`
- files imported by that generator, such as `H:\python_templates\HA_Composite_Card_Lib\...`
- room/device DSL changes that affect `packages/_auto_generated_packages/auto_gen_*.yaml`
- requests to "regenerate", "generate YAML", "update room config", or similar

Run generation on the Home Assistant host, not local Windows Python:

```powershell
ssh home-192-168-1-8 "cd /config && sudo -n python3 python_templates/gen_config_yaml.py -C"
```

Do not use local Windows `python3`; it may be the WindowsApps stub. Local `python` may be Python 3.8 and fail on `dict |= dict`. The remote `/config` Python has the expected runtime and filesystem ownership.

If generation fails, report the traceback and do not check or reload.

2. Run the configuration check:

```powershell
powershell -ExecutionPolicy Bypass -File H:\tools\ha\ha-check.ps1
```

3. If the check fails, report the error and do not reload.

4. If the check succeeds, reload only the affected domain when possible.

## Reload Selection

Use the narrowest matching reload script:

- Edited `automations.yaml`, `automations/`, automation packages, or files that define `automation:`:

```powershell
powershell -ExecutionPolicy Bypass -File H:\tools\ha\ha-reload-automations.ps1
```

- Edited `scripts.yaml`, `scripts/`, or files that define `script:`:

```powershell
powershell -ExecutionPolicy Bypass -File H:\tools\ha\ha-reload-scripts.ps1
```

- Edited `scenes.yaml`, `scenes/`, or files that define `scene:`:

```powershell
powershell -ExecutionPolicy Bypass -File H:\tools\ha\ha-reload-scenes.ps1
```

- Edited template sensors, template binary sensors, template triggers, or files that define `template:`:

```powershell
powershell -ExecutionPolicy Bypass -File H:\tools\ha\ha-reload-templates.ps1
```

- Edited core config such as `homeassistant:`, `customize:`, zones, groups, input helpers, or files where a narrower reload is not obvious:

```powershell
powershell -ExecutionPolicy Bypass -File H:\tools\ha\ha-reload-core-config.ps1
```

- Edited multiple domains or cannot confidently identify the affected domain:

```powershell
powershell -ExecutionPolicy Bypass -File H:\tools\ha\ha-reload-all.ps1
```

Generated room packages should be reloaded through the Home Assistant script already defined in `H:\packages\devices\system.yaml`:

```yaml
script.reload_autogen_entity
```

After regenerating `auto_gen_*.yaml`, call it via:

```powershell
powershell -ExecutionPolicy Bypass -File H:\tools\ha\ha-reload-autogen.ps1
```

Do not manually choose individual reload services for generated entities. The script already reloads min/max, filter, trend, input helpers, history stats, timers, scripts, automations, groups, and templates.

## Restart Only When Needed

Do not restart Home Assistant by default. Use restart only when a change cannot be applied by reload, such as integrations that require restart, custom components, frontend resources that need full reload, dependency changes, or when Home Assistant reports restart required:

```powershell
powershell -ExecutionPolicy Bypass -File H:\tools\ha\ha-restart.ps1
```

## Logs

If reload/check fails and more context is needed:

```powershell
powershell -ExecutionPolicy Bypass -File H:\tools\ha\ha-logs.ps1
```

## Token Handling

The helper scripts use `H:\tools\ha\.ha_token` or `$env:HA_TOKEN`. Treat `.ha_token` as secret. Do not print, copy, summarize, or commit it.

## Reporting

In the final response, state:

- which files were edited
- whether generated YAML was regenerated, and the exact command used
- whether `ha-check.ps1` passed
- which reload script or Home Assistant script ran
- whether reload succeeded
- any follow-up manual restart needed
