# Python Templates

This directory contains the Python generator used to build Home Assistant
package YAML and Lovelace dashboard YAML from room-specific Python classes.

## Main Files

- `gen_config_yaml.py` is the main generator.
- `generator_io.py` contains output path configuration and YAML/JSON writing
  helpers.
- `generator_cli.py` contains command-line argument parsing and dashboard flag
  interpretation.
- `entity_naming.py` contains entity ID, postfix, display-name, and automation
  alias naming helpers.
- `dashboard_generator.py` contains the overall Lovelace dashboard aggregation
  logic.
- `ha_entity_registry.py` contains helper functions for inspecting and cleaning
  Home Assistant's `core.entity_registry`.
- `room_registry.py` defines the room order used by package and dashboard
  generation.
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
python -m unittest discover -s H:\python_templates\tests
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

Recommended next steps:

1. Split `RoomBase` only after the generated-output tests are strong.

Avoid large mechanical rewrites until the generator can produce and compare all
outputs in a temporary directory.

## Notes

- Python 3.14 is currently installed on the Windows environment and works with
  the test suite.
- PyYAML is required.
- The generator currently uses Python 3.9+ dictionary merge syntax.
- Some regular expressions trigger warnings on newer Python versions because
  they are not raw strings. These warnings should be cleaned up in a separate
  low-risk commit.
