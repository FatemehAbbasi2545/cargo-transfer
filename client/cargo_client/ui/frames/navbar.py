from tkinter import Tk, Frame, Button, Label

from cargo_client.ui.frames.base_frame import BaseFrame
from cargo_client.events import EventBus, Event

class Navbar(BaseFrame):
    def __init__(self, container: Tk):
        super().__init__(container)

        self.current_user = None

        self.frame = Frame(self)
        self.frame.pack()

        self.current_user_label = Label(self.frame, text="", font=('Segoe UI', 11), bg='#F0F0F0', fg="#62BBF3")
        self.current_user_label.grid(row=0, column=0, sticky='w')

        self.logout_button = Button(self.frame, text="Logout", command=self.logout, font=('Segoe UI', 11), bg='#4682B4', fg='#FFFFFF', activebackground='#4169E1', activeforeground='#FFFFFF', relief='raised', borderwidth=0)
        self.logout_button.grid(row=0, column=1, sticky='e')

    def set_current_user(self, user):
        self.current_user = user
        self.current_user_label.config(text=f"User: {self.current_user.user_name}")

    def logout(self):
        EventBus.publish(Event.LOGOUT)
