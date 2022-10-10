from datetime import datetime as dt
from datetime import timezone as timezone

# Get the number of seconds this entity has been current state 
def get_sec_of_cur_state(entity_name):
  last_time_cur_entity_changed = state.get(entity_name + '.last_changed')
  return (dt.now(tz=timezone.utc) - last_time_cur_entity_changed).total_seconds()

################################
# Room Occupancy
#
#       outside --c0---> just_entered ----c2----> stayed
#           |<----c3---------|                      |
#           |<-------------------c5-----------------|
#          |c1|             |c4|                  |c6| 
#
# State machine changing conditions:
#
# c0. outside      -> just_entered:
#     currently on 
# c1. outside      -> outside: 
#     currently off for 5 Min & previously off in [0, 2x] 
#     OR all other condition
# c2. just_entered -> stayed:
#     currently on & previously largely on in [0,x]
#     OR previously fully on in [0,x] & currently on
# c3. just_entered -> outside:
#     (currently off for 5min) & largely off in [0,2x]
# c4. just_entered -> just_entered
#     all other conditions
# c5. stayed       -> outside:
#     (currently off for 5min) & largely off in [0,2x]
# c4. stayed       -> stayed:
#     all other condition
################################
@service
def room_occupancy_state_machine(occupancy_entity_str, 
                                 motion_str,                                 
                                 motion_ratio_for_x_min_str,
                                 motion_ratio_for_2x_min_str):
    
    percentage_for_largely_def = 0.4
    #percentage_for_fully_def   = 0.8
    
    # Get state based on string
    cur_state               = state.get(occupancy_entity_str)
    motion                  = state.get(motion_str)
    motion_ratio_for_x_min  = float(state.get(motion_ratio_for_x_min_str))
    motion_ratio_for_2x_min = float(state.get(motion_ratio_for_2x_min_str))
    nxt_state               = ''
    
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
           (motion_ratio_for_x_min  >= percentage_for_largely_def or
            motion_ratio_for_2x_min >= percentage_for_largely_def):
            nxt_state = "Stayed Inside"
            
        # c3. Just Entered -> Outside:
        #     (currently off for 5min) & largely off in [0,2x]
        elif motion == 'off' and \
           get_sec_of_cur_state(motion) >= 5*60 and \
           motion_ratio_for_2x_min <= (1-percentage_for_largely_def):
            nxt_state = "Outside"
        
        # c4. just_entered -> just_entered
        #     all other conditions
        else:
            nxt_state = "Just Entered"

    # Stayed Inside -> xxx    
    elif state.get(occupancy_entity) == 'Stayed Inside':       
        
        # c5. Stayed Inside -> Outside:
        #     (currently off for 5min) & largely off in [0,2x]
        if motion == 'off' and \
           get_sec_of_cur_state(motion) >= 5*60 and \
           motion_ratio_for_2x_min <= (1-percentage_for_largely_def):
            nxt_state = "Outside"
        
        # c4. Stayed Inside -> Stayed Inside:
        #     all other condition
        else:
            nxt_state = "Stayed Inside"

    # Set next state
    state.get(occupancy_entity_str, nxt_state)
            
            