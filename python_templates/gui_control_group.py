SCENE_CONTROL_NAMES = [
  'intense light summer',
  'moderate light outdoor',
  'low light outdoor',
  'sleep mode',
]


def scene_control_entities(
  ceiling_lights,
  lamps,
  leds,
  curtains,
  ceiling_light_control_when,
  lamp_control_when,
  led_control_when,
  curtain_control_when,
):
  entities = []

  for control_name in SCENE_CONTROL_NAMES:
    entities += [ceiling_light_control_when[control_name]] if len(ceiling_lights) > 0 else []
    entities += [lamp_control_when[control_name]] if len(lamps) > 0 else []
    entities += [led_control_when[control_name]] if len(leds) > 0 else []
    entities += [curtain_control_when[control_name]] if len(curtains) > 0 else []

  return entities
