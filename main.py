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
                # Account for blank lines.
                if len(line.split()) == 0:
                    continue
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
                if int(lst[4]) > 11:
                    raise ValueError("Channel cannot exceed 11.")
                if len(lst) != 14:
                    lst.append(' ')
                ap_lst.append(lst)
            elif lst[0] == 'CLIENT':
                client_lst.append(lst)
            elif lst[0] == 'MOVE':
                move_lst.append(lst)

        self.field_lst = field_lst
        self.ap_lst = ap_lst
        self.client_lst = client_lst
        self.move_lst = move_lst
        self.ap_log = ap_log
        self.ac_log = ac_log
        self.client_log = client_log
        self.move_to_next = False
        self.n = 1

    def modify_channels(self):
        print(self.ap_lst)
        pref_channels = [1, 6, 11]

        # Compares APs after they have been modified.
        modified = True
        while modified:
            modified = False
            # Note: Multiple APs can have the same channel, as long as they do not overlap.
            for i in range(0, len(self.ap_lst) - 1):
                for j in range(i + 1, len(self.ap_lst)):
                    #print(f'comparing {self.ap_lst[i][1]} and {self.ap_lst[j][1]}')
                    # Calculate the distance between first AP and the next.
                    distance = self.calculate_distance(self.ap_lst[j][2], self.ap_lst[j][3], self.ap_lst[i][2],
                                                       self.ap_lst[i][3])
                    #print(f'distance: {distance}')
                    # If adding the coverage radii of both APs is > distance, there is overlap so change the channel.
                    if distance < (int(self.ap_lst[i][11]) + int(self.ap_lst[j][11])):
                        # Check if the channels are the same.
                        if self.ap_lst[i][4] == self.ap_lst[j][4]:
                            #print('changed')
                            # Change the first AP's channel to the highest possible channel in pref_channels.
                            #print(f'comparing {self.ap_lst[i][4]} and {self.ap_lst[j][4]}')
                            if len(pref_channels) > 0:
                                self.ap_lst[i][4] = str(max(pref_channels))
                                #print('changed channel to', self.ap_lst[i][1], self.ap_lst[i][4])
                                self.ac_log.append(f"1Step 1: AC REQUIRES {self.ap_lst[i][1]} TO CHANGE CHANNEL TO "
                                              f"{max(pref_channels)}")
                                pref_channels.remove(int(self.ap_lst[i][4]))
                                #print('revised pref_channels', pref_channels)
                                modified = True
                            else:
                                if int(self.ap_lst[i][4]) + 1 <= 11:
                                    self.ap_lst[i][4] = str(int(self.ap_lst[i][4]) + 1)
                                    #print('changed channel to', self.ap_lst[i][1], self.ap_lst[i][4])
                                    self.ac_log.append(f"2Step 1: AC REQUIRES {self.ap_lst[i][1]} TO CHANGE CHANNEL TO "
                                                  f"{self.ap_lst[i][4]}")
                                    modified = True
        # print('what', self.ac_log)
        # print(self.ap_lst)

    def find_best_ap(self):
        # Step 2: Connect each CLIENT to the best AP possible.
        for client in self.client_lst:
            to_remove_set = set()
            for i in range(0, len(self.ap_lst) - 1):
                for j in range(i + 1, len(self.ap_lst)):
                    # Evaluate Wi-Fi
                    if int(self.ap_lst[i][7][-1]) > int(self.ap_lst[j][7][-1]):
                        to_remove_set.add(tuple(self.ap_lst[j]))
                    elif int(self.ap_lst[i][7][-1]) == int(self.ap_lst[j][7][-1]):
                        # Evaluate Roaming Standards
                        client_standard = [client[6], client[7], client[8]]
                        i_ap_standard = [self.ap_lst[i][8], self.ap_lst[i][9], self.ap_lst[i][10]]
                        j_ap_standard = [self.ap_lst[j][8], self.ap_lst[j][9], self.ap_lst[j][10]]

                        if i_ap_standard == j_ap_standard:
                            # Evaluate Power
                            if self.ap_lst[i][5] > self.ap_lst[j][5]:
                                to_remove_set.add(tuple(self.ap_lst[j]))
                            elif self.ap_lst[i][5] == self.ap_lst[j][5]:
                                # Evaluate Frequency
                                i_frequency_lst = [float(element) for element in self.ap_lst[i][6].split('/')]
                                j_frequency_lst = [float(element) for element in self.ap_lst[j][6].split('/')]
                                if max(i_frequency_lst) > max(j_frequency_lst):
                                    to_remove_set.add(tuple(self.ap_lst[j]))
                                elif max(i_frequency_lst) == max(j_frequency_lst):
                                    # Evaluate Channel
                                    if self.ap_lst[i][4] > self.ap_lst[j][4]:
                                        to_remove_set.add(tuple(self.ap_lst[j]))
                                    elif self.ap_lst[i][4] < self.ap_lst[j][4]:
                                        to_remove_set.add(tuple(self.ap_lst[j]))
                                        # If all other conditions are met/tied with each other,
                                        # calculate which has the stronger signal strength w/ the AP.
                                    else:
                                        i_rssi = self.calculate_rssi(self.ap_lst[i][2], self.ap_lst[i][3], client[2],
                                                                     client[3], self.ap_lst[i][6], self.ap_lst[j][5])
                                        j_rssi = self.calculate_rssi(self.ap_lst[j][2], self.ap_lst[j][3], client[2],
                                                                     client[3], self.ap_lst[j][6], self.ap_lst[j][5])
                                        if i_rssi < j_rssi:
                                            to_remove_set.add(tuple(self.ap_lst[j]))
                                        else:
                                            to_remove_set.add(tuple(self.ap_lst[i]))
                                else:
                                    to_remove_set.add(tuple(self.ap_lst[i]))
                            else:
                                to_remove_set.add(tuple(self.ap_lst[j]))
                        elif client_standard == i_ap_standard:
                            to_remove_set.add(tuple(self.ap_lst[j]))
                        elif client_standard == j_ap_standard:
                            to_remove_set.add(tuple(self.ap_lst[i]))
                        # Account for the same standards.
                        elif client_standard.count('true') == i_ap_standard.count('true'):
                            to_remove_set.add(tuple(self.ap_lst[j]))
                        elif client_standard.count('true') == j_ap_standard.count('true'):
                            to_remove_set.add(tuple(self.ap_lst[i]))
                        else:
                            # Evaluate if 802.11r is true.
                            if i_ap_standard[2] == 'true' and j_ap_standard[2] == 'false':
                                to_remove_set.add(tuple(self.ap_lst[j]))
                            elif i_ap_standard[2] == 'false' and i_ap_standard[2] == 'true':
                                to_remove_set.add(tuple(self.ap_lst[i]))
                    else:
                        to_remove_set.add(tuple(self.ap_lst[i]))

            # compatible_ap contains the AP that is the best match for the current CLIENT.
            compatible_ap = [element for element in self.ap_lst if tuple(element) not in to_remove_set]
            print('compatible ap', compatible_ap)
            # If AP reaches its maximum device limit, display the denied message.
            if len(compatible_ap[0]) - 13 >= int(compatible_ap[0][12]):
                self.client_log.append(f"Step {self.n}: CLIENT ROAM DENIED")
                self.ap_log.append(f"Step {self.n}: {client[1]} TRIED {compatible_ap[0][1]} BUT WAS DENIED")
            else:
                self.n += 1
                for ap in self.ap_lst:
                    if ap[1] == compatible_ap[0][1]:
                        ap.append(client[1])
                # Log Roam: Fast roam if the new AP supports 802.11r
                if compatible_ap[0][10] == 'true':
                    self.ap_log.append(f"STEP {self.n}: {client[1]} FAST ROAM TO {compatible_ap[0][1]}")
                else:
                    self.ap_log.append(f"STEP {self.n}: {client[1]} ROAM TO {compatible_ap[0][1]}")
                # Log Connection
                self.client_log.append("Step " + str(self.n) + ": " + str(client[1]) + " CONNECT TO " +
                                       compatible_ap[0][1] + " WITH SIGNAL STRENGTH " +
                                       str(self.calculate_rssi(client[2], client[3], compatible_ap[0][2],
                                           compatible_ap[0][3], compatible_ap[0][6], compatible_ap[0][5])))
                self.ap_log.append(f"STEP {self.n}: {client[1]} CONNECT LOCATION {' '.join(client[2:9])}")

        if self.move_to_next:
            for client in self.client_lst:
                # Get the AP that the CLIENT is currently connected to.
                for ap in self.ap_lst:
                    if client[1] in ap:
                        # If the distance between MOVE and AP is greater than the AP's coverage radius, CLIENT
                        # has gone out of range.
                        if self.calculate_distance(self.move_lst[0][2], self.move_lst[0][3], ap[2], ap[3]) > int(ap[11]):
                            self.n += 1
                            self.client_log.append("Step " + str(self.n) + ": CLIENT DISCONNECT FROM " + str(ap[1]) +
                                                   " SIGNAL STRENGTH " + str(self.calculate_rssi(client[2], client[3],
                                                                             ap[2], ap[3], ap[6], ap[5])))
                            self.ap_log.append(f"Step {self.n}: {client[1]} DISCONNECTS AT LOCATION "
                                               f"{' '.join(client[2:9])}")

        print(self.client_log)
        print(self.ap_log)
        print(self.ap_lst)

    def when_to_roam(self):
        #print('roaming')
        # Evaluate APs based on signal strength.
        for client in self.client_lst:
            # Check if the names of CLIENT and MOVE match.
            if client[1] == self.move_lst[0][1]:
                for ap in self.ap_lst:
                    if client[1] in ap:
                        #print(f'{client[1]} connected to {ap[1]}')
                        # Calculate RSSI for AP and MOVE.
                        rssi = self.calculate_rssi(self.move_lst[0][2], self.move_lst[0][3], ap[2], ap[3], ap[6], ap[5])
                        # Account for the optional RSSI in APs.
                        if ap[13] == ' ':
                            # If minimum RSSI of MOVE and AP <= CLIENT'S minimum RSSI...
                            if rssi <= -(int(client[9])):
                                # print(rssi)
                                # print(int(client[9]))
                                # print('ap removed')
                                # Remove the AP that MOVE cannot connect to.
                                self.ap_lst.remove(ap)
                                self.move_to_next = True
                        else:
                            # If minimum RSSI of MOVE and AP >= CLIENT or AP's minimum RSSI...
                            if rssi <= -(int(client[9])) or rssi <= -(int(ap[13])):
                                # print(rssi)
                                # print(-int(client[9]))
                                # print(-int(ap[13]))
                                # print('ap removed')
                                # Remove the AP that MOVE cannot connect to.
                                self.ap_lst.remove(ap)
                                self.move_to_next = True
            else:
                # Remove CLIENT if it is not the CLIENT specified in MOVE.
                #print('remove client')
                self.client_lst.remove(client)
        # print('revised ap list', self.ap_lst)
        # print('revised client list', self.client_lst)

    def calculate_rssi(self, coord_1_x, coord_1_y, coord_2_x, coord_2_y, frequency, ap_power):
        distance = self.calculate_distance(coord_1_x, coord_1_y, coord_2_x, coord_2_y)
        frequency_lst = [float(element) * 1000 for element in frequency.split('/')]
        max_frequency = max(frequency_lst)
        return int(ap_power) - (20 * log10(distance)) - (20 * log10(max_frequency)) - 32.44

    def calculate_distance(self, coord_1_x, coord_1_y, coord_2_x, coord_2_y):
        return sqrt((int(coord_2_x) - int(coord_1_x)) ** 2 +
                    (int(coord_2_y) - int(coord_1_y)) ** 2)
    def __call__(self, *args, **kwargs): # __call__(client, ap, ac)
        for arg in args:
            if arg.upper() == 'AP':
                with open('ap.pkl', 'wb') as file:
                    pickle.dump(self.ap_log, file)
            elif arg.upper() == 'CLIENT':
                with open('client.pkl', 'wb') as file:
                    pickle.dump(self.client_log, file)
            elif arg.upper() == 'AC':
                with open('ac.pkl', 'wb') as file:
                    pickle.dump(self.ac_log, file)


o = NetworkHandler('example.txt')
o.modify_channels()
o.find_best_ap()
o.when_to_roam()
o.find_best_ap()
o.__call__('ap')



