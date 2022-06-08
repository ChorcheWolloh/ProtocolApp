from kivy.core.window import Window
from kivy.uix.recycleview import RecycleView
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition
from kivymd.app import MDApp
from datetime import date
import requests
import json
import re
from functools import partial

from colorspopup import ColorsPopup
from myfirebase import MyFirebase
from profilepopup import ProfilePopup

#Window.size = (300, 600)


class MainPage(Screen):
    pass


class Profile(Screen):
    pass


class ProtocolInfoPage(Screen):
    casing_enabled = BooleanProperty(False)
    pilot = ObjectProperty(None)
    extender = ObjectProperty(None)
    reamer = ObjectProperty(None)
    caula = ObjectProperty(None)
    additional = ObjectProperty(None)
    today = date.today()

    collected_info = {"Liners": {"4x20": list(), "8x10": list()}, "Date": today.strftime("%d/%m/%Y")}
    # Getting object lists from the database
    clients = requests.get("https://protocol-app-hdd-default-rtdb.europe-west1.firebasedatabase.app/Objects.json")
    object_list = json.loads(clients.content.decode())

    mup = [obj for obj in object_list['MUP'] if obj != None]
    olaf = [obj for obj in object_list['OLAF'] if obj != None]
    fnb = [obj for obj in object_list['FNB'] if obj != None]

    def update_client_object(self, text):
        self.collected_info['Client'] = text
        dropdown = self.ids.object_dropdown
        if text == "MUP":
            dropdown.values = self.mup
        elif text == "Olaf Sitte":
            dropdown.values = self.olaf
        elif text == "FNB":
            dropdown.values = self.fnb

    def choose_open_type(self):
        self.pilot.disabled = True
        self.extender.disabled = True
        self.reamer.disabled = True

    def choose_drill_type(self):
        self.pilot.disabled = False
        self.extender.disabled = False
        self.reamer.disabled = False

    def caula_button_toggle(self, caula):
        if caula.state == 'normal':
            # Caula Off
            self.casing_enabled = False
            self.caula.text = ''
        else:
            # Caula On
            self.casing_enabled = True

    def collect_info(self):
        self.collected_info["Pilot Drill"] = self.pilot.text
        self.collected_info["Extender"] = self.extender.text
        self.collected_info["Reamer"] = self.reamer.text
        self.collected_info["Caula/Casing"] = self.caula.text
        self.collected_info["Additional Info"] = self.additional.text

    def select_option(self, tbtn):
        self.popup = ColorsPopup()
        self.popup.bind(liners=partial(self.update_collected_info, tbtn))
        if tbtn.state == 'normal':
            self.collected_info["Liners"][tbtn.text] = []
        else:
            self.popup.popupWindow.open()
        self.ids.info.text = re.sub(r"[,\]\['{}]", '', str(self.collected_info['Liners']))

    def update_collected_info(self, tbtn, instance, value):
        self.collected_info["Liners"][tbtn.text] = value
        self.ids.info.text = re.sub(r"[,\]\['{}]", '', str(self.collected_info['Liners']))


class DrillingInfoPage(Screen):
    rod = 1
    dist = 3
    protocol = list()  # {Rod:_,Distance:_,Proc:_,Depth:_}

    def add_holes(self, start, end):
        ProtocolInfoPage.collected_info['Start BG'] = start
        ProtocolInfoPage.collected_info['End BG'] = end

    def add_entry(self, proc, depth):
        self.protocol.append({"Rod": 0, "Distance": 0, "Proc": 0, "Depth": 0})
        self.protocol[self.rod - 1]["Proc"] = proc
        self.protocol[self.rod - 1]["Depth"] = depth
        self.protocol[self.rod - 1]["Rod"] = self.rod
        self.protocol[self.rod - 1]["Distance"] = self.dist
        clean_entry = re.sub(r"[,'{}]", '', str(self.protocol[self.rod - 1]))
        self.ids.drilling_data.data.append({'text': clean_entry})
        self.rod += 1
        self.dist += 3

    def collect_final_info(self, total):
        ProtocolInfoPage.collected_info["Total Distance"] = total
        ProtocolInfoPage.collected_info["Protocol"] = self.protocol
        self.protocol = []
        self.rod = 1
        self.dist = 3


