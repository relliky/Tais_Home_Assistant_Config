import random


IOS_THEMES = [
  'ios-dark-mode-blue-red',
  'ios-dark-mode-dark-blue',
  'ios-dark-mode-dark-green',
  'ios-dark-mode-light-blue',
  'ios-dark-mode-light-green',
  'ios-dark-mode-orange',
  'ios-dark-mode-red'
]


def default_dashboard_settings():
  return {
    "dashboard_default_root": "/Uninitliazed_dashboard_root",
    "dashboard_view_name": "Uninitliazed_dashboard_view_name",
    "room_icon": "Uninitliazed_room_icon",
    "room_theme": IOS_THEMES[random.randint(0, 6)],
  }


def dashboard_root_for_type(dashboard_type, dashboard_default_root):
  return (
    dashboard_default_root if dashboard_type == "default" else
    "dashboard-tablet" if dashboard_type == "tablet" else
    "dashboard-mobile" if dashboard_type == "mobile" else
    "uninitialized_dashboard_root"
  )
