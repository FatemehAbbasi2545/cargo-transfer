import string
import random
from tkinter import Frame, Label, Entry, Button, messagebox, END

from cargo_client.ui.frames.base_frame import BaseFrame
from cargo_client.ui.api_client import APIClient
from cargo_client.models import Response
from cargo_client.events import EventBus, Event

class LoginFrame(BaseFrame):
    def __init__(self, container: Frame, api_client: APIClient):
        super().__init__(container)

        self.api_client = api_client

        self.build_user_info_section()
        self.generate_captcha_code()
        self.build_captcha_section()
        self.build_user_action_section()

    def build_user_info_section(self):
        self.user_info_frame = Frame(self)
        self.user_info_frame.pack()

        self.user_name_label = Label(self.user_info_frame, text="User Name:", font=("Segoe UI", 11), bg="#F0F0F0")
        self.user_name_label.grid(row=0, column=0, padx=10, pady=10)

        self.user_name_entry = Entry(self.user_info_frame, font=('Segoe UI', 11), bg='#FFFFFF', relief='solid', borderwidth=1)
        self.user_name_entry.grid(row=0, column=1, padx=10, pady=10)

        self.password_label = Label(self.user_info_frame, text="Password:", font=("Segoe UI", 11), bg="#F0F0F0")
        self.password_label.grid(row=1, column=0, padx=10, pady=10)

        self.password_entry = Entry(self.user_info_frame, show="*", font=('Segoe UI', 11), bg='#FFFFFF', relief='solid', borderwidth=1)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

    def build_captcha_section(self):
        self.captcha_frame = Frame(self)
        self.captcha_frame.pack(padx=10, pady=10)

        self.refresh_captcha_btn = Button(self.captcha_frame, text="Refresh", command=self.refresh_captcha, font=('Segoe UI', 11), bg='#4682B4', fg='#FFFFFF', activebackground='#4169E1', activeforeground='#FFFFFF', relief='raised', borderwidth=0)
        self.refresh_captcha_btn.grid(row=0, column=0, padx=5)

        self.captcha_label = Label(self.captcha_frame, text=self.captcha_code, font=("Segoe UI", 11, "bold"), bg="#F0F0F0", fg="blue", relief="solid")
        self.captcha_label.grid(row=0, column=1, padx=5)

        self.captcha_entry = Entry(self.captcha_frame, font=('Segoe UI', 11), bg='#FFFFFF', relief='solid', borderwidth=1)
        self.captcha_entry.grid(row=0, column=2, padx=5)

    def build_user_action_section(self):
        self.user_action_frame = Frame(self)
        self.user_action_frame.pack(padx=10, pady=10)

        self.login_button = Button(self.user_action_frame, text="Login", command=self.login, font=('Segoe UI', 11), bg='#4682B4', fg='#FFFFFF', activebackground='#4169E1', activeforeground='#FFFFFF', relief='raised', borderwidth=0)
        self.login_button.pack(padx=10, pady=5)

        self.sign_up_label = Label(self.user_action_frame, text="Go to register", font=("Segoe UI", 11), bg="#F0F0F0", fg="blue", cursor="hand2")
        self.sign_up_label.pack(pady=5)
        self.sign_up_label.bind("<Button-1>", lambda e: self.go_to_register())

    def generate_captcha_code(self, length=5):
        chars = string.ascii_uppercase + string.digits # or chars = string.digits
        chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('L', '')
        self.captcha_code = ''.join(random.choices(chars, k=length))

    def refresh_captcha(self):
        self.generate_captcha_code()
        self.captcha_label.config(text=self.captcha_code)

    def login(self):
        user_name = self.user_name_entry.get()
        password = self.password_entry.get()
        user_captcha = self.captcha_entry.get()

        if not user_name or not password or not user_captcha:
            messagebox.showerror("Error", "All fields are required.")
            return False

        user_captcha = user_captcha.strip()
        if user_captcha.upper() != self.captcha_code.upper():
            messagebox.showerror("Error", "Incorrect security code.")
            return False

        response:Response = self.api_client.login(user_name, password)

        if not response.success:
            messagebox.showerror(title="Login Failed!", message=response.message)
            return

        EventBus.publish(Event.LOGIN_SUCCEEDED, response.data)
        self.clear_user_inputs()
        self.pack_forget()

    def go_to_register(self):
        self.clear_user_inputs()
        self.pack_forget()
        EventBus.publish(Event.GO_TO_REGISTER)
        
    def clear_user_inputs(self):
        self.user_name_entry.delete(0, END)
        self.password_entry.delete(0, END)
        self.captcha_entry.delete(0, END)