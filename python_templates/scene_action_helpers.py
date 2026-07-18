def simple_room_scene_actions(
    scene_name,
    lamps,
    ceiling_lights,
    leds,
    tvs,
    room_entity,
    set_service,
):
  if scene_name == 'All White':
    return [
      set_service(lamps, "on"),
      set_service(ceiling_lights, "on"),
      set_service(leds, "on"),
      set_service(tvs, tv_brightness=3),
    ], True
  if scene_name == 'Ceiling Light White':
    return [
      set_service(lamps, "off"),
      set_service(leds, "off"),
      set_service(ceiling_lights, "on"),
      set_service(tvs, tv_brightness=3),
    ], True
  if scene_name == 'Lamp LED White':
    return [
      set_service(ceiling_lights, "off"),
      set_service(lamps, "on"),
      set_service(leds, "on"),
    ], True
  if scene_name == 'LED White':
    return [set_service(leds, "on")], True
  if scene_name == 'Hue':
    return [
      {
        "service": "pyscript.turn_rgb_light",
        "data": {
          "light_list": lamps + ceiling_lights + leds,
          "state": 'off',
          "rgb": 'non_rgb_only',
        },
      },
      {
        "service": "pyscript.turn_rgb_light",
        "data": {"light_list": lamps + ceiling_lights + leds},
      },
      set_service(tvs, tv_brightness=2),
    ], False
  if scene_name == 'Night Mode':
    return [
      {
        "service": "homeassistant.turn_on",
        "entity_id": "scene." + room_entity + "_night_mode",
      },
      set_service(tvs, tv_brightness=2),
    ], True
  if scene_name == 'Dark Night Mode':
    return [
      {
        "service": "homeassistant.turn_on",
        "entity_id": "scene." + room_entity + "_dark_night_mode",
      },
      set_service(tvs, tv_brightness=1),
    ], True
  if scene_name == "Sleep Mode":
    return [
      {
        "service": "homeassistant.turn_on",
        "entity_id": "scene." + room_entity + "_sleep_mode",
      }
    ], True
  if scene_name == 'All Off':
    return [
      set_service(ceiling_lights, "off"),
      set_service(lamps, "off"),
      set_service(leds, "off"),
      set_service(tvs, tv_brightness=3),
    ], True
  return None
