COLOR_VALUES = {
  'transparent': "rgba(245, 245, 245, 0)",
  'more_transparent_grey': "rgba(10, 10, 10, 0.4)",
  'less_transparent_grey': "rgba(10, 10, 10, 0.7)",
  'most_transparent_white': "rgba(245, 245, 245, 0.1)",
  'more_transparent_white': "rgba(245, 245, 245, 0.3)",
  'less_transparent_white': "rgba(245, 245, 245, 0.9)",
  'dark_grey': "rgba(100, 100, 100, 1)",
  'light_grey': "rgba(220, 220, 220, 1)",
  'ios_yellow': "rgba(253,204,0,1)",
}


def get_color(color):
  return COLOR_VALUES.get(color, color)
