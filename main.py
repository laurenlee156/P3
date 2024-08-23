import pickle
import copy
from math import sqrt, log10

class NetworkHandler:
    def __init__(self, filename):
        # Logs
        ap_log = []
        ac_log = []
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

        # AC Handling
        # Step 1: Ensure that all APs are operating on the most efficient and least conflicting channels.
        # Account for overlaps based on coverage and location of APs.
        ap_lst = []
        client_lst = []
        move_lst = []
        for lst in field_lst:
            if lst[0] == 'AP':
                ap_lst.append(lst)
            elif lst[0] == 'CLIENT':
                client_lst.append(lst)
            elif lst[0] == 'MOVE':
                move_lst.append(lst)


        pref_channels = [1, 6, 11]
        other_channels = [2, 3, 4, 5, 7, 8, 9, 10]

        # Note: Multiple APs can have the same channel, as long as they do not overlap.
        for i in range(0, len(ap_lst) - 1):
            for j in range(i + 1, len(ap_lst)):
                # Calculate the distance between first AP and the next.
                distance = sqrt((int(ap_lst[j][2]) - int(ap_lst[i][2])) ** 2 +
                                (int(ap_lst[j][3]) - int(ap_lst[i][3])) ** 2)
                # print(distance_lst[i][1], distance_lst[j][1], distance)
                # If adding the coverage radii of both APs is > distance, there is overlap so change the channel.
                if distance < int(ap_lst[i][11]) + int(ap_lst[j][11]):
                    # print('change needed')
                    # Check if the channels are the same.
                    if ap_lst[i][4] == ap_lst[j][4]:
                        # Change the first AP's channel to the highest possible channel in pref_channels.
                        if len(pref_channels) > 0:
                            # print('pref channels', pref_channels)
                            ap_lst[i][4] = str(max(pref_channels))
                            ac_log.append(f"1Step 1: AC REQUIRES {ap_lst[i][1]} TO CHANGE CHANNEL TO "
                                          f"{max(pref_channels)}")
                            pref_channels.remove(int(ap_lst[i][4]))
                            # print('modified pref channel', pref_channels)
                            # print(distance_lst)
                        else:
                            # print('change to other channel')
                            # print('other channels', other_channels)
                            ap_lst[i][4] = str(int(ap_lst[i][4]) + 1)

                            ac_log.append(f"2Step 1: AC REQUIRES {ap_lst[i][1]} TO CHANGE CHANNEL TO "
                                          f"{ap_lst[i][4]}")
                            # print('modified other channel', other_channels)
                            # print(distance_lst)
                else:
                    print('no change')

        # Step 2: Connect each CLIENT to the best AP possible.
        #print(client_lst)
        #print(ap_lst)
        copy_of_ap_lst = copy.deepcopy(ap_lst)

        for client in client_lst:
            to_remove_set = set()
            for i in range(0, len(ap_lst) - 1):
                #print('i', ap_lst[i])
                for j in range(i + 1, len(ap_lst)):
                    #print('j', ap_lst[j])
                    # Evaluate Wi-Fi
                    if int(ap_lst[i][7][-1]) > int(ap_lst[j][7][-1]):
                        to_remove_set.add(tuple(ap_lst[j]))
                    elif int(ap_lst[i][7][-1]) == int(ap_lst[j][7][-1]):
                        # Evaluate Roaming Standards
                        client_standard = [client[6], client[7], client[8]]
                        if [ap_lst[i][8], ap_lst[i][9], ap_lst[i][10]] == [ap_lst[j][8], ap_lst[j][9], ap_lst[j][10]]:
                            if ap_lst[i][5] > ap_lst[j][5]:
                                to_remove_set.add(tuple(ap_lst[j]))
                            elif ap_lst[i][5] == ap_lst[j][5]:
                                # Evaluate Frequency
                                i_frequency_lst = [float(element) for element in ap_lst[i][6].split('/')]
                                j_frequency_lst = [float(element) for element in ap_lst[j][6].split('/')]
                                if max(i_frequency_lst) > max(j_frequency_lst):
                                    to_remove_set.add(tuple(ap_lst[j]))
                                elif max(i_frequency_lst) == max(j_frequency_lst):
                                    # Evaluate Channel
                                    if ap_lst[i][4] > ap_lst[j][4]:
                                        to_remove_set.add(tuple(ap_lst[j]))
                                    elif ap_lst[i][4] < ap_lst[j][4]:
                                        to_remove_set.add(tuple(ap_lst[j]))
                                else:
                                    to_remove_set.add(tuple(ap_lst[i]))
                            else:
                                to_remove_set.add(tuple(ap_lst[j]))
                        if client_standard == [ap_lst[i][8], ap_lst[i][9], ap_lst[i][10]]:
                            to_remove_set.add(tuple(ap_lst[j]))
                        elif client_standard == [ap_lst[j][8], ap_lst[j][9], ap_lst[j][10]]:
                            to_remove_set.add(tuple(ap_lst[i]))
                        else:
                            # Evaluate if 802.11r is true.
                            if ap_lst[i][10] == 'true' and ap_lst[j][10] == 'false':
                                to_remove_set.add(tuple(ap_lst[j]))
                            elif ap_lst[i][10] == 'false' and ap_lst[j][10] == 'true':
                                to_remove_set.add(tuple(ap_lst[i]))
                    else:
                        to_remove_set.add(tuple(ap_lst[i]))
            final_lst = [element for element in ap_lst if tuple(element) not in to_remove_set]
            for ap in ap_log:
                if ap[1] == final_lst[0][1]:
                    ap.append(client[0])
            client_log.append(f"Step 2: CLIENT CONNECT TO {final_lst[0][1]} WITH SIGNAL STRENGTH")

            print(to_remove_set)

            #final_lst = [element for element in copy_of_ap_lst if tuple(element) not in to_remove_set]
            print(final_lst)



