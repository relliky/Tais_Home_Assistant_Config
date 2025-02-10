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
#           |------------------------c11------------------------------>|
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
                                 sleep_time,
                                 turn_to_outside_when_no_motion,
                                 inside_to_sleep_timeout,
                                 inside_to_outside_timeout,
                                 sleep_to_outside_timesout):
    
    #percentage_for_largely_def = 0.4
    #percentage_for_fully_def   = 0.8
    
    # Get state based on string
    cur_state                  = state.get(occupancy_entity_str)
    motion                     = state.get(motion_str)
    motion_state_lasts_for     = get_sec_of_cur_state(motion_str)
    motion_off_for             = motion_state_lasts_for if motion == 'off' else 0
    motion_on_ratio_for_x_min  = float(state.get(motion_on_ratio_for_x_min_str))/100
    motion_on_ratio_for_2x_min = float(state.get(motion_on_ratio_for_2x_min_str))/100
    motion_off_ratio_for_x_min = 1 - motion_on_ratio_for_x_min
    motion_off_ratio_for_2x_min= 1 - motion_on_ratio_for_2x_min
    nxt_state                  = 'Uninitialized_states'
    stay_inside_for            = get_sec_of_cur_state(occupancy_entity_str) if cur_state == 'Stayed Inside' else 0
    now_is_sleep_time          = state.get(sleep_time) == 'on'
    
    # Timeouts   
    inside_to_sleep_timeout    = int(inside_to_sleep_timeout) 
    inside_to_outside_timeout  = int(inside_to_outside_timeout) 
    sleep_to_outside_timesout  = int(sleep_to_outside_timesout)  

    # Outside -> xxx
    if cur_state == 'Outside':

        # c11. Outside -> In Sleep
        # People can sometimes not moving for a while and go to outside state
        # Make them back to In Sleep state as long as they moved once
        if motion == 'on' and \
            now_is_sleep_time:
            nxt_state = "In Sleep"

        # c0. Outside      -> Just Entered:
        #     currently on
        elif motion == 'on':
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
          (motion_on_ratio_for_x_min  >= 0.6 or \
           motion_on_ratio_for_2x_min >= 0.4):
            nxt_state = "Stayed Inside"
            
        # c3. Just Entered -> Outside:
        #     (currently off for <normal_timeout> minutes) & largely off in [0,2x]
        elif motion_off_for >= inside_to_outside_timeout and \
             motion_off_ratio_for_2x_min >= 0.5:
               nxt_state = "Outside"
        
        # special case when using only use occupancy sensor to accurately detect when people are outside
        elif turn_to_outside_when_no_motion == 'yes' and \
             motion == 'off':
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
        if stay_inside_for > inside_to_sleep_timeout and \
           now_is_sleep_time:
            nxt_state = "In Sleep"
                    
        # c5. Stayed Inside -> Outside:
        #     (currently off for  <normal_timeout> minutes) & largely off in [0,2x]
        elif motion_off_for >=  inside_to_outside_timeout and \
             motion_off_ratio_for_2x_min >= 0.7:
            nxt_state = "Outside"

        # special case when using only use occupancy sensor to accurately detect when people are outside
        elif turn_to_outside_when_no_motion == 'yes' and \
             motion == 'off':
               nxt_state = "Outside"

        # c6. Stayed Inside -> Stayed Inside:
        #     all other condition
        else:
          nxt_state = "Stayed Inside"

    # In Sleep -> xxx    
    elif cur_state == 'In Sleep':       

        # c7. In Sleep -> Stayed Inside:
        #     Assuming people will wake up once it is not sleep time anymore, living the next FSM transition to handle inside->outside
        if not now_is_sleep_time:
            nxt_state = "Stayed Inside"

        # c8. In Sleep -> Outside in sleep time:
        #     No motions for an hour means people are outside during sleep time
        elif motion_off_for > sleep_to_outside_timesout:
            nxt_state = "Outside"

        # c9. In Sleep -> In Sleep:
        else:    
            nxt_state = "In Sleep"
            
    # Set next state
    state.set(occupancy_entity_str, nxt_state)

    # Log I/O
    
#    log.info("\n==========================================================================================================================================================================================\n" + \
#    "motion_str                     :" + str(motion_str                     ) + "\n"\
#    "cur_state                      :" + str(cur_state                      ) + "\n"\
#    "motion                         :" + str(motion                         ) + "\n"\
#    "motion_state_lasts_for         :" + str(motion_state_lasts_for         ) + "\n"\
#    "motion_off_for                 :" + str(motion_off_for                 ) + "\n"\
#    "motion_on_ratio_for_x_min      :" + str(motion_on_ratio_for_x_min      ) + "\n"\
#    "motion_on_ratio_for_2x_min     :" + str(motion_on_ratio_for_2x_min     ) + "\n"\
#    "motion_off_ratio_for_x_min     :" + str(motion_off_ratio_for_x_min     ) + "\n"\
#    "motion_off_ratio_for_2x_min    :" + str(motion_off_ratio_for_2x_min    ) + "\n"\
#    "stay_inside_for                :" + str(stay_inside_for                ) + "\n"\
#    "now_is_sleep_time              :" + str(now_is_sleep_time              ) + "\n"\
#    "sleep_time                     :" + str(sleep_time                     ) + "\n"\
#    "turn_to_outside_when_no_motion :" + str(turn_to_outside_when_no_motion ) + "\n"\
#    "inside_to_sleep_timeout        :" + str(inside_to_sleep_timeout        ) + "\n"\
#    "inside_to_outside_timeout      :" + str(inside_to_outside_timeout      ) + "\n"\
#    "sleep_to_outside_timesout      :" + str(sleep_to_outside_timesout      ) + "\n"\
#    "nxt_state                      :" + str(nxt_state                      ) + "\n"\
#    "==========================================================================================================================================================================================")    



