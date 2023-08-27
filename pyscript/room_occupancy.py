import datetime 

# Get the number of seconds this entity has been current state 
def get_sec_of_cur_state(entity_name):
  last_time_cur_entity_changed = state.get(entity_name + '.last_changed')
  return (datetime.datetime.now(tz=datetime.timezone.utc) - last_time_cur_entity_changed).total_seconds()

def now_is_before(hour, minute, second):
    return datetime.datetime.now().time() < datetime.time(hour, minute, second)
    
def now_is_after(hour, minute, second):
    return datetime.datetime.now().time() > datetime.time(hour, minute, second)
  
################################
# Room Occupancy
#
#       outside --c0---> just_entered ----c2----> stayed ---c7-----> in_sleep
#           |<----c3---------|                      |                  |
#           |<-------------------c5-----------------|<------c10--------|
#           |<----------------------------------------------c8---------|
#          |c1|             |c4|                  |c6|                |c9|
#
# State machine changing conditions:
#
# c0. outside      -> just_entered:
# c1. outside      -> outside: 
# c2. just_entered -> stayed:
# c3. just_entered -> outside:
# c4. just_entered -> just_entered
# c5. stayed       -> outside:
# c6. stayed       -> stayed:
# c7. stayed       -> in_sleep:
# c8. in_sleep     -> outside:
# c9. in_sleep     -> in_sleep
#
################################

@service
def room_occupancy_state_machine(occupancy_entity_str, 
                                 motion_str,                                 
                                 motion_on_ratio_for_x_min_str,
                                 motion_on_ratio_for_2x_min_str,
                                 room_type):
    
    #percentage_for_largely_def = 0.4
    #percentage_for_fully_def   = 0.8
    
    # Get state based on string
    cur_state                  = state.get(occupancy_entity_str)
    motion                     = state.get(motion_str)
    motion_state_lasts_for     = get_sec_of_cur_state(motion_str)
    motion_off_for             = motion_state_lasts_for if motion == 'off' else 0
    motion_on_ratio_for_x_min  = float(state.get(motion_on_ratio_for_x_min_str))
    motion_on_ratio_for_2x_min = float(state.get(motion_on_ratio_for_2x_min_str))
    motion_off_ratio_for_x_min = 1 - motion_on_ratio_for_x_min
    motion_off_ratio_for_2x_min= 1 - motion_on_ratio_for_2x_min
    nxt_state                  = ''
    stay_inside_for            = get_sec_of_cur_state(occupancy_entity_str) if cur_state == 'Stayed Inside' else 0
    now_is_sleep_time          = now_is_before(9,30,0) or now_is_after(21,0,0)
    normal_timeout             = 1 if room_type == 'landing' else 5 # other rooms timeout at 5 minutes 
    
    # Outside -> xxx
    if cur_state == 'Outside':
      
        # c0. Outside      -> Just Entered:
        #     currently on
        if motion == 'on':
            nxt_state = "Just Entered"
            
        # c1. Outside      -> Outside: 
        #     currently off for 5 Min & previously off in [0, 2x] 
        #     OR all other condition
        else:
            nxt_state = 'Outside'
            
    # Just Entered -> xxx    
    elif cur_state == 'Just Entered':      
        
        # c2. Just Entered -> Stayed Inside:
        #     currently on & previously largely on in [0,x] or [0,2x]
        if motion == 'on' and \
           (motion_on_ratio_for_x_min  >= 0.6 or
            motion_on_ratio_for_2x_min >= 0.4):
            nxt_state = "Stayed Inside"
            
        # c3. Just Entered -> Outside:
        #     (currently off for <normal_timeout> minutes) & largely off in [0,2x]
        elif motion_off_for >= normal_timeout*60 and \
             motion_off_ratio_for_2x_min >= 0.5:
               nxt_state = "Outside"
        
        # c4. just_entered -> just_entered
        #     all other conditions
        else:
            nxt_state = "Just Entered"

    # Stayed Inside -> xxx    
    elif cur_state == 'Stayed Inside':       
        
        # c7. Stayed Inside -> In Sleep:
        #     People is inside the room for an hour in the night time 
        #     would assume they are in bed and ready for sleep
        if room_type == 'bedroom' and \
           stay_inside_for > 60*60 and \
           now_is_sleep_time:
            nxt_state = "In Sleep"
                    
        # c5. Stayed Inside -> Outside:
        #     (currently off for  <normal_timeout> minutes) & largely off in [0,2x]
        elif motion_off_for >=  normal_timeout*60 and \
             motion_off_ratio_for_2x_min >= 0.7:
            nxt_state = "Outside"
        
        # c6. Stayed Inside -> Stayed Inside:
        #     all other condition
        else:
          nxt_state = "Stayed Inside"

    # In Sleep -> xxx    
    elif cur_state == 'In Sleep':       
        
        # c7. In Sleep -> Stayed Inside:
        #     Assuming people will wake up once it is not sleep time anymore
        if not now_is_sleep_time:
            nxt_state = "Stayed Inside"

        # c8. In Sleep -> Outside:
        #     No motions for an hour means people are outside during sleep time
        elif motion_off_for >= 60*60:
            nxt_state = "Outside"

        # c9. In Sleep -> In Sleep:
        else:    
            nxt_state = "In Sleep"
            
    # Set next state
    state.set(occupancy_entity_str, nxt_state)

    # Log I/O
    #log.info("cur_state                   :" + str(cur_state              ))    
    #log.info("motion                      :" + str(motion                 ))    
    #log.info("motion_state_lasts_for      :" + str(motion_state_lasts_for ))    
    #log.info("motion_off_for              :" + str(motion_off_for         ))    
    #log.info("motion_on_ratio_for_x_min   :" + str(motion_on_ratio_for_x_min ))    
    #log.info("motion_on_ratio_for_2x_min  :" + str(motion_on_ratio_for_2x_min))    
    #log.info("motion_off_ratio_for_x_min  :" + str(motion_off_ratio_for_x_min ))    
    #log.info("motion_off_ratio_for_2x_min :" + str(motion_off_ratio_for_2x_min))    
    #log.info("stay_inside_for             :" + str(stay_inside_for        ))    
    #log.info("now_is_sleep_time           :" + str(now_is_sleep_time      ))    
    #log.info("nxt_state                   :" + str(nxt_state              ))    
    
    
    
#room_occupancy_state_machine(  occupancy_entity_str=input_select.en_suite_room_occupancy,
#                               motion_str=group.en_suite_room_motion,
#                               motion_on_ratio_for_x_min_str=sensor.en_suite_room_motion_on_ratio_for_last_4_minutes,
#                               motion_on_ratio_for_2x_min_str=sensor.en_suite_room_motion_on_ratio_for_last_8_minutes,
#                               room_type=bedroom
    