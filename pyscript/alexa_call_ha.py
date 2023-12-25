@service
def alexa_call_ha_script(script_index=None):
    # Get room entity that calls Alexa
    room = sensor.last_alexa
    
    if script_index in [1]:
        script.do_nothing()
    elif script_index in [6,7]:
        target_action(room, 'curtain', 'on' if script_index == 6 else 'off') 
    elif script_index in [8,9]:
        target_action(room, 'blind',   'on' if script_index == 8 else 'off') 
    elif script_index in [10,11,12,13,14,15,16,17,18]:
        # These commands are not supported and deprecated
        pass
    elif script_index in [19,20,21,22]:
        target_action(room, 'tv_brightness',  'Dynamic'  if script_index == 19 else \
                                              'Standard' if script_index == 20 else \
                                              'Natural'  if script_index == 21 else \
                                              'Movie') 
    elif script_index in [23,24]:
        target_action('whole_home', 'gaming_pc', 'on' if script_index == 23 else 'off')
    elif script_index in [25]:
        # These commands are not supported and deprecated
        script.do_nothing()        
    elif script_index in [26,27]:
        target_action(room, 'tv',   'on' if script_index == 27 else 'off') 
        
@service        
def target_action(room, target=None, state=None):

    log.info('room=' + room + ', target=' + target, ', state=' + state)

    if room == 'whole_home':
        if target == 'gaming_pc':
            if state == 'on':
                homeassistant.turn_on( entity_id='switch.gaming_pc')
            else:
                homeassistant.turn_off(entity_id='switch.gaming_pc')
            return
    
    if target in ['tv', 'tv_brightness']:
        room_tv = 'media_player.' + room + '_tv'

        if target == 'tv_brightness':
            # Set brightness if TV exists and is on
            samsungtv_smart.select_picture_mode(entity_id=room_tv, picture_mode=state)
            return
        elif target == 'tv':
            # Turn on/off TV
            if state == 'on':
                homeassistant.turn_on( entity_id=room_tv)
            else:
                homeassistant.turn_off(entity_id=room_tv)
        return

    # Open/Close curtains    
    if target in ['curtain', 'blind']:    
        room_cover = 'cover.' + room + '_' + target
        if state == 'on':
            cover.open_cover( entity_id=room_cover)
        else:
            cover.close_cover(entity_id=room_cover)
        return
    

    
#          {% if   script_brightness == 1 %}
#              script.do_nothing                
#
#          {% elif script_brightness == 6 %}
#              script.master_room_open_curtain                
#              
#          {% elif script_brightness == 7 %}
#              script.master_room_close_curtain                 
#
#          {% elif script_brightness == 8 %}
#              script.master_room_open_blind                
#              
#          {% elif script_brightness == 9 %}
#              script.master_room_close_blind
#              
#          {% elif script_brightness == 10 %}
#              script.master_room_tv_sleep_timer_start
#
#          {% elif script_brightness == 11 %}
#              script.find_tais_iphone_13
#
#          {% elif script_brightness == 12 %}
#              script.find_tais_iphone_8
#
#          {% elif script_brightness == 13 %}
#              script.find_tais_iphone_6
#
#          {% elif script_brightness == 14 %}
#              script.find_tais_ipad
#
#          {% elif script_brightness == 15 %}
#              script.find_tais_macbook_air
#
#          {% elif script_brightness == 16 %}
#              script.find_kes_iphone_11
#
#          {% elif script_brightness == 17 %}
#              script.find_kes_iphone_8
#
#          {% elif script_brightness == 18 %}
#              script.find_kes_macbook_air
#
#          {% elif script_brightness == 19 %}
#              script.alexa_set_tv_brightness_to_dynamic
#
#          {% elif script_brightness == 20 %}
#              script.alexa_set_tv_brightness_to_standard
#
#          {% elif script_brightness == 21 %}
#              script.alexa_set_tv_brightness_to_natural
#
#          {% elif script_brightness == 22 %}
#              script.alexa_set_tv_brightness_to_movie
#
#          {% elif script_brightness == 23 %}
#              script.turn_on_gaming_pc
#
#          {% elif script_brightness == 24 %}
#              script.turn_off_gaming_pc
#
#          {% elif script_brightness == 25 %}
#              script.doorbell_notify_ha_users
#
#          {% elif script_brightness == 26 %}
#              script.alexa_turn_off_tv
#
#          {% elif script_brightness == 27 %}
#              script.alexa_turn_on_tv
#                