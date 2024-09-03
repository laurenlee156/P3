import unittest
import pickle
from main import NetworkHandler


class TestNetworkHandler(unittest.TestCase):
    def setUp(self):
        # Create test file
        self.filename1 = 'test_file.txt'
        with open(self.filename1, 'w') as f:
            f.write(
                "AP AP1 0 0 6 20 2.4/5 WiFi8 true true true 50 10 75\n"
                "AP AP2 100 100 6 20 2.4 WiFi6 false true false 50 60\n"
                "AP AP3 30 50 6 20 5 WiFi8 false true false 60 60\n"
                "AP AP4 40 50 6 20 5 WiFi6 true true false 40 60\n"
                "AP AP5 30 60 6 20 5 WiFi7 false true true 55 60\n"
                "CLIENT Client1 10 10 WiFi6 2.4/5 false true false 73\n"
                "CLIENT Client2 5 5 WiFi7 5 true true true 60\n"
                "MOVE Client1 10 9\n"
            )

        self.filename2 = 'test_disconnect.txt'
        with open(self.filename2, 'w') as file:
            file.write(
                "AP AP1 0 0 6 20 2.4 WiFi7 true true true 50 10 75\n"
                "AP AP2 100 100 6 20 2.4 WiFi6 false true false 50 60\n"
                "CLIENT Client1 10 10 WiFi6 2.4 true true true 73\n"
                "MOVE Client1 60 60\n"
            )

        self.filename3 = 'test_single_ap_txt'
        with open(self.filename3, 'w') as file:
            file.write(
                "AP AP1 0 0 6 20 2.4 WiFi7 true true true 10 10 75\n"
                "CLIENT Client1 10 10 WiFi6 2.4 true true true 73\n"
                "CLIENT Client2 5 5 WiFi7 5 true true true 60\n"
                
                "MOVE Client1 10 20\n"
            )

    def test_init_(self):
        nh_object = NetworkHandler(self.filename1)
        # Check if the lengths of the lists are the same.
        # AP LIST
        ap_count = 0
        for lst in nh_object.ap_lst:
            ap_count += 1
        self.assertEqual(ap_count, 5)

        # CLIENT LIST
        client_count = 0
        for lst in nh_object.client_lst:
            client_count += 1
        self.assertEqual(client_count, 2)

        # MOVE LIST
        move_count = 0
        for lst in nh_object.move_lst:
            move_count += 1
        self.assertEqual(move_count, 1)

    def test_modify_channels(self):
        nh_object = NetworkHandler(self.filename1)
        nh_object.modify_channels()
        self.assertEqual(int(nh_object.ap_lst[0][4]), 11)
        self.assertEqual(int(nh_object.ap_lst[1][4]), 1)
        self.assertEqual(int(nh_object.ap_lst[2][4]), 8)
        self.assertEqual(int(nh_object.ap_lst[3][4]), 7)
        self.assertEqual(int(nh_object.ap_lst[4][4]), 6)
        self.assertEqual(nh_object.ac_log, ['Step 1: AC REQUIRES AP1 TO CHANGE CHANNEL TO 11',
                                            'Step 2: AC REQUIRES AP2 TO CHANGE CHANNEL TO 6',
                                            'Step 3: AC REQUIRES AP2 TO CHANGE CHANNEL TO 1',
                                            'Step 4: AC REQUIRES AP3 TO CHANGE CHANNEL TO 7',
                                            'Step 5: AC REQUIRES AP4 TO CHANGE CHANNEL TO 7',
                                            'Step 6: AC REQUIRES AP3 TO CHANGE CHANNEL TO 8'])

    def test_find_best_ap(self):
        nh_object = NetworkHandler(self.filename1)
        nh_object.modify_channels()
        nh_object.find_best_ap()
        nh_object.when_to_roam()
        nh_object.find_best_ap()

        self.assertEqual(nh_object.ap_log, ['STEP 2: Client1 ROAM TO AP3',
                                            'STEP 2: Client1 CONNECT LOCATION 10 10 WiFi6 2.4/5 false true false',
                                            'STEP 3: Client2 FAST ROAM TO AP1',
                                            'STEP 3: Client2 CONNECT LOCATION 5 5 WiFi7 5 true true true',
                                            'STEP 4: Client1 FAST ROAM TO AP1',
                                            'STEP 4: Client1 CONNECT LOCATION 10 10 WiFi6 2.4/5 false true false'])
        self.assertEqual(nh_object.ap_lst, [['AP', 'AP1', '0', '0', '11', '20', '2.4/5', 'WiFi8', 'true',
                                             'true', 'true', '50', '10', '75', 'Client2', 'Client1'],
                                            ['AP', 'AP2', '100', '100', '1', '20', '2.4', 'WiFi6', 'false', 'true',
                                             'false', '50', '60', ' '],
                                            ['AP', 'AP4', '40', '50', '7', '20', '5', 'WiFi6', 'true', 'true',
                                             'false', '40', '60', ' '],
                                            ['AP', 'AP5', '30', '60', '6', '20', '5', 'WiFi7', 'false', 'true',
                                             'true', '55', '60', ' ']])
        self.assertEqual(nh_object.client_log, ['Step 2: Client1 CONNECT TO AP3 WITH SIGNAL STRENGTH '
                                                '-119.42970004336019',
                                                'Step 3: Client2 CONNECT TO AP1 WITH SIGNAL STRENGTH '
                                                '-103.40910013008056',
                                                'Step 4: Client1 CONNECT TO AP1 WITH SIGNAL STRENGTH '
                                                '-109.42970004336019'])
        self.assertEqual(nh_object.client_lst, [['CLIENT', 'Client1', '10', '10', 'WiFi6', '2.4/5', 'false',
                                                 'true', 'false', '73']])
    def test_disconnect(self):
        nh_object = NetworkHandler(self.filename2)
        nh_object.find_best_ap()
        nh_object.when_to_roam()
        nh_object.find_best_ap()
        self.assertEqual(nh_object.ap_log, ['STEP 2: Client1 FAST ROAM TO AP1',
                                            'STEP 2: Client1 CONNECT LOCATION 10 10 WiFi6 2.4 true true true',
                                            'STEP 3: Client1 ROAM TO AP2', 'STEP 3: Client1 CONNECT LOCATION '
                                                                           '10 10 WiFi6 2.4 true true true',
                                            'Step 4: Client1 DISCONNECTS AT LOCATION 10 10 WiFi6 2.4 true true true'])
        self.assertEqual(nh_object.ap_lst, [['AP', 'AP2', '100', '100', '6', '20', '2.4', 'WiFi6', 'false',
                                             'true', 'false', '50', '60', ' ', 'Client1']])
        self.assertEqual(nh_object.client_log, ['Step 2: Client1 CONNECT TO AP1 WITH SIGNAL STRENGTH '
                                                '-103.05452479087192',
                                                'Step 3: Client1 CONNECT TO AP2 WITH SIGNAL STRENGTH '
                                                '-122.13937497965841',
                                                'Step 4: CLIENT DISCONNECT FROM AP2 SIGNAL STRENGTH '
                                                '-122.13937497965841'])

    def test_single_ap(self):
        nh_object = NetworkHandler(self.filename3)
        nh_object.single_ap()
        nh_object.when_to_roam()
        nh_object.single_ap()
        self.assertEqual(nh_object.ap_log, ['STEP 1: Client1 CONNECT LOCATION 10 10 WiFi6 2.4 true true true',
                                            'Step 2: Client1 DISCONNECTS AT LOCATION 10 10 WiFi6 2.4 true true true',
                                            'STEP 3: Client2 CONNECT LOCATION 5 5 WiFi7 5 true true true',
                                            'Final Step: Client1 HAS NO APS TO CONNECT TO'])
        self.assertEqual(nh_object.ap_lst, [])
        self.assertEqual(nh_object.client_log, ['Step 1: Client1 FAST ROAM TO AP1',
                                                'Step 1: Client1 CONNECT TO AP1 WITH SIGNAL STRENGTH '
                                                '-103.05452479087192',
                                                'Step 2: CLIENT DISCONNECT FROM AP1 SIGNAL STRENGTH '
                                                '-103.05452479087192', 'Step 3: Client2 FAST ROAM TO AP1',
                                                'Step 3: Client2 CONNECT TO AP1 WITH SIGNAL STRENGTH '
                                                '-97.0339248775923', 'Final Step: Client1 HAS NO APS TO CONNECT TO'])

    def test_rssi(self):
        nh_object = NetworkHandler(self.filename1)
        rssi = nh_object.calculate_rssi(5, 6, 3, 4, 2.4, 20)
        self.assertEqual(round(rssi, 5), -89.07512)

    def test_distance(self):
        nh_object = NetworkHandler(self.filename1)
        distance = nh_object.calculate_distance(4, 3, 5, 10)
        self.assertEqual(round(distance, 5), 7.07107)

    def test_pickle1(self):
        nh_object1 = NetworkHandler(self.filename1)
        nh_object1.find_best_ap()
        nh_object1.when_to_roam()
        nh_object1.find_best_ap()
        with open('ap.pkl', 'rb') as file:
            ap_data = pickle.load(file)
        self.assertEqual(nh_object1.ap_log, ap_data)

        with open('client.pkl', 'rb') as file:
            client_data = pickle.load(file)
        self.assertEqual(nh_object1.client_log, client_data)

        with open('ac.pkl', 'rb') as file:
            ac_data = pickle.load(file)
        self.assertEqual(nh_object1.ac_log, ac_data)

    def test_pickle2(self):
        nh_object2 = NetworkHandler(self.filename2)
        nh_object2.find_best_ap()
        nh_object2.when_to_roam()
        nh_object2.find_best_ap()
        with open('ap.pkl', 'rb') as file:
            ap_data = pickle.load(file)
        self.assertEqual(nh_object2.ap_log, ap_data)

        with open('client.pkl', 'rb') as file:
            client_data = pickle.load(file)
        self.assertEqual(nh_object2.client_log, client_data)

        with open('ac.pkl', 'rb') as file:
            ac_data = pickle.load(file)
        self.assertEqual(nh_object2.ac_log, ac_data)

    def test_pickle3(self):
        nh_object3 = NetworkHandler(self.filename3)
        nh_object3.single_ap()
        nh_object3.when_to_roam()
        nh_object3.single_ap()
        with open('ap.pkl', 'rb') as file:
            ap_data = pickle.load(file)
        self.assertEqual(nh_object3.ap_log, ap_data)

        with open('client.pkl', 'rb') as file:
            client_data = pickle.load(file)
        self.assertEqual(nh_object3.client_log, client_data)

        with open('ac.pkl', 'rb') as file:
            ac_data = pickle.load(file)
        print('data', ac_data)
        self.assertEqual(nh_object3.ac_log, ac_data)


if __name__ == "__main__":
    unittest.main()