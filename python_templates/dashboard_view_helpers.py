def build_view(view_path='', cards=None, theme="Mushroom Shadow", title=''):
  return {
    "theme": theme,
    "title": title,
    "path":  view_path,
    "subview": True,
    "badges": [],
    "cards": [] if cards is None else cards
  }


def layout_wrapper_cards(dashboard_type, cards=None):
  if dashboard_type in ['mobile', 'default']:
    return [{
        "square": False,
        "columns": 2,
        "type": "grid",
        "cards": cards}]
  elif dashboard_type == 'tablet':
    return cards

  raise TypeError( "\n" +\
    "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" + \
    "getLayoutWrapperCardList does not support dashboard_type" + str(dashboard_type) + \
    "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")


def home_navigation_card(dashboard_root, navigate_path=None):
  navigation_path = (dashboard_root + "/" + "home") if navigate_path is None else navigate_path
  return {
    "type": "custom:mushroom-template-card",
    "entity": "input_boolean.placeholder",
    "icon": "mdi:keyboard-return",
    "icon_color": "yellow",
    "primary": "HOME",
    "secondary": "",
    "layout": "vertical",
    "hold_action": {
      "action": "toggle"
    },
    "tap_action": {
      "action": "navigate",
      "navigation_path": navigation_path
    },
    "icon_tap_action": {
      "action": "navigate",
      "navigation_path": navigation_path
    },
    "card_mod": {
      "style": {
        "mushroom-state-info$": ".primary {\n  font-size: 16px !important;\n  position: relative;\n  top: 0px;\n  left: 0px;\n  overflow: visible !important;\n  white-space:  \n}\n",
        "mushroom-shape-icon$": ".shape {\n  position: relative;\n  left: 0px;\n  top: 0px;\n}\n",
        ".": ":host {\n  --mush-icon-size: 80px;\n}\n"
      }
    }
  }


def header_cards(dashboard_root, scene_card, navigate_path=None):
  return [
    home_navigation_card(dashboard_root, navigate_path=navigate_path),
    scene_card,
  ]
