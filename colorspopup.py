from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import  ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.togglebutton import ToggleButton


class ColorsPopup(Screen):
    liners = ListProperty([])
    colors = ['GB', 'BL', 'GR', 'RT', 'SW', 'BR', 'TR', 'OR', 'VI']

    def __init__(self, **kwargs):
        super(ColorsPopup, self).__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical')
        layout = GridLayout(cols=3, size_hint=(.7, .7), pos_hint={'center_x': .5})
        self.popupWindow = Popup(title='Flatliner Colors', content=main_layout, size_hint=(1, .5), auto_dismiss=False)
        close_btn = Button(text='Choose Colors', size_hint=(.7, .2), pos_hint={'center_x': .5})
        close_btn.bind(on_press=self.popupWindow.dismiss)
        for color in self.colors:
            color_btn = ToggleButton(text=color)
            color_btn.bind(state=self.adding_removing_colors)
            if color == 'GB':
                color_btn.background_color = (1, 1, 0, 1)
            elif color == 'BL':
                color_btn.background_color = (0, 0, 1, 1)
            elif color == 'GR':
                color_btn.background_color = (0, 1, 0, 1)
            elif color == 'RT':
                color_btn.background_color = (1, 0, 0, 1)
            elif color == 'SW':
                color_btn.background_color = (0, 0, 0, .5)
            elif color == 'BR':
                color_btn.background_color = (.5, .5, .3, 1)
            elif color == 'OR':
                color_btn.background_color = (.7, .7, 0, 1)
            elif color == 'VI':
                color_btn.background_color = (.7, 0, .5, 1)
            layout.add_widget(color_btn)
        main_layout.add_widget(layout)
        main_layout.add_widget(close_btn)

    def adding_removing_colors(self, color, state):
        if state == 'down':
            self.liners.append(color.text)
        elif state == 'normal':
            self.liners.remove(color.text)