#                         # If Wi-Fi of i > Wi-Fi of j, i_Wi-Fi = True
#                         if int(ap_lst[i][7][-1]) > int(ap_lst[j][7][-1]):
# #                            # Check Frequency band
#                             i_frequency_lst = [float(element) for element in ap_lst[i][6].split('/')]
#                             j_frequency_lst = [float(element) for element in ap_lst[j][6].split('/')]
#                             # If the highest frequency in 1st AP is >= Client's frequency, move on.
#                             if max(i_frequency_lst) >= int(client[4][-1]) and max(j_frequency_lst) >= int(client[4][-1]):
#                                 # If AP's frequency is higher than 2nd AP's, frequency = True.
#                                 if max(i_frequency_lst) > max(j_frequency_lst):
#                                     #i_matched_cond[2] = True
#                                 else:
#                                     #j_matched_cond[2] = True
#                                     # 1st AP's channel is higher than 2nd AP's, and AP prefers 802.11r, then True.
#                                     if ap_lst[i][4] > ap_lst[j][4] and ap_lst[i][10] == 'true':
#                                         #i_matched_cond[3] = True
#                         else:
#                             # If Wi-Fi of j > Wi-Fi of j, j_Wi-Fi = True
#                             #j_matched_cond[1] = True
#                                         # Log connections
#                         #elif int(ap_lst[i][7][-1]) < int(ap_lst[j][7][-1]):
#                     else:
#                         ap_log.append(f"fStep 2: {client[1]} TRIED {ap_lst[i][1]} BUT WAS DENIED.")

        self.field_lst = field_lst
        self.ap_lst = ap_lst
        self.client_lst = client_lst
        self.move_lst = move_lst
        self.ap_log = ap_log
        self.ac_log = ac_log
        self.client_log = client_log



    # Calculate RSSI -> Strength of a signal received by a device from a router/phone.
    # Measured from 0db -> -120db.
    def when_to_roam(self):
        print(self.ap_lst)
        print(self.client_lst)
        print(self.move_lst)

        # Evaluate APs based on signal strength.
        for client in self.client_lst:
            # Check if the names of CLIENT and MOVE match.
            if client[1] == self.move_lst[0][1]:
                for ap in self.ap_lst:
                    # frequency_lst = [float(element) * 1000 for element in ap[6].split('/')]
                    # ap[6] = str(max(frequency_lst))
                    # distance = sqrt((int(self.move_lst[0][2]) - int(ap[2])) ** 2 +
                    #                 (int(self.move_lst[0][3]) - int(ap[3])) ** 2)
                    # # RSSI of MOVE and APs.
                    # rssi = int(ap[5]) - (20 * log10(distance)) - (20 * log10(float(ap[6]))) - 32.44
                    # #print(rssi)
                    rssi = self.calculate_rssi(self.move_lst[0][2], self.move_lst[0][3], ap[2], ap[3], ap[6], ap[5])
                    print(rssi)
                    # Account for the optional RSSI in APs.
                    # if len(ap) != 14:
                    #     # If minimum RSSI of MOVE and AP >= CLIENT'S minimum RSSI...
                    #     if rssi >= -(int(client[9])):
                    #         self.ap_lst.remove(ap)
                    # else:
                    #     # If minimum RSSI of MOVE and AP >= CLIENT or AP's minimum RSSI...
                    #     if rssi >= -(int(client[9])) or rssi >= -(int(ap[13])):
                    #         self.ap_lst.remove(ap)

    def calculate_rssi(self, coord_1_x, coord_1_y, coord_2_x, coord_2_y, frequency, ap_power):
        distance = sqrt((int(coord_2_x) - int(coord_1_x)) ** 2 +
                        (int(coord_2_y) - int(coord_1_y)) ** 2)
        frequency_lst = [float(element) * 1000 for element in frequency.split('/')]
        max_frequency = max(frequency_lst)
        rssi = int(ap_power) - (20 * log10(distance)) - (20 * log10(max_frequency)) - 32.44
        return 'hi', rssi


o = NetworkHandler('example.txt')
(o.when_to_roam())
#print(o.calculate_rssi(0, 0, 10, 9, '2.4/5', 20))

