from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.app import App

import requests
import json


class ProfilePopup(Screen):

    def __init__(self, **kwargs):
        super(ProfilePopup, self).__init__(**kwargs)
        main_Layout = BoxLayout(orientation='vertical')
        btn_layout = GridLayout(cols=2, size_hint=(1,.7))
        name_layout = GridLayout(cols=2, padding=10)
        name = Label(text='Name')
        name_text = TextInput(multiline=False)
        name_layout.add_widget(name)
        name_layout.add_widget(name_text)
        drill_layout = GridLayout(cols=2, padding=10)
        drill_text = TextInput(multiline=False)
        drill = Label(text='Drill')
        drill_layout.add_widget(drill)
        drill_layout.add_widget(drill_text)
        loc_layout = GridLayout(cols=2, padding=10)
        loc = Label(text='LocationSys')
        loc_text = TextInput(multiline=False)
        loc_layout.add_widget(loc)
        loc_layout.add_widget(loc_text)
        self.popupWindow = Popup(title='Edit info', content = main_Layout, size_hint=(1, .5), auto_dismiss=False)
        save_btn = Button(text='Save changes')
        close_btn = Button(text='Close')
        close_btn.bind(on_press=self.popupWindow.dismiss)
        save_btn.bind(on_press=lambda x: self.save_changes(name_text.text, drill_text.text, loc_text.text))
        save_btn.bind(on_press=self.popupWindow.dismiss)
        btn_layout.add_widget(close_btn)
        btn_layout.add_widget(save_btn)
        main_Layout.add_widget(name_layout)
        main_Layout.add_widget(drill_layout)
        main_Layout.add_widget(loc_layout)
        main_Layout.add_widget(btn_layout)

    def save_changes(self, name, drill, loc):
        app = App.get_running_app()
        json_data = '{"Name": "%s", "Drill": "%s", "Loc": "%s" }' % (name, drill, loc)
        try:
            with open('refresh_token.txt', 'r') as f:
                refresh_token = f.read()

            id_token, local_id = app.my_firebase.exchange_refresh_token(refresh_token)

            requests.patch(url="https://protocol-app-hdd-default-rtdb.europe-west1.firebasedatabase.app/" + local_id + ".json?auth=" + id_token, json=json.loads(json_data))

        except Exception as e:
            print(e)

        name_label = app.root.ids['profile'].ids['name']
        drill_label = app.root.ids['profile'].ids['drill']
        loc_label = app.root.ids['profile'].ids['location']
        name_label.text = name
        drill_label.text = drill
        loc_label.text = loc
