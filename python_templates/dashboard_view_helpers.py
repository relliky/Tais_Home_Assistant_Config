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
