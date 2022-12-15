
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



from datetime import datetime as dt
from datetime import timezone as timezone

# Get the number of seconds this entity has been current state 
@service
def get_sec_of_cur_state(entity_name):
  last_time_cur_entity_changed = state.get(entity_name + '.last_changed')
  return (dt.now(tz=timezone.utc) - last_time_cur_entity_changed).total_seconds()


@service
def alexa_set_tv(action=None, brightness='Standard', power='on'):
    
    # Get TV id for the room alexa is called
    alexa_room_tv = 'media_player.' + sensor.last_alexa + '_tv'
    
    if action == 'brightness':
        # Set brightness if TV exists and is on
        samsungtv_smart.select_picture_mode(entity_id=alexa_room_tv, picture_mode=brightness)
    elif action == 'power':
        # Turn on/off TV
        if power == 'on':
            homeassistant.turn_on( entity_id=alexa_room_tv, power='on')
        else:
            homeassistant.turn_off(entity_id=alexa_room_tv, power='off')

@service
def set_room_heat_temperature(room=None, temperature=None ):
    if room != None and temperature != None:
      climate.set_temperature( entity_id = room,
                               hvac_mode = 'heat',
                               temperature = temperature);

