import dashboard_colors


def _get_color(color):
  return dashboard_colors.get_color(color)


def build_card_mod(style='background_color_select', card_type=None, color=None, support_dark_mode=True):
  css_variable = ""

  if style == 'background_color_select':
    css_variable += ":host { --ha-card-background:" + _get_color(color) + ";}\n"

  elif style == 'ios16_toggle':
    entity_is_on_condition = " (states(config.entity) in ['on']) " + \
                                ("and (states('sun.sun') != 'below_horizon')" if support_dark_mode == True else '')

    # Make card background white if on, dark if off.
    css_variable += (":host {\n"
    "--ha-card-background:    {% if" + entity_is_on_condition + "%} " + _get_color("less_transparent_white") + "  {% else  %} " + _get_color("more_transparent_grey") + "  {% endif %};\n"
    "--primary-text-color:    {% if" + entity_is_on_condition + "%} black                                            {% else  %} white                                           {% endif %};\n"
    "--secondary-text-color : {% if" + entity_is_on_condition + "%} " + _get_color("dark_grey") +                "{% else  %} " + _get_color("light_grey") +             " {% endif %};\n"
    ";}\n")

    # Make icon a bit larger, similar to ios 16.
    css_variable += ("ha-card > mushroom-card > mushroom-state-item > mushroom-shape-icon > ha-state-icon {\n"
    "--mdc-icon-size: 0.6em;"
    ";}\n")

    # Make icon inner white if on, outter dark if off.
    if card_type == 'custom:mushroom-light-card':
        css_variable +=  "ha-card > mushroom-card > mushroom-state-item > mushroom-shape-icon {"       + " \n" + \
          "--icon-color-disabled:   " + _get_color(color)                                           + ";\n" + \
          "--shape-color-disabled:  " + _get_color("more_transparent_grey")                         + ";\n" + \
          "--icon-color:            " + _get_color("white")                                         + ";\n" + \
          "--shape-color:            {% if state_attr(config.entity, 'color_mode') == 'color_temp' %}" + " \n" + \
                                        _get_color(color)                                           + " \n" + \
                                    "{% else  %}"                                                      + " \n" + \
                                    "   rgb{{state_attr(config.entity, 'rgb_color')}}"                 + " \n" + \
                                    "{% endif%}"                                                       + ";\n" + \
          "}\n"

    else:
      css_variable += ( "ha-card > mushroom-card > mushroom-state-item > mushroom-shape-icon {\n"
        "--icon-color-disabled:  " + _get_color(color)            + ";\n"
        "--shape-color-disabled: " + _get_color("more_transparent_grey") + ";\n"
        "--icon-color:           " + _get_color("white")                 + ";\n"
        "--shape-color:          " + _get_color(color)            + ";\n"
        "}\n")

    # Make light card brightness slider color same as the light color if it is in RGB, otherwise use ios_yellow.
    if card_type == 'custom:mushroom-light-card':
        css_variable +=  "ha-card > mushroom-card > div > mushroom-light-brightness-control {"         + " \n" + \
          "--slider-color:           {% if state_attr(config.entity, 'color_mode') == 'color_temp' %}" + " \n" + \
                                        _get_color(color)                                           + " \n" + \
                                    "{% else  %}"                                                      + " \n" + \
                                    "   rgb{{state_attr(config.entity, 'rgb_color')}}"                 + " \n" + \
                                    "{% endif%}"                                                       + ";\n" + \
          "--slider-bg-color:        {% if state_attr(config.entity, 'color_mode') == 'color_temp' %}" + " \n" + \
                                        "{{ '" + _get_color(color) + "' | regex_replace(',([\\d\\.])+\\)$', ',0.2)') }}" + " \n" + \
                                    "{% else  %}"                                                      + " \n" + \
                                    "   rgba{{(state_attr(config.entity, 'rgb_color')|string)[0:-1]}}, 0.2)"  + " \n" + \
                                    "{% endif%}"                                                       + ";\n" + \
          "}\n"

    # Make bottom buttons background more visiable in white card and default in dark card.
    if card_type == 'custom:mushroom-light-card':
      for index in [2,3]:
        css_variable += "" + \
          "ha-card > mushroom-card > div > mushroom-button:nth-child(" + str(index) + ") {"
        css_variable += "" + \
          "  --bg-color: {% if " + entity_is_on_condition + " %} " + _get_color("less_transparent_white") + " {% else %} rgba(var(--rgb-primary-text-color), 0.05)" +  " {% endif %};" + \
          "}\n"

  else:
    raise TypeError( "\n" +\
        "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" + \
        "getCardMod does not support style = " + style + \
        "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n")

  return {
    "card_mod": {
      "style":  css_variable
    }
  }
