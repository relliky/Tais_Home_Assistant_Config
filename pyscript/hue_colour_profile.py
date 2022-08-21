@service
def get_hue_colour_profiles():
    return {
    'hal' :    [(110,237,252), 
                (171,221,251),
                (236,97, 96),
                (237,119,104),
                (248,210,93)],
    'tyrell' : [(183,37, 246), 
                (235,82, 185),
                (240,105,204),
                (207,149,248),
                (106,229,251)],  
    'soho' :   [(234,51, 100), 
                (241,154,122),
                (237,114,141),
                (178,41, 245),
                (145,251,213)]
    }


@service
def filter_rbg_light_list(light_list=None ):
    assert isinstance(light_list, list), log.info ('input light_list '+light_list+' is not a list.')
    filter_light_list = []
    for light in light_list:
        #log.info(state.getattr(light)['supported_color_modes'])
        if light.startswith('light'):
            rgb_supported = 0
            for color_mode in state.getattr(light)['supported_color_modes']:
              rgb_supported += 1 if color_mode == 'hs'  else 0
              rgb_supported += 1 if color_mode == 'rgb' else 0
            filter_light_list += [light] if rgb_supported > 0 else []
    #log.info(filter_light_list)
    return filter_light_list

@service
def set_rgb_light_list(light_list=None, profile_name='soho'):
    assert isinstance(light_list, list), log.info ('input light_list '+light_list+' is not a list.')
    
    # Filter out lights that support colour
    light_list = filter_rbg_light_list(light_list)
    
    # Select a colour profile
    selected_colour_list = []
    for profile_name, colour_list in get_hue_colour_profiles().items():
      if profile_name == 'soho':
        selected_colour_list = colour_list
        #log.info (selected_colour_list)
        #light.master_room_lamp_2.turn_on(rgb_color = (0, 237, 252))
        #light.turn_on( entity_id = 'light.master_room_lamp_2', rgb_color = rgb_colour)

    # Picking up random colour for a light from a sepecific colour profile 
    num_of_lights = len(light_list)
    colour_index_5 = [0,1,2,3,4]
    import random
    random.shuffle(colour_index_5)
    colour_index = []
    for i in range(len(light_list)):
        colour_index += [colour_index_5[i%5]]
        
    # Turn on lights with the selected colour list
    for i in range(len(light_list)):
        rgb_colour = selected_colour_list[colour_index[i]]
        light.turn_on(entity_id=light_list[i], rgb_color=rgb_colour)









