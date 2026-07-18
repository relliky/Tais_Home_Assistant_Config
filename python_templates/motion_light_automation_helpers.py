def curtain_scene_choose(condition_list_is, call_scene_service, do_nothing_service):
  return {
    "alias": 'If it is intense light summer',
    "if": condition_list_is('intense light summer'),
    "then": call_scene_service('curtain states when intense light summer'),
    "else": {
      "alias": 'If it is moderate light outdoor',
      "if": condition_list_is('moderate light outdoor'),
      "then": call_scene_service('curtain states when moderate light outdoor'),
      "else": {
        "alias": 'If it is low light outdoor',
        "if": condition_list_is('low light outdoor'),
        "then": call_scene_service('curtain states when low light outdoor'),
        "else": {
          "alias": 'If it is sleep mode',
          "if": condition_list_is('sleep mode'),
          "then": call_scene_service('curtain states when sleep mode'),
          "else": {
            "alias": 'Default',
            **do_nothing_service()
          }
        }
      }
    }
  }


def light_scene_choose(condition_list_is, call_scene_service, do_nothing_service):
  return {
    "alias": 'If it is bright morning',
    "if": condition_list_is('intense light summer'),
    "then": call_scene_service('light states when intense light summer'),
    "else": {
      "alias": 'If it is bright afternoon',
      "if": condition_list_is('moderate light outdoor'),
      "then": call_scene_service('light states when moderate light outdoor'),
      "else": {
        "alias": 'If it is bright afternoon',
        "if": condition_list_is('low light outdoor'),
        "then": call_scene_service('light states when low light outdoor'),
        "else": {
          "alias": 'If it is bright afternoon',
          "if": condition_list_is('sleep mode'),
          "then": call_scene_service('light states when sleep mode'),
          "else": {
            "alias": 'Default',
            **do_nothing_service()
          }
        }
      }
    }
  }
