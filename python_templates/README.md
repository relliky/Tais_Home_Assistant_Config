# Python Templates

This directory contains the Python generator used to build Home Assistant
package YAML and Lovelace dashboard YAML from room-specific Python classes.

## Main Files

- `gen_config_yaml.py` is the main generator.
- `generator_io.py` contains output path configuration and YAML/JSON writing
  helpers.
- `package_writer.py` contains package/customize YAML write orchestration.
- `room_device_defaults.py` contains default mirror, TV, cover, window, and
  temperature-control entity builders.
- `generator_cli.py` contains command-line argument parsing and dashboard flag
  interpretation.
- `entity_naming.py` contains entity ID, postfix, display-name, and automation
  alias naming helpers.
- `entity_declaration_builders.py` contains small entity/group/automation
  declaration builders.
- `sensor_declaration_builders.py` contains battery, temperature, template, and
  filter sensor declaration builders.
- `entity_interface_defaults.py` contains the default entity-interface
  containers used during room generation.
- `configured_entity_filter.py` contains filtering for generated declarations
  guarded by a `configured` flag.
- `automation_helpers.py` contains small Home Assistant trigger, action, and
  condition dict builders.
- `occupancy_state_machine.py` contains the room occupancy choose/action
  generation logic.
- `occupancy_ratio_sensor.py` contains history-stats occupancy ratio sensor
  config builders.
- `dashboard_colors.py` contains dashboard CSS color aliases.
- `dashboard_card_mod.py` contains Lovelace `card_mod` style builders.
- `dashboard_settings.py` contains default dashboard settings, dashboard root
  selection, and theme selection.
- `dashboard_restrictions.py` contains Lovelace restriction-card wrappers and
  exemption user IDs.
- `dashboard_view_helpers.py` contains small Lovelace view and layout wrapper
  helpers.
- `dashboard_generator.py` contains the overall Lovelace dashboard aggregation
  logic.
- `ha_entity_registry.py` contains helper functions for inspecting and cleaning
  Home Assistant's `core.entity_registry`.
- `message_helpers.py` contains shared warning, error, and info output helpers.
- `room_registry.py` defines the room order used by package and dashboard
  generation.
- `room_config_defaults.py` contains default room feature flags and initial
  room metadata values.
- `room_properties.py` contains derived room metadata such as entity name,
  dashboard path, room type, and west-facing-window classification.
- `room_scene_defaults.py` contains default scene-control entities and internal
  scene state values.
- `room_remote_entities.py` contains default remote button and wall-switch
  entity list builders.
- `room_motion_entities.py` contains default motion, occupancy, and occupancy
  override entity builders.
- `room_light_entities.py` contains default light entity, adaptive-lighting,
  and light-control config builders.
- `room_time_settings.py` contains default sleep-time and light-time settings.
- `rooms.py` contains room-specific classes such as `MasterRoom`, `Kitchen`,
  `LivingRoom`, and `Study`.
- `auto_gen_overall_dashboard.yaml` is the generated Lovelace dashboard YAML.
- `tests/` contains unit tests and generated YAML consistency baselines.
- `HA_Composite_Card_Lib/` contains helper code used while building dashboard cards.

## What `gen_config_yaml.py` Does

The generator has three main responsibilities:

1. Build room package YAML under `../packages/_auto_generated_packages/auto_gen_*.yaml`.
2. Build Home Assistant customize YAML under `../packages/auto_gen_customize_*.yaml`.
3. Build the overall Lovelace dashboard YAML at `auto_gen_overall_dashboard.yaml`.

It also has utility functions for checking Home Assistant's
`.storage/core.entity_registry` for duplicated generated entities.

## Code Shape

`RoomBase` contains the shared generation logic for:

- entity naming and helper methods
- device declarations
- input helpers, groups, sensors, timers, and scripts
- automation generation
- occupancy state machine generation
- dashboard cards and views
- generated YAML file writing

Room-specific classes such as `MasterRoom`, `Kitchen`, `LivingRoom`, and
`Study` override small pieces of `RoomBase` to declare room-specific devices,
features, automations, and dashboard settings.