class WindowManager(ScreenManager):
    pass


class LoginScreen(Screen):
    pass


class RecycleProtocols(RecycleView):
    def __init__(self, **kwargs):
        super(RecycleProtocols, self).__init__(**kwargs)
        self.data = []


class Recycle(RecycleView):
    def __init__(self, **kwargs):
        super(Recycle, self).__init__(**kwargs)
        self.data = []


class MyApp(MDApp):
    refresh_token_file = "refresh_token.txt"
    protocol_info = ProtocolInfoPage.collected_info
    drilling_info = DrillingInfoPage.protocol

    olaf_number = 1

    def build(self):
        self.my_firebase = MyFirebase()
        self.theme_cls.theme_style = "Dark"
        GUI = Builder.load_file('main.kv')
        return GUI

    def on_start(self):
        try:
            # Try to read persistent credentials in refresh token
            with open('refresh_token.txt', 'r') as f:
                refresh_token = f.read()

            # Use refresh token to get a new idToken
            id_token, local_id = self.my_firebase.exchange_refresh_token(refresh_token)

            # Getting the database info
            result = requests.get("https://protocol-app-hdd-default-rtdb.europe-west1.firebasedatabase.app/"
                                  + local_id + ".json?auth=" + id_token)
            data = json.loads(result.content.decode())
            name = self.root.ids['profile'].ids['name']
            drill = self.root.ids['profile'].ids['drill']
            loc = self.root.ids['profile'].ids['location']
            name.text = str(data['Name'])
            drill.text = str(data['Drill'])
            loc.text = str(data['Loc'])
            self.root.ids['main'].ids["past_protocols"].data = []
            self.root.transition = NoTransition()
            self.root.current = 'main'
            self.root.transition = SlideTransition()
        except Exception as e:
            print('!!!on_start!!!')
            print(e)

    def sign_out(self):
        with open(self.refresh_token_file, 'w') as f:
            f.write('')
            f.close()
            self.root.current = 'login_screen'

    def update_personal_info(self):
        self.popup = ProfilePopup()
        self.popup.popupWindow.open()

    def send_protocol_to_firebase(self):
        # Combine all the info in one place
        all_data = ProtocolInfoPage.collected_info
        protocol_info = str(all_data).replace("'", '"')
        json_data = '%s' % protocol_info

        # Opens refresh token for ids
        try:
            with open('refresh_token.txt', 'r') as f:
                refresh_token = f.read()

            id_token, local_id = self.my_firebase.exchange_refresh_token(refresh_token)
            # Sorting through clients and adding to a correct object
            if all_data['Client'] == 'MUP':
                try:
                    # Get the Bohrprotocol number for MUP
                    bp_json = requests.get(
                        "https://protocol-app-hdd-default-rtdb.europe-west1.firebasedatabase.app/" + local_id +
                        "/Protocols/" + str(all_data['Client']).lower() + f"/{all_data['Object']}" + ".json?auth=" + id_token)
                    bp_number_json = json.loads(bp_json.content.decode())
                    print(bp_number_json)
                    # Checks if its a new object and if so sets bp to 0
                    if bp_number_json == None:
                        bp_number = 0
                    else:
                        bp_number = len(bp_number_json.keys())
                except Exception as e:
                    print('!!!Bohrprotokoll number Exception MUP!!!')
                    print(e)
                # Sends the data to correct object with the correct numeration
                try:
                    requests.patch(
                        url="https://protocol-app-hdd-default-rtdb.europe-west1.firebasedatabase.app/" + local_id +
                            "/Protocols/mup/" + f"{all_data['Object']}/" + "BP" + str(bp_number + 1) + ".json?auth=" +
                            id_token, json=json.loads(json_data))

                    self.root.ids['main'].ids['past_protocols'].data.append({'text': f"{all_data['Client']} "
                                                                                     f"{all_data['Object']} BP"
                                                                                     f"{bp_number+1}"})
                except Exception as e:
                    print('!!!Exception on sending to MUP!!!')
                    print(e)

            elif all_data['Client'] == 'FNB':
                try:
                    # Get the Bohrprotocol number for FNB
                    bp_json = requests.get(
                        "https://protocol-app-hdd-default-rtdb.europe-west1.firebasedatabase.app/" + local_id +
                        "/Protocols/" + str(
                            all_data['Client']).lower() + f"/{all_data['Object']}" + ".json?auth=" + id_token)
                    bp_number_json = json.loads(bp_json.content.decode())
                    print(bp_number_json)
                    # Checks if its a new object and if so sets bp to 0
                    if bp_number_json == None:
                        bp_number = 0
                    else:
                        bp_number = len(bp_number_json.keys())
                except Exception as e:
                    print('!!!Bohrprotokoll Exception FNB!!!')
                    print(e)
                try:
                    # Sends the data to correct object with the correct numeration
                    requests.patch(
                        url="https://protocol-app-hdd-default-rtdb.europe-west1.firebasedatabase.app/" + local_id +
                            "/Protocols/fnb/" + f"{all_data['Object']}/" + "BP" + str(bp_number + 1) + ".json?auth=" +
                            id_token, json=json.loads(json_data))

                    self.root.ids['main'].ids['past_protocols'].data.append({'text': f"{all_data['Client']} "
                                                                                     f"{all_data['Object']} BP"
                                                                                     f"{bp_number+1}"})
                except Exception as e:
                    print("!!!Exception on sending to FNB!!!")
                    print(e)
            else:
                try:
                    # Gets amount of past protocols from the database
                    olaf_bp_json = requests.get("https://protocol-app-hdd-default-rtdb.europe-west1.firebasedatabase.app/"
                                        + local_id + "/PastOlaf" + ".json?auth=" + id_token)
                    olaf_bp = json.loads(olaf_bp_json.content.decode())
                    # Sets that value to a variable
                    olaf_number = olaf_bp["Previous BP"]
                    # Sends the data to correct object with the continues numeration
                    olaf_number += 1
                    requests.patch(
                        url="https://protocol-app-hdd-default-rtdb.europe-west1.firebasedatabase.app/" + local_id +
                            "/Protocols/olaf/" + f"{all_data['Object']}/" + "BP" + str(olaf_number) + ".json?auth=" +
                            id_token, json=json.loads(json_data))
                    olaf_number_back = '{"Previous BP": %s}' % olaf_number
                    requests.patch("https://protocol-app-hdd-default-rtdb.europe-west1.firebasedatabase.app/"
                                   + local_id + "/PastOlaf" + ".json?auth=" + id_token, json=json.loads(olaf_number_back))

                    self.root.ids['main'].ids['past_protocols'].data.append({'text': f"{all_data['Client']} "
                                                                                     f"{all_data['Object']} BP"
                                                                                     f"{olaf_number}"})
                except Exception as e:
                    print("!!!Exception on sending Olaf!!!")
                    print(e)

            # Updating RecycleView on the mainpage

        except Exception as e:
            print('!!!Exception on sending!!!')
            print(e)

    def clean_everything_and_return(self):
        # Cleaning text inputs, buttons and everything in ProtocolInfoPage
        for key, val in self.root.ids['protocolinfo'].ids.items():
            if 'spinner' in str(val):
                self.root.ids['protocolinfo'].ids[key].text = 'Choose Object'
            elif 'textinput' in str(val) or 'label' in str(val):
                self.root.ids['protocolinfo'].ids[key].text = ''
            else:
                self.root.ids['protocolinfo'].ids[key].state = 'normal'
        # Cleaning text inputs in DrillingInfo
        for key, val in self.root.ids['drillinginfo'].ids.items():
            self.root.ids['drillinginfo'].ids[key].text = ''
        # Cleaning RecycleView with entries
        self.root.ids['drillinginfo'].ids['drilling_data'].data = []

        self.root.current = 'main'

    def enable_signout(self, status):
        if status == True:
            self.root.ids['main'].ids['sign_out_btn'].disabled = False
        else:
            self.root.ids['main'].ids['sign_out_btn'].disabled = True

if __name__ == '__main__':
    MyApp().run()
