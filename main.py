import pickle
from math import sqrt

class NetworkHandler:
    def __init__(self, filename):
        # Logs
        ap_log = []
        client_log = []

        # Open the file.
        field_lst = []
        with open(filename, 'r') as file:
            # Create a list of lists of fields since APs may appear more than once.
            for line in file:
                field = line.rstrip('\n').split(' ')
                field_lst.append(field)

        # Check Name and Negative Values Exceptions.
        for lst in field_lst:
            if lst[0] != 'AP' and lst[0] != 'CLIENT' and lst[0] != 'MOVE' and lst[0] != " ":
                raise ValueError("Must be AP, CLIENT, or MOVE.")
            for element in lst:
                if element[0] == '-' and element.lstrip('-').isdigit():
                    raise ValueError("Values must all be positive integers.")
        print(field_lst)

        # AC Handling
        # Step 1: Ensure that all APs are operating on the most efficient and least conflicting channels.

        # pref_channels = [1, 6, 11]
        # other_channels = [2, 3, 4, 5, 7, 8, 9, 10]
        # for lst in field_lst:
        #     if lst[0] == 'AP':
        #         # If the channel is a preferred channel, check if it is the greatest in the list.
        #         if int(lst[4]) in pref_channels:
        #             if len(pref_channels) > 0:
        #                 lst[4] = str(max(pref_channels))
        #                 ap_log.append(f"1Step 1: AC REQUIRES {lst[1]} TO CHANGE CHANNEL TO {max(pref_channels)}")
        #                 pref_channels.remove(int(lst[4]))
        #
        #             # If the channel is a preferred channel, but pref_channels is empty,
        #             # reduce the channel number by one.
        #             else:
        #                 lst[4] = str(int(lst[4]) + 1)
        #                 ap_log.append(f"2Step 1: AC REQUIRES {lst[1]} TO CHANGE CHANNEL TO {lst[4]}")
        #                 other_channels.remove(int(lst[4]))
        #
        #         # If the channel is a preferred channel,
        #         # but not in pref_channels, assign it the greatest available value in pref_channels.
        #         elif int(lst[4]) == 1 or int(lst[4]) == 6 or int(lst[4]) == 11 and int(lst[4]) not in pref_channels:
        #             if len(pref_channels) > 0:
        #                 lst[4] = str(max(pref_channels))
        #                 ap_log.append(f"4Step 1: AC REQUIRES {lst[1]} TO CHANGE CHANNEL TO {max(pref_channels)}")
        #                 pref_channels.remove(int(lst[4]))
        #             # If pref_channels is empty, and the channel is a preferred channel,
        #             # reduce the channel number by one.
        #             else:
        #                 lst[4] = str(int(lst[4]) + 1)
        #                 ap_log.append(f"5Step 1: AC REQUIRES {lst[1]} TO CHANGE CHANNEL TO {lst[4]}")
        #                 other_channels.remove(int(lst[4]))
        #
        #         # NOT DONE!! If the channel is not a preferred channel, reduce the channel number by one (add by one).
        #         if int(lst[4]) in other_channels:
        #             # While other_channels is not empty, remove the channel to eliminate duplicate channels.
        #             if len(other_channels) > 0:
        #                 other_channels.remove(int(lst[4]))
        #             else:
        #                 lst[4] = str(max(pref_channels))
        #                 ap_log.append(f"3Step 1: AC REQUIRES {lst[1]} TO CHANGE CHANNEL TO {lst[4]}")

        # Account for overlaps based on coverage and location of APs.
        distance_lst = []
        for lst in field_lst:
            if lst[0] == 'AP':
                distance_lst.append(lst)

        pref_channels = [1, 6, 11]
        other_channels = [2, 3, 4, 5, 7, 8, 9, 10]

        # Note: Multiple APs can have the same channel, as long as they do not overlap.
        print(distance_lst)
        for i in range(0, len(distance_lst) - 1):
            for j in range(i + 1, len(distance_lst)):
                # Calculate the distance between first AP and the next.
                distance = sqrt((int(distance_lst[j][2]) - int(distance_lst[i][2])) ** 2 +
                                (int(distance_lst[j][3]) - int(distance_lst[i][3])) ** 2)
                #print(distance_lst[i][1], distance_lst[j][1], distance)
                # If adding the coverage radii of both APs is > distance, there is overlap so change the channel.
                if distance < int(distance_lst[i][11]) + int(distance_lst[j][11]):
                    # print('change needed')
                    # Check if the channels are the same.
                    if distance_lst[i][4] == distance_lst[j][4]:
                        # Change the first AP's channel to the highest possible channel in pref_channels.
                        if len(pref_channels) > 0:
                            # print('pref channels', pref_channels)
                            distance_lst[i][4] = str(max(pref_channels))
                            ap_log.append(f"1Step 1: AC REQUIRES {distance_lst[i][1]} TO CHANGE CHANNEL TO "
                                          f"{max(pref_channels)}")
                            pref_channels.remove(int(distance_lst[i][4]))
                            # print('modified pref channel', pref_channels)
                            # print(distance_lst)
                        else:
                            # print('change to other channel')
                            # print('other channels', other_channels)
                            distance_lst[i][4] = str(int(distance_lst[i][4]) + 1)

                            ap_log.append(f"2Step 1: AC REQUIRES {distance_lst[i][1]} TO CHANGE CHANNEL TO "
                                          f"{distance_lst[i][4]}")
                            # print('modified other channel', other_channels)
                            # print(distance_lst)
                else:
                    print('no change')

        print(distance_lst)
        print(ap_log)


o = NetworkHandler('example.txt')

