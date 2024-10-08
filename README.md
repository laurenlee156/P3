P3 Design Document

INIT: 
- Initialize the inputs by creating separate logs and lists for AP, AC, and CLIENT. 
- Initialize a “move_to_next” variable to indicate whether roaming has to happen (associated with the when_to_roam function). 
- Raise errors if there are incorrect values in the inputs.
    
AC: 
1. modify_channels function: 
    - Keep track of the preferred channels in order of 1, 6, and 11 so multiple APs are not connected to the same preferred channel. 
    - Key point: A preferred channel can only be connected to once. Any other APs will be connected to one above only if there is overlap between the APS. 
    - Compare APs by computing the distance between the first AP and the next. 
    - If there is overlap, first check if they are connected to the same channel. If there are still channels left in the preferred channels list, connect the AP to the available highest channel. However, if the AP is a preferred channel, connect the AP to its channel +         1. If there is no overlap between APs, there is no need to change channels. 
    - Log all changes into ac_log. 

AP/CLIENT: 
1. find_best_ap function (called 2x): 
    - Primarily used when there are multiple APs in the input. 
    - Compare each AP to the next, and evaluate the APs based on this priority level: 
    - Wi-Fi -> Roaming standards -> Power -> Frequency -> Channel -> Signal 
    - When comparing these APs based on this priority level, the program adds the specific AP that is not considered the best match into the “to_remove_set”. 
    - After comparisons are completed, compatible_ap will contain the AP that is the best match for the current Client by getting the AP that is not in the to_remove_set when compared to ap_lst. 
    - The program will check if the device limit of the specified AP has been met; if so, client/ap logs will log roam denied. If the AP supports 802.11r, log fast roam. 
    - Log disconnect if the client specified in MOVE has gone out of the radius between its connected AP’s coverage radius. 
2. single_ap function (if there is only one AP in input, call 2x): 
    - Used when there is only one AP in the input. 
    - Automatically connects the client to the AP until it reaches the max device limit. 
    - Similar details to find_best_ap. 
3. when_to_roam function (call between the 2 calls of the above): 
    - Calculates RSSI for AP and MOVE, and allows the client to move if the minimum RSSI of MOVE and AP are >= CLIENT or AP’s minimum RSSI. 
    - If roam is successful, set the flag move_to_next -> True 
4. __call__: 
    - Utilize pickle.dump to dump contents of each specified log into a pickle file. 
