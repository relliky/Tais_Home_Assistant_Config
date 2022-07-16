@service
def hello_world(action=None, id=None):
    """hello_world example using pyscript."""
    
    #################################################
    # Print function needs to be done by (log.info) #
    #################################################
    log.info(f"hello world: got action {action} id {id}")
    
    if action == "turn_on" and id is not None:
        light.turn_on(entity_id=id, brightness=255)
    elif action == "fire" and id is not None:
        event.fire(id, param1=12, pararm2=80)


#@service
#def turn_off_gaming_pc_based_on_a_timer():
#    
#    # Duration of gaming_pc state
#    from datetime import datetime as dt
#    from datetime import timezone as timezone
#
#    num_seconds_ago = (dt.now(tz=timezone.utc) - switch.gaming_pc.last_changed).total_seconds()
#    num_hours_ago  = int(num_seconds_ago/3600)
#    
#    # Setting of timer
#    timer = int(float(input_number.gaming_pc_shutdown_timer_in_hour))
#    
#    # Gaming PC is On for specificed time, turn off pc
#    if num_hours_ago >= timer and switch.gaming_pc == 'on':
#        switch.gaming_pc.turn_off()
    
@service
def alexa_set_tv_brightness( brightness='Standard' ):
   
    # Get TV id for the room alexa is called
    alexa_room_tv = 'media_player.' + sensor.last_alexa + '_tv'
    
    # Set brightness if TV exists and is on
    samsungtv_smart.select_picture_mode(entity_id=alexa_room_tv, picture_mode=brightness)



@service
def set_room_heat_temperature(room=None, temperature=None ):
    if room != None and temperature != None:
      climate.set_temperature( entity_id = room,
                               hvac_mode = 'heat',
                               temperature = temperature);