`Dashboard` combines room dashboard views into the overall Lovelace dashboard.

## Safe Change Workflow

Treat generated YAML as the compatibility contract. Home Assistant should keep
receiving the same YAML structure unless a behavior change is intentional.

Recommended workflow:

1. Run the tests before changing the generator.
2. Make one small refactor.
3. Run the tests again.
4. Inspect any generated YAML diff before committing.
5. Commit each safe step separately.

Test command:

```powershell
py -3.14 -m unittest discover -s H:\python_templates\tests
```

Common dashboard-only generation command:

```bash
python3 /ha_config/python_templates/gen_config_yaml.py -C -dy -R
```

That command skips package generation (`-R`), skips entity-registry checking
(`-C`), and writes dashboard YAML (`-dy`). Without `-dm` or `-dt`, it uses the
default dashboard type.

## YAML Consistency Baseline

`tests/baseline_generated/` stores snapshots of generated YAML files. The
consistency test loads both the baseline YAML and the current generated YAML
with PyYAML, then compares their parsed structures.

This catches changes that would affect Home Assistant behavior while avoiding
false failures for harmless formatting differences.

The baseline should only be updated when an intentional generated YAML behavior
change is made and manually reviewed.

`test_temp_output_generation.py` verifies that package and customize YAML can be
generated into a temporary output directory and still match the baseline
structure. Dashboard YAML is currently checked for successful generation and
parseability, but not yet baseline equality because the current dashboard
generator output does not reproduce the checked-in dashboard snapshot exactly.

## Refactoring Status

Completed foundations:

1. Keep file writing and output paths centralized.
2. Add support for generating into a temporary output directory.
3. Extend tests so they can generate into that temporary directory and compare
   package/customize YAML against the baseline.
4. Split command-line parsing and generation orchestration out of `main()`.
5. Move entity-registry inspection helpers into their own module.
6. Move dashboard generation into its own module.
7. Move package/dashboard room ordering into its own module.
8. Move room-specific classes into a `rooms.py` module.
9. Move output path and YAML/JSON writing helpers into their own module.
10. Move CLI parsing helpers into their own module.
11. Move entity naming helpers into their own module.
12. Move small automation trigger/action/condition helpers into their own
    module.
13. Move dashboard color aliases into their own module.
14. Move shared message helpers into their own module.
15. Move occupancy state machine generation into its own module.
16. Move small entity declaration builders into their own module.
17. Move configured entity filtering into its own module.
18. Move small dashboard view/layout helpers into their own module.
19. Move dashboard restriction-card helpers into their own module.
20. Move package/customize YAML writing orchestration into its own module.
21. Move default dashboard settings into their own module.
22. Move Lovelace `card_mod` style builders into their own module.
23. Move derived room metadata helpers into their own module.
24. Move default room time settings into their own module.
25. Move default remote button and wall-switch entities into their own module.
26. Move default mirror, TV, cover, and window entities into their own module.
27. Move default temperature-control entities into the room device defaults
    module.
28. Move default motion, occupancy, and occupancy override entities into their
    own module.
29. Move default light entities, adaptive-lighting config, and light-control
    entities into their own module.
30. Move entity-interface container defaults into their own module.
31. Move default scene-control entities into their own module.
32. Move occupancy ratio sensor config generation into its own module.
33. Move default room config flags into their own module.
34. Move dashboard root selection into dashboard settings.
35. Move battery, temperature, template, and filter sensor declaration builders
    into their own module.

Recommended next steps:

1. Split `RoomBase` only after the generated-output tests are strong.

Avoid large mechanical rewrites until the generator can produce and compare all
outputs in a temporary directory.

## Notes

- Python 3.14 is currently installed on the Windows environment and works with
  the test suite.
- PyYAML is required.
- The generator currently uses Python 3.9+ dictionary merge syntax.
- Regex strings have been cleaned up so `gen_config_yaml.py` compiles under
  Python 3.14 without `SyntaxWarning`.